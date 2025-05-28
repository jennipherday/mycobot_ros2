import os

from ament_index_python import get_package_share_directory
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

from launch import LaunchDescription
from launch.conditions import IfCondition
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration


def generate_launch_description():
    res = []

    port_launch_arg = DeclareLaunchArgument(name="port", default_value="/dev/ttyAMA0")
    res.append(port_launch_arg)

    baud_launch_arg = DeclareLaunchArgument(name="baud", default_value="1000000")
    res.append(baud_launch_arg)

    model_launch_arg = DeclareLaunchArgument(
        name="model",
        default_value=os.path.join(
            get_package_share_directory("mycobot_description"),
            "urdf/mycobot_280_pi/mycobot_280_pi.urdf",
        ),
    )
    res.append(model_launch_arg)

    rvizconfig_launch_arg = DeclareLaunchArgument(
        name="rvizconfig",
        default_value=os.path.join(
            get_package_share_directory("mycobot_280pi"), "config/mycobot_pi.rviz"
        ),
    )
    res.append(rvizconfig_launch_arg)

    gui_launch_arg = DeclareLaunchArgument(name="gui", default_value="true")
    res.append(gui_launch_arg)

    driver_launch_arg = DeclareLaunchArgument(name="driver", default_value="true")
    res.append(driver_launch_arg)

    rviz_bool_launch_arg = DeclareLaunchArgument("rviz", default_value="true")
    res.append(rviz_bool_launch_arg)

    robot_description = ParameterValue(
        Command(["xacro ", LaunchConfiguration("model")]), value_type=str
    )

    # robot_state_publisher
    robot_state_publisher_node = Node(
        name="robot_state_publisher",
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": robot_description}],
        condition=IfCondition(LaunchConfiguration("driver")),
    )
    res.append(robot_state_publisher_node)

    # rviz2
    rviz_node = Node(
        name="rviz2",
        package="rviz2",
        executable="rviz2",
        output="screen",
        arguments=["-d", LaunchConfiguration("rvizconfig")],
        condition=IfCondition(LaunchConfiguration("rviz")),
    )
    res.append(rviz_node)

    # subscriber_driver node
    driver_node = Node(
        name="mycobot_driver",
        package="mycobot_280pi",
        executable="subscriber_driver",
        parameters=[
            {"port": LaunchConfiguration("port")},
            {"baud": LaunchConfiguration("baud")},
            {"max_speed": 50},
        ],
        output="screen",
        condition=IfCondition(LaunchConfiguration("driver")),
    )
    res.append(driver_node)

    # GUI (conditionally launched if gui:=true)
    gui_node = Node(
        name="mycobot_gui",
        package="mycobot_280pi",
        executable="publishing_gui",
        output="screen",
        condition=IfCondition(LaunchConfiguration("gui")),
    )
    res.append(gui_node)

    return LaunchDescription(res)
