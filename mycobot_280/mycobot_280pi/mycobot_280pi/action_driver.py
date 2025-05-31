import math
import time

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, GoalResponse, CancelResponse
from rclpy.action.server import ServerGoalHandle
from rclpy.parameter import Parameter
from rcl_interfaces.msg import SetParametersResult
from std_msgs.msg import Header
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory


from control_msgs.action import FollowJointTrajectory
from pymycobot.mycobot import MyCobot


class MyCobotDriver(Node):
    def __init__(self):
        super().__init__("mycobot_driver")

        # Parameters
        self.declare_parameter("port", "/dev/ttyAMA0")
        self.declare_parameter("baud", 1000000)
        self.declare_parameter("max_speed", 50)

        port = self.get_parameter("port").get_parameter_value().string_value
        baud = self.get_parameter("baud").get_parameter_value().integer_value
        self._max_speed = self.get_parameter("max_speed").get_parameter_value().integer_value

        self.add_on_set_parameters_callback(self._on_param_change)

        self.get_logger().info(f"Connecting to MyCobot on port {port} at {baud} baud...")
        self.mc = MyCobot(port, baud)
        time.sleep(0.05)
        self.mc.set_fresh_mode(1)
        time.sleep(0.05)
        self.get_logger().info("MyCobot ready.")

        # ROS publishers
        self.joint_states_publisher = self.create_publisher(JointState, "joint_states", 10)
        self.create_timer(0.1, self.publish_joint_states)  # 10Hz

        # Action server
        self._action_server = ActionServer(
            self,
            FollowJointTrajectory,
            'mycobot_arm_controller/follow_joint_trajectory',
            execute_callback=self.execute_trajectory_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
        )

    def _on_param_change(self, params):
        for param in params:
            if param.name == "max_speed" and param.type_ == Parameter.Type.INTEGER:
                self._max_speed = param.value
                self.get_logger().info(f"Updated max_speed to {self._max_speed}")
        return SetParametersResult(successful=True)

    def goal_callback(self, goal_request, goal_handle=None):
        self.get_logger().info("Received FollowJointTrajectory goal")
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        self.get_logger().info("Cancel request received")
        return CancelResponse.ACCEPT

    def execute_trajectory_callback(self, goal_handle:ServerGoalHandle):
        traj: JointTrajectory = goal_handle.request.trajectory
        if not traj.points:
            self.get_logger().warn("Empty trajectory received.")
            goal_handle.abort()
            return FollowJointTrajectory.Result()

        for point in traj.points:
            joint_angles_deg = [math.degrees(r) for r in point.positions]
            self.mc.send_angles(joint_angles_deg, self._max_speed)
            self.get_logger().info(f"Sent joint angles to serial bus: {joint_angles_deg}")

            duration = point.time_from_start.sec + point.time_from_start.nanosec * 1e-9
            self.get_logger().info(f"Waiting for {duration} seconds to complete movement")
            time.sleep(duration)

        self.publish_joint_states() # Force publish final joint states
        time.sleep(0.2)  # Allow time for the last command to complete
        self.publish_joint_states()  # Final publish to ensure state is up-to-date


        goal_handle.succeed()
        return FollowJointTrajectory.Result()

    def publish_joint_states(self):
        try:
            res = self.mc.get_angles()
            if not res or all(r == 0.0 for r in res):
                return  # skip uninitialized

            radians_list = [math.radians(deg) for deg in res]
            msg = JointState()
            msg.header = Header()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.name = [
                "joint2_to_joint1",
                "joint3_to_joint2",
                "joint4_to_joint3",
                "joint5_to_joint4",
                "joint6_to_joint5",
                "joint6output_to_joint6",
            ]
            msg.position = radians_list
            msg.velocity = [0.0] * 6
            msg.effort = [0.0] * 6
            self.joint_states_publisher.publish(msg)
        except Exception as e:
            self.get_logger().warn(f"Failed to publish joint states: {e}")


def main(args=None):
    rclpy.init(args=args)
    node = MyCobotDriver()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()
