#!/usr/bin/python3

from turtle_bringup.dummy_module import dummy_function, dummy_var
import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist, Point
from turtlesim.msg import Pose
from turtlesim_plus_interfaces.srv import GivePosition
from std_srvs.srv import Empty
import numpy as np
import math as m

from nav_msgs.msg import Odometry
from tf2_ros import TransformBroadcaster
from tf_transformations import quaternion_from_euler
from geometry_msgs.msg import TransformStamped

class GotoPos(Node):
    def __init__(self):
        super().__init__('go_to_pos_node')
        self.odom_pub = self.create_publisher(Odometry, '/odom', 10)
        self.tf_broardcaster = TransformBroadcaster(self)
        self.cmd_vel_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.cmd_vel_pub = self.create_publisher(Twist, '/turtle2/cmd_vel', 10)
        self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)
        self.create_subscription(Pose, '/turtle2/pose', self.pose_callback, 10)
        self.create_subscription(Point, '/mouse_position', self.mouse_callback, 10)
        self.create_timer(0.01, self.timer_callback)
        self.spawn_pizza_client = self.create_client(GivePosition, '/spawn_pizza')
        self.eat_pizza_client = self.create_client(Empty, '/turtle1/eat')
        self.eat_pizza_client = self.create_client(Empty, '/turtle2/eat')

        self.robot_pose = None
        # self.mouse_pose = None
        self.waypoints = []

        self.get_logger().info('go_to_pos_node has been started')
    
    def pose_callback(self, msg):
        self.robot_pose = np.array([msg.x, msg.y, msg.theta])
        # print(f'Robot pose: {self.robot_pose}')

        odom_msg = Odometry()
        odom_msg.header.stamp = self.get_clock().now().to_msg()
        odom_msg.header.frame_id = 'odom'
        odom_msg.child_frame_id = 'base_link'

        odom_msg.pose.pose.position.x = self.robot_pose[0]
        odom_msg.pose.pose.position.y = self.robot_pose[1]
        odom_msg.pose.pose.position.z = 0.0

        q = quaternion_from_euler(0.0, 0.0, self.robot_pose[2])
        odom_msg.pose.pose.orientation.x = q[0]
        odom_msg.pose.pose.orientation.y = q[1]
        odom_msg.pose.pose.orientation.z = q[2]
        odom_msg.pose.pose.orientation.w = q[3]

        self.odom_pub.publish(odom_msg)

        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_link'

        t.transform.translation.x = self.robot_pose[0]
        t.transform.translation.y = self.robot_pose[1]
        t.transform.translation.z = 0.0
        t.transform.rotation.x = q[0]
        t.transform.rotation.y = q[1]
        t.transform.rotation.z = q[2]
        t.transform.rotation.w = q[3]

        self.tf_broardcaster.sendTransform(t)

    def spawn_pizza(self, x, y):
        req = GivePosition.Request()
        req.x = x
        req.y = y
        self.spawn_pizza_client.call_async(req)
    
    def eat_pizza(self):
        req = Empty.Request()
        self.eat_pizza_client.call_async(req)
    
    def timer_callback(self):
        if not self.waypoints:
            self.cmdvel(0.0, 0.0)
            return
        # self.cmdvel(0.1, 0.5)
        current_target = self.waypoints[0]

        delta_x = current_target[0] - self.robot_pose[0]
        delta_y = current_target[1] - self.robot_pose[1]
        distance = np.sqrt(delta_x**2 + delta_y**2)

        angle = np.arctan2(delta_y, delta_x)
        angle_diff = angle - self.robot_pose[2]
        correct_angle = m.atan2(m.sin(angle_diff), m.cos(angle_diff))

        K_linear = 0.7
        K_angular = 2.0

        vx = K_linear * distance
        wz = K_angular * correct_angle

        max_vx = 2.0
        max_wz = 2.0
        vx = max(-max_vx, min(vx, max_vx))
        wz = max(-max_wz, min(wz, max_wz))

        self.cmdvel(vx, wz)

        if distance < 0.5:
            self.eat_pizza()
            self.waypoints.pop(0)
            self.cmdvel(0.0, 0.0)

    def mouse_callback(self, msg):
        waypoint = np.array([msg.x, msg.y])
        self.waypoints.append(waypoint)
        self.spawn_pizza(waypoint[0], waypoint[1])
        # print(f'Mouse pose: {self.mouse_pose}')
        
    def cmdvel(self, v, w):
        msg = Twist()
        msg.linear.x = v
        msg.angular.z = w
        self.cmd_vel_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = GotoPos()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__=='__main__':
    main()
