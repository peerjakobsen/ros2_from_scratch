#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from rcl_interfaces.msg import SetParametersResult
from example_interfaces.msg import Int64
from my_robot_interfaces.msg import HardwareStatus


class NumberPublisherNode(Node):
    def __init__(self):
        super().__init__("number_publisher")

        # Declare parameters
        self.declare_parameter('initial_number', 2)
        self.declare_parameter('number_timer_period', 1.0)
        self.declare_parameter('hardware_timer_period', 2.0)

        # Get parameter values
        initial_number = self.get_parameter('initial_number').get_parameter_value().integer_value
        number_timer_period = self.get_parameter('number_timer_period').get_parameter_value().double_value
        hardware_timer_period = self.get_parameter('hardware_timer_period').get_parameter_value().double_value

        self.number = self.create_publisher(Int64, 'number', 10)
        self.hardware_status = self.create_publisher(HardwareStatus, 'hardware_status', 10)
        self._number = initial_number
        self.number_timer_ = self.create_timer(number_timer_period, self.publish_number)
        self.hardware_timer_ = self.create_timer(hardware_timer_period, self.publish_hardware_status)

        # Add parameter callback
        self.add_on_set_parameters_callback(self.parameter_callback)

        self.get_logger().info(f'Publisher "number" has been started with initial_number={initial_number}, timer_period={number_timer_period}s')
        self.get_logger().info(f'Publisher "hardware_status" has been started with timer_period={hardware_timer_period}s')

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

    def parameter_callback(self, params):
        result = SetParametersResult()
        result.successful = True

        for param in params:
            if param.name == 'initial_number':
                if param.type_ == Parameter.Type.INTEGER:
                    self._number = param.value
                    self.get_logger().info(f'Parameter "initial_number" updated to: {param.value}')
                else:
                    result.successful = False
                    result.reason = 'initial_number must be an integer'

            elif param.name == 'number_timer_period':
                if param.type_ == Parameter.Type.DOUBLE:
                    self.number_timer_.cancel()
                    self.number_timer_ = self.create_timer(param.value, self.publish_number)
                    self.get_logger().info(f'Parameter "number_timer_period" updated to: {param.value}s')
                else:
                    result.successful = False
                    result.reason = 'number_timer_period must be a double'

            elif param.name == 'hardware_timer_period':
                if param.type_ == Parameter.Type.DOUBLE:
                    self.hardware_timer_.cancel()
                    self.hardware_timer_ = self.create_timer(param.value, self.publish_hardware_status)
                    self.get_logger().info(f'Parameter "hardware_timer_period" updated to: {param.value}s')
                else:
                    result.successful = False
                    result.reason = 'hardware_timer_period must be a double'

        return result


def main(args=None):
    rclpy.init(args=args)
    node = NumberPublisherNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
