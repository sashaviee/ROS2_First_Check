import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    urdf_file = os.path.join(
        get_package_share_directory('exam_robot'),
        'urdf',
        'exam_robot.urdf'
    )

    with open(urdf_file, 'r') as infp:
        robot_description = infp.read()

    return LaunchDescription([

        Node(
            package='exam_robot',
            executable='battery_node',
            name='battery_node',
            output='screen'
        ),

        Node(
            package='exam_robot',
            executable='distance_sensor',
            name='distance_sensor',
            output='screen'
        ),

        Node(
            package='exam_robot',
            executable='status_display',
            name='status_display',
            output='screen'
        ),

        Node(
            package='exam_robot',
            executable='robot_controller',
            name='robot_controller',
            output='screen'
        ),

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_description}]
        ),
    ])