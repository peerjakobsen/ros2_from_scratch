from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    # Get the path to the parameter file
    config = os.path.join(
        get_package_share_directory('my_py_pkg'),
        'config',
        'number_params.yaml'
    )

    return LaunchDescription([
        Node(
            package='my_py_pkg',
            executable='number_publisher',
            name='num_pub1',
            namespace='abc',
            parameters=[config]
        ),
        Node(
            package='my_py_pkg',
            executable='number_publisher',
            name='num_pub2',
            namespace='abc',
            parameters=[
                {'initial_number': 5},
                {'number_timer_period': 0.5},
                {'hardware_timer_period': 1.0}
            ]
        ),
        Node(
            package='my_py_pkg',
            executable='number_counter',
            name='number_counter',
            namespace='abc'
        )
    ])
