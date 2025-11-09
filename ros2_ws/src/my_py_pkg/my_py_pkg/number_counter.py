#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from example_interfaces.msg import Int64
from my_robot_interfaces.srv import ResetCounter


class NumberCounterNode(Node):
    def __init__(self):
        super().__init__("number_counter")
        self.counter_ = 0
        self.number_subscriber = self.create_subscription(Int64, 'number', self.callback_number, 10)
        self.reset_counter_service = self.create_service(ResetCounter, 'reset_counter', self.callback_reset_counter)
        self.get_logger().info('Subscribed to "number"')
        self.get_logger().info('Reset counter service created')

    def callback_number(self, msg):
        self.counter_ += msg.data
        self.get_logger().info(f'Counter: {self.counter_}')

    def callback_reset_counter(self, request, response):
        if request.reset_value < 0:
            response.success = False
            response.message = "Reset value cannot be negative"
            self.get_logger().warn(f'Reset failed: negative value {request.reset_value}')
        elif request.reset_value >= self.counter_:
            response.success = False
            response.message = f"Reset value must be greater than current counter ({self.counter_})"
            self.get_logger().warn(f'Reset failed: {request.reset_value} not greater than {self.counter_}')
        else:
            self.counter_ = request.reset_value
            response.success = True
            response.message = "Success"
            self.get_logger().info(f'Counter reset to {request.reset_value}')
        return response


def main(args=None):
    rclpy.init(args=args)
    node = NumberCounterNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
