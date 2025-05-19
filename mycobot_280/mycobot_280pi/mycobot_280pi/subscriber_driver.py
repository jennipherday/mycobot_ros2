# Simple subscriber driver for the MyCobot 280 that is MoveIt compatible.
import math
from trajectory_msgs.msg import JointTrajectory
from sensor_msgs.msg import JointState
from std_msgs.msg import Header
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from rcl_interfaces.msg import SetParametersResult
from pymycobot.mycobot import MyCobot
import time


class MyCobotDriver(Node):
    def __init__(self):
        super().__init__("mycobot_driver")

        self.declare_parameter("port", "/dev/ttyAMA0")
        self.declare_parameter("baud", 1000000)
        self.declare_parameter("max_speed", 50)

        port = self.get_parameter("port").get_parameter_value().string_value
        baud = self.get_parameter("baud").get_parameter_value().integer_value
        self._max_speed = (
            self.get_parameter("max_speed").get_parameter_value().integer_value
        )

        self.get_logger().info("port:%s, baud:%d" % (port, baud))
        self.add_on_set_parameters_callback(self._on_param_change)

        self.mc = MyCobot(port, baud)
        time.sleep(0.05)
        self.mc.set_fresh_mode(1)
        time.sleep(0.05)

        # ROS interfaces
        self.joint_subscription = self.create_subscription(
            msg_type=JointTrajectory,
            topic="joint_trajectory",
            callback=self.joint_callback,
            qos_profile=10,
        )
        self.gripper_subscription = self.create_subscription(
            JointTrajectory, "gripper_trajectory", self.gripper_callback, qos_profile=10
        )
        self.joint_states_publisher = self.create_publisher(
            msg_type=JointState, topic="joint_states", qos_profile=10
        )
        self.create_timer(0.1, self.publish_joint_states)

    def joint_callback(self, msg: JointTrajectory):
        self.get_logger().info(f"Max speed: {self._max_speed}")
        if msg.points:
            joint_angles = [math.degrees(rad) for rad in msg.points[0].positions]
            self.mc.send_angles(joint_angles, self._max_speed)
            self.get_logger().info(f"Joint angles sent to serial: {joint_angles}")

    def _on_param_change(self, params):
        for param in params:
            if param.name == "max_speed" and param.type_ == Parameter.Type.INTEGER:
                self._max_speed = param.value
                self.get_logger().info(f"Updated max_speed to {self._max_speed}")
        return SetParametersResult(successful=True)

    def gripper_callback(self, msg: JointTrajectory):
        if msg.points:
            gripper_position = msg.points[0].positions[0]
            self.mc.set_gripper_value(gripper_position, self._max_speed)
            self.get_logger().info(f"Gripper position sent: {gripper_position}")

    def publish_joint_states(self):
        try:
            res = self.mc.get_angles()
            if not res or all(r == 0.0 for r in res):
                return  # skip invalid read

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
            self.get_logger().warn(f"Failed to get joint states: {e}")


def main(args=None):
    rclpy.init(args=args)
    driver = MyCobotDriver()
    rclpy.spin(driver)
    driver.destroy_node()
    rclpy.shutdown()
