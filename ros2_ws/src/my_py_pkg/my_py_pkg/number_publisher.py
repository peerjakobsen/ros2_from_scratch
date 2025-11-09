#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from example_interfaces.msg import Int64
from my_robot_interfaces.msg import HardwareStatus


class NumberPublisherNode(Node):
    def __init__(self):
        super().__init__("number_publisher")
        self.number = self.create_publisher(Int64, 'number', 10)
        self.hardware_status = self.create_publisher(HardwareStatus, 'hardware_status', 10)
        self._number = 2
        self.number_timer_ = self.create_timer(1.0, self.publish_number)
        self.hardware_timer_ = self.create_timer(2.0, self.publish_hardware_status)
        self.get_logger().info('Publisher "number" has been started')
        self.get_logger().info('Publisher "hardware_status" has been started')

    def publish_number(self):
        msg = Int64()
        msg.data = self._number
        self.number.publish(msg)
        self._number += 1

    def publish_hardware_status(self):
        msg = HardwareStatus()
        msg.version = int(self._number / 2)
        msg.temperature = 45.5 + (self._number % 10) * 0.5
        msg.are_motors_ready = True
        msg.debug_message = f"System running smoothly. Number: {self._number}"
        self.hardware_status.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = NumberPublisherNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
