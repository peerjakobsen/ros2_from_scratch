#!/usr/bin/env python3
"""ROS 2 node for controlling a turtle robot."""

from __future__ import annotations

import random
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose


class TurtleControllerNode(Node):
  def __init__(self) -> None:
    super().__init__('turtle_controller')

    # Create publisher for velocity commands
    self.cmd_vel_publisher_ = self.create_publisher(
        Twist,
        'turtle1/cmd_vel',
        10
    )

    # Create subscriber for pose
    self.pose_subscriber_ = self.create_subscription(
        Pose,
        'turtle1/pose',
        self.pose_callback,
        10
    )

    # Boundary limits (turtlesim window is 11x11)
    self.min_x_ = 0.5
    self.max_x_ = 10.5
    self.min_y_ = 0.5
    self.max_y_ = 10.5
    self.boundary_margin_ = 1.0

    # Zig-zag state
    self.direction_change_counter_ = 0
    self.current_linear_vel_ = 1.0
    self.current_angular_vel_ = 0.0

    self.get_logger().info('TurtleControllerNode initialized')

  def pose_callback(self, msg: Pose) -> None:
    """Callback for pose updates - publish random zig-zag commands."""
    # Check if near boundaries and reverse if needed
    if (msg.x < self.min_x_ + self.boundary_margin_ or
        msg.x > self.max_x_ - self.boundary_margin_ or
        msg.y < self.min_y_ + self.boundary_margin_ or
        msg.y > self.max_y_ - self.boundary_margin_):
      # Reverse direction and pick random turn
      self.current_linear_vel_ *= -1.0
      self.current_angular_vel_ = random.uniform(-1.0, 1.0)
      self.direction_change_counter_ = 0

    # Change direction randomly every 20 callbacks
    self.direction_change_counter_ += 1
    if self.direction_change_counter_ >= 20:
      self.current_angular_vel_ = random.uniform(-1.0, 1.0)
      self.direction_change_counter_ = 0

    # Create and publish velocity command
    cmd_vel = Twist()
    cmd_vel.linear.x = self.current_linear_vel_
    cmd_vel.angular.z = self.current_angular_vel_

    self.cmd_vel_publisher_.publish(cmd_vel)

    self.get_logger().debug(
        f'Pose: x={msg.x:.2f}, y={msg.y:.2f}, theta={msg.theta:.2f} | '
        f'Vel: linear={cmd_vel.linear.x:.2f}, angular={cmd_vel.angular.z:.2f}'
    )

def main(args=None) -> None:
  rclpy.init(args=args)
  node = TurtleControllerNode()
  try:
    rclpy.spin(node)
  finally:
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
  main()
