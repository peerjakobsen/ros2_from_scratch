import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, RegisterEventHandler
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch.event_handlers import OnProcessStart
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg_share = get_package_share_directory('my_robot_bringup')
    urdf_file = os.path.join(pkg_share, 'urdf', 'my_robot.urdf')

    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_desc,
            'publish_frequency': 30.0
        }]
    )

    joint_state_publisher_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        output='screen'
    )

    rviz_config_file = PathJoinSubstitution(
        [FindPackageShare('urdf_tutorial'), 'rviz', 'urdf.rviz']
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file]
    )

    joint_state_publisher_event = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=robot_state_publisher_node,
            on_start=[joint_state_publisher_node]
        )
    )

    rviz_event = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=joint_state_publisher_node,
            on_start=[rviz_node]
        )
    )

    return LaunchDescription([
        robot_state_publisher_node,
        joint_state_publisher_event,
        rviz_event
    ])
