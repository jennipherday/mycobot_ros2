import tkinter as tk
import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint


class MyCobotGui(Node):
    def __init__(self, tk_root):
        super().__init__("mycobot_gui")
        self.win = tk_root

        # GUI layout + state setup
        self.setup_gui()

        # ROS 2 interfaces
        self.joint_pub = self.create_publisher(JointTrajectory, "/joint_trajectory", 10)
        self.joint_sub = self.create_subscription(
            JointState, "/joint_states", self.joint_state_cb, 10
        )

        self.gripper_pub = self.create_publisher(
            JointTrajectory, "/gripper_trajectory", 10
        )

    def setup_gui(self):
        self.frm = tk.Frame(self.win)
        self.frm.pack()
        self.entries = []
        self.joint_vars = []

        for i in range(6):
            tk.Label(self.frm, text=f"Joint {i + 1}").grid(row=i, column=0)
            var = tk.StringVar()
            ent = tk.Entry(self.frm, textvariable=var)
            ent.grid(row=i, column=1)
            var.set("0.0")  # Default value
            self.joint_vars.append(var)
            self.entries.append(ent)

        self.status_labels = [tk.Label(self.frm, text="---") for _ in range(6)]
        for i, label in enumerate(self.status_labels):
            label.grid(row=i, column=2)

        tk.Button(self.frm, text="Set Joints", command=self.send_joint_command).grid(
            row=6, column=0, columnspan=3
        )

        # Gripper controls

        tk.Label(self.frm, text="Gripper Value").grid(row=8, column=0)
        self.gripper_var = tk.StringVar()
        tk.Entry(self.frm, textvariable=self.gripper_var).grid(row=8, column=1)
        tk.Button(self.frm, text="Open Gripper", command=self.send_gripper_open).grid(
            row=9, column=0
        )
        tk.Button(self.frm, text="Close Gripper", command=self.send_gripper_close).grid(
            row=9, column=1
        )
        tk.Button(self.frm, text="Set Gripper", command=self.set_gripper_value).grid(
            row=8, column=2
        )

    def joint_state_cb(self, msg):
        for i, pos in enumerate(msg.position[:6]):
            self.status_labels[i]["text"] = f"{round(pos * 180 / 3.1415, 1)}°"

    def send_joint_command(self):
        try:
            values = [float(var.get()) for var in self.joint_vars]
            msg = JointTrajectory()
            msg.joint_names = [
                "joint2_to_joint1",
                "joint3_to_joint2",
                "joint4_to_joint3",
                "joint5_to_joint4",
                "joint6_to_joint5",
                "joint6output_to_joint6",
            ]
            point = JointTrajectoryPoint()
            point.positions = [math.radians(v) for v in values]  # degrees → radians
            point.time_from_start.sec = 1
            msg.points = [point]
            self.joint_pub.publish(msg)
        except ValueError:
            self.get_logger().warn("Invalid input: joint values must be numbers")

    def send_gripper_open(self):
        # Send a gripper trajectory message with a position (e.g., 0 for open)
        msg = JointTrajectory()
        msg.joint_names = ["gripper_joint"]
        point = JointTrajectoryPoint()
        point.positions = [100.0]
        point.time_from_start.sec = 1
        msg.points = [point]
        self.gripper_pub.publish(msg)

    def send_gripper_close(self):
        # Send a gripper trajectory message with a position (e.g., 100 for close)
        msg = JointTrajectory()
        msg.joint_names = ["gripper_joint"]
        point = JointTrajectoryPoint()
        point.positions = [0.0]
        point.time_from_start.sec = 1
        msg.points = [point]
        self.gripper_pub.publish(msg)

    def set_gripper_value(self):
        # Set any value based on user input
        try:
            val = float(self.gripper_var.get())
            msg = JointTrajectory()
            msg.joint_names = ["gripper_joint"]
            point = JointTrajectoryPoint()
            point.positions = [val]
            point.time_from_start.sec = 1
            msg.points = [point]
            self.gripper_pub.publish(msg)
        except ValueError:
            self.get_logger().warn("Invalid gripper input: must be a number")


def main():
    rclpy.init()
    root = tk.Tk()
    root.title("MyCobot ROS GUI")
    gui_node = MyCobotGui(root)

    def loop():
        rclpy.spin_once(gui_node, timeout_sec=0.01)
        root.after(10, loop)

    loop()
    root.mainloop()
    gui_node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
