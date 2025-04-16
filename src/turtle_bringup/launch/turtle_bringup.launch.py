#!/usr/bin/env python3
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
import os
from launch.actions import ExecuteProcess

def generate_launch_description():
    pkg_dir = get_package_share_directory('turtle_bringup')
    rviz_config_path = os.path.join(pkg_dir, 'rviz', 'fun2.rviz')

    micro_ros_agent = ExecuteProcess(
        cmd=['ros2', 'run', 'micro_ros_agent', 'micro_ros_agent', 'serial', '--dev', '/dev/ttyACM0', '-b', '2000000'],
        output='screen'
    )
    
    turtlesim_plus_node = Node(
        package='turtlesim_plus',
        executable='turtlesim_plus_node.py',
        name='turtlesim_plus_node',
        output='screen'
    )

    turtle_spawner_node = Node(
        package='turtle_bringup',
        executable='turtle_spawner.py',
        name='turtle_spawner',
        output='screen'
    )

    crazy_pizza_node = Node(
        package='turtle_bringup',
        executable='crazy_pizza.py',
        name='crazy_pizza',
        output='screen'
    )
    
    controller_node = Node(
        package='turtle_bringup',
        executable='controller.py',
        name='controller',
        namespace='turtle1',
        output='screen'
    )
    
    crazy_turtle_node = Node(
        package='turtle_bringup',
        executable='controller.py',
        name='crazy_turtle',
        namespace='turtle2',
        output='screen'
    )
    
    odom_publisher_node = Node(
        package='turtle_bringup',
        executable='odom_publisher.py',
        name='odom_publisher',
        output='screen'
    )
    
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_path],
        output='screen'
    )
    
    ld = LaunchDescription()
    
    # ld.add_action(micro_ros_agent)
    ld.add_action(turtlesim_plus_node)
    ld.add_action(odom_publisher_node)
    ld.add_action(rviz_node)
    ld.add_action(crazy_turtle_node)
    ld.add_action(crazy_pizza_node)
    ld.add_action(controller_node)
    # ld.add_action(turtle_spawner_node)

    return ld