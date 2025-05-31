import os
import yaml

from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def load_yaml(package_name, file_path):
    abs_path = os.path.join(get_package_share_directory(package_name), file_path)
    with open(abs_path, "r") as f:
        return yaml.safe_load(f)


def generate_launch_description():
    pkg_name = "mycobot_moveit_config"
    pkg_share = get_package_share_directory(pkg_name)

    # Load YAML files as dictionaries
    kinematics_yaml = load_yaml(pkg_name, "config/kinematics.yaml")
    ompl_yaml = load_yaml(pkg_name, "config/ompl_planning.yaml")
    joint_limits_yaml = load_yaml(pkg_name, "config/joint_limits.yaml")
    controllers_yaml = load_yaml(pkg_name, "config/moveit_controllers.yaml")

    # Load URDF
    urdf_path = os.path.join(
        get_package_share_directory("mycobot_description"),
        "urdf",
        "mycobot_280_pi",
        "mycobot_280_pi.urdf",
    )
    with open(urdf_path, "r") as urdf_file:
        robot_description = {"robot_description": urdf_file.read()}

    # Load SRDF
    srdf_path = os.path.join(pkg_share, "config", "mycobot_280_pi.srdf")
    with open(srdf_path, "r") as srdf_file:
        robot_description_semantic = {"robot_description_semantic": srdf_file.read()}

    rviz_config_file = PathJoinSubstitution(
        [FindPackageShare(pkg_name), "config", "mycobot_moveit.rviz"]
    )
    print("Loaded kinematics.yaml:", kinematics_yaml)


    # Launch robot state publisher
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[robot_description],
    )

    # Launch move_group
    move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[
            robot_description,
            robot_description_semantic,
            kinematics_yaml,
            controllers_yaml,
            ompl_yaml,
            joint_limits_yaml,
            {"publish_planning_scene": True},
        ],
    )

    # Launch static transform
    static_tf_node = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="static_transform_publisher",
        arguments=["0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "world_frame", "g_base"],
    )

    # RViz node
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", rviz_config_file],
        parameters=[robot_description, robot_description_semantic, kinematics_yaml],
    )

    return LaunchDescription([robot_state_publisher_node, static_tf_node, move_group_node, rviz_node])
