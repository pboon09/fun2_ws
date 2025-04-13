#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from nav_msgs.msg import Odometry
from tf2_ros import TransformBroadcaster
from tf_transformations import quaternion_from_euler
from geometry_msgs.msg import TransformStamped
import numpy as np

class OdomPublisher(Node):
    def __init__(self):
        super().__init__('odom_publisher_node')
        
        self.tf_broadcaster = TransformBroadcaster(self)

        self.odom1_pub = self.create_publisher(Odometry, '/odom1', 10)
        self.odom2_pub = self.create_publisher(Odometry, '/odom2', 10)
        
        self.create_subscription(Pose, '/turtle1/pose', 
                                lambda msg: self.pose_callback(msg, 'turtle1', 'turtle1'), 10)
        self.create_subscription(Pose, '/turtle2/pose', 
                                lambda msg: self.pose_callback(msg, 'turtle2', 'turtle2'), 10)
        
        self.get_logger().info('odom_publisher_node has been started')
    
    def pose_callback(self, msg, turtle_name, child_frame_id):
        self.pub_odom(msg, turtle_name, child_frame_id)
    
    def pub_odom(self, msg, turtle_name, child_frame_id):
        # Turtlesim has (0,0) at bottom-left with a 11x11 grid
        x = msg.x - 5.44  # Center the x coordinate
        y = msg.y - 5.44  # Center the y coordinate
        theta = msg.theta
        
        odom_msg = Odometry()
        odom_msg.header.stamp = self.get_clock().now().to_msg()
        odom_msg.header.frame_id = 'odom'
        odom_msg.child_frame_id = child_frame_id
        
        odom_msg.pose.pose.position.x = x
        odom_msg.pose.pose.position.y = y
        odom_msg.pose.pose.position.z = 0.0
        
        q = quaternion_from_euler(0.0, 0.0, theta)
        odom_msg.pose.pose.orientation.x = q[0]
        odom_msg.pose.pose.orientation.y = q[1]
        odom_msg.pose.pose.orientation.z = q[2]
        odom_msg.pose.pose.orientation.w = q[3]
        
        if turtle_name == 'turtle1':
            self.odom1_pub.publish(odom_msg)
        elif turtle_name == 'turtle2':
            self.odom2_pub.publish(odom_msg)
        
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'odom'
        t.child_frame_id = child_frame_id
        
        t.transform.translation.x = x
        t.transform.translation.y = y
        t.transform.translation.z = 0.0
        
        t.transform.rotation.x = q[0]
        t.transform.rotation.y = q[1]
        t.transform.rotation.z = q[2]
        t.transform.rotation.w = q[3]
        
        self.tf_broadcaster.sendTransform(t)


def main(args=None):
    rclpy.init(args=args)
    node = OdomPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__=='__main__':
    main()