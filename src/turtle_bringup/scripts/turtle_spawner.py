#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from turtlesim.srv import Spawn
import time

class TurtleSpawner(Node):
    def __init__(self):
        super().__init__('turtle_spawner_node')
        self.spawn_client = self.create_client(Spawn, '/spawn_turtle')

        self.timer = self.create_timer(0.01, self.check_and_spawn_turtles)

        self.get_logger().info('turtle_spawner_node has been started')

        while not self.spawn_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for spawn_turtle service...')


    def spawn_turtle(self, name, x, y, theta):
        self.get_logger().info(f'Attempting to spawn turtle: {name}')
        request = Spawn.Request()
        request.name = name
        request.x = x
        request.y = y
        request.theta = theta
        
        self.spawn_client.call_async(request)
        
    def check_topic_exists(self, topic_name):
        topic_names_and_types = self.get_topic_names_and_types()
        return any(topic_name == name for name, _ in topic_names_and_types)
    
    def check_and_spawn_turtles(self):
        turtle1_exists = self.check_topic_exists('/turtle1/scan')
        turtle2_exists = self.check_topic_exists('/turtle2/scan')
        
        # self.get_logger().info(f'Checking turtles: turtle1 {"exists" if turtle1_exists else "missing"}, turtle2 {"exists" if turtle2_exists else "missing"}')
        
        if not turtle1_exists:
            self.get_logger().info('Turtle1 not detected, spawning...')
            self.spawn_turtle('turtle1', 5.5, 5.5, 0.0)
        
        if not turtle2_exists:
            self.get_logger().info('Turtle2 not detected, spawning...')
            self.spawn_turtle('turtle2', 5.5, 5.5, 0.0)

def main(args=None):
    rclpy.init(args=args)
    node = TurtleSpawner()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()