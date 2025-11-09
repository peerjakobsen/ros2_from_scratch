#!/usr/bin/env python3
"""Minimal example ROS 2 Python node used for testing the workspace setup."""

from __future__ import annotations

import rclpy
from rclpy.node import Node


class MyCustomNode(Node):
    def __init__(self) -> None:
        super().__init__("my_node_name")
        self.counter_ = 0
        self.timer_ = self.create_timer(1.0, self.print_hello)

    def print_hello(self):
        self.get_logger().info(f"Hello {self.counter_}")
        self.counter_ +=1


def main(args=None) -> None:
    rclpy.init(args=args)
    node = MyCustomNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
