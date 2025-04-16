#!/usr/bin/python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtlesim.srv import Spawn
from turtlesim_plus_interfaces.srv import GivePosition
from std_srvs.srv import Empty
import numpy as np
import math as m

class CrazyTurtle(Node):
    def __init__(self):
        super().__init__('crazy_turtle_node')
        self.cmd_vel_pub = self.create_publisher(Twist, '/turtle2/cmd_vel', 10)
        self.create_subscription(Pose, '/turtle2/pose', self.pose_callback, 10)
        self.create_subscription(Pose, '/crazy_pizza', self.crazy_pizza_callback, 10)
        self.spawn_pizza_client = self.create_client(GivePosition, '/spawn_pizza')
        self.spawn_turtle_client = self.create_client(Spawn, '/spawn_turtle')
        self.eat_pizza_client = self.create_client(Empty, '/turtle2/eat')

        self.create_timer(0.01, self.timer_callback)

        self.robot_pose = None
        self.waypoints = []
        self.is_turtle_spawned = False

        self.get_logger().info('crazy_turtle_node has been started')
        
        self.get_logger().info('Waiting for spawn_turtle service...')
        self.spawn_turtle_client.wait_for_service()
        self.get_logger().info('Spawn turtle service is available, spawning turtle2...')
        self.spawn_turtle2()
    
    def spawn_turtle2(self):
        req = Spawn.Request()
        req.x = 5.44
        req.y = 5.44
        req.theta = 0.0
        req.name = 'turtle2'
        self.get_logger().info('Spawning turtle2')
        
        future = self.spawn_turtle_client.call_async(req)
        future.add_done_callback(self.turtle_spawned_callback)
    
    def turtle_spawned_callback(self, future):
        try:
            response = future.result()
            self.get_logger().info(f'Turtle spawned with name: {response.name}')
            self.is_turtle_spawned = True
        except Exception as e:
            self.get_logger().error(f'Service call failed: {e}')
    
    def pose_callback(self, msg):
        self.robot_pose = np.array([msg.x, msg.y, msg.theta])
    
    def spawn_pizza(self, x, y):
        req = GivePosition.Request()
        req.x = x
        req.y = y
        self.spawn_pizza_client.call_async(req)
    
    def eat_pizza(self):
        req = Empty.Request()
        self.eat_pizza_client.call_async(req)
    
    def crazy_pizza_callback(self, msg):
        waypoint = np.array([msg.x, msg.y])
        self.waypoints.append(waypoint)
        self.spawn_pizza(msg.x, msg.y)
    
    def timer_callback(self):
        if not self.is_turtle_spawned or self.robot_pose is None or not self.waypoints:
            self.cmdvel(0.0, 0.0)
            return
        
        current_target = self.waypoints[0]
        
        delta_x = current_target[0] - self.robot_pose[0]
        delta_y = current_target[1] - self.robot_pose[1]
        distance = np.sqrt(delta_x**2 + delta_y**2)

        angle = np.arctan2(delta_y, delta_x)
        angle_diff = angle - self.robot_pose[2]
        correct_angle = m.atan2(m.sin(angle_diff), m.cos(angle_diff))

        K_linear = 5.0
        K_angular = 15.0

        vx = K_linear * distance
        wz = K_angular * correct_angle

        max_vx = 10.0
        max_wz = 20.0
        vx = max(-max_vx, min(vx, max_vx))
        wz = max(-max_wz, min(wz, max_wz))

        self.cmdvel(vx, wz)

        if distance < 0.7:
            self.eat_pizza()
            self.waypoints.pop(0)
            self.cmdvel(0.0, 0.0)
    
    def cmdvel(self, v, w):
        msg = Twist()
        msg.linear.x = v
        msg.angular.z = w
        self.cmd_vel_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = CrazyTurtle()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__=='__main__':
    main()