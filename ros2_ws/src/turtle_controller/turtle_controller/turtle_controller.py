#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from rcl_interfaces.msg import SetParametersResult
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtlesim.srv import SetPen
from my_robot_interfaces.srv import SetSpinning


class TurtleControllerNode(Node):
    def __init__(self):
        super().__init__("turtle_controller")

        # Declare parameters
        self.declare_parameter('color_1', [255, 0, 0])  # Red for left side
        self.declare_parameter('color_2', [0, 0, 255])  # Blue for right side
        self.declare_parameter('velocity_left', 1.0)
        self.declare_parameter('velocity_right', 2.0)
        self.declare_parameter('angular_velocity_left', 1.0)
        self.declare_parameter('angular_velocity_right', 2.0)

        # Get parameter values
        self.color_1_ = self.get_parameter('color_1').get_parameter_value().integer_array_value
        self.color_2_ = self.get_parameter('color_2').get_parameter_value().integer_array_value
        self.velocity_left_ = self.get_parameter('velocity_left').get_parameter_value().double_value
        self.velocity_right_ = self.get_parameter('velocity_right').get_parameter_value().double_value
        self.angular_velocity_left_ = self.get_parameter('angular_velocity_left').get_parameter_value().double_value
        self.angular_velocity_right_ = self.get_parameter('angular_velocity_right').get_parameter_value().double_value

        self.cmd_vel_pub_ = self.create_publisher(Twist, "/turtle1/cmd_vel", 10)
        self.pose_sub_ = self.create_subscription(Pose, "/turtle1/pose",
                                                   self.callback_pose, 10)
        self.set_pen_client_ = self.create_client(SetPen, "/turtle1/set_pen")
        self.set_spinning_server_ = self.create_service(SetSpinning, "~/set_spinning",
                                                         self.callback_set_spinning)

        # Add parameter callback
        self.add_on_set_parameters_callback(self.parameter_callback)

        # Rotation tracking
        self.rotation_count_ = 0.0
        self.last_theta_ = 0.0
        self.last_set_pen_rotation_ = 0.0

        # Spinning state
        self.spinning_enabled_ = True

        # Track which side the turtle is on
        self.current_side_ = None  # 'left' or 'right'

        self.get_logger().info(f'Turtle controller started with color_1={list(self.color_1_)}, color_2={list(self.color_2_)}')
        self.get_logger().info(f'Velocities: left={self.velocity_left_}, right={self.velocity_right_}')

    def callback_set_spinning(self, request, response):
        self.spinning_enabled_ = request.spinning
        response.success = True
        status = "enabled" if request.spinning else "disabled"
        response.message = f"Spinning {status}"
        self.get_logger().info(f"Spinning {status}")
        return response

    def call_set_pen_service(self, side):
        while not self.set_pen_client_.wait_for_service(1.0):
            self.get_logger().warn("Waiting for /turtle1/set_pen service...")

        request = SetPen.Request()
        if side == 'left':
            request.r = int(self.color_1_[0])
            request.g = int(self.color_1_[1])
            request.b = int(self.color_1_[2])
        else:  # right
            request.r = int(self.color_2_[0])
            request.g = int(self.color_2_[1])
            request.b = int(self.color_2_[2])
        request.width = 20

        self.get_logger().info(f"Setting pen to RGB({request.r}, {request.g}, {request.b}) for {side} side")
        future = self.set_pen_client_.call_async(request)
        future.add_done_callback(self.callback_set_pen_response)

    def callback_set_pen_response(self, future):
        self.get_logger().info("Set pen service called")

    def callback_pose(self, pose: Pose):
        # Track rotation count
        theta_change = pose.theta - self.last_theta_

        # Handle wrapping at 2π/-π boundary
        if theta_change > 3.14:  # Wrapped around (large positive jump backwards)
            theta_change -= 6.28
        elif theta_change < -3.14:  # Wrapped around (large negative jump forwards)
            theta_change += 6.28

        self.rotation_count_ += abs(theta_change) / (2 * math.pi)
        self.last_theta_ = pose.theta

        # Determine which side the turtle is on and change color if it switched sides
        new_side = 'left' if pose.x < 5.5 else 'right'
        if new_side != self.current_side_:
            self.current_side_ = new_side
            self.call_set_pen_service(new_side)

        # Only publish velocity commands if spinning is enabled
        if self.spinning_enabled_:
            cmd = Twist()
            if pose.x < 5.5:
                cmd.linear.x = self.velocity_left_
                cmd.angular.z = self.angular_velocity_left_
            else:
                cmd.linear.x = self.velocity_right_
                cmd.angular.z = self.angular_velocity_right_
            self.cmd_vel_pub_.publish(cmd)

    def parameter_callback(self, params):
        result = SetParametersResult()
        result.successful = True

        for param in params:
            if param.name == 'color_1':
                if param.type_ == Parameter.Type.INTEGER_ARRAY and len(param.value) == 3:
                    self.color_1_ = param.value
                    self.get_logger().info(f'Parameter "color_1" updated to: {list(param.value)}')
                    # Update pen color if currently on left side
                    if self.current_side_ == 'left':
                        self.call_set_pen_service('left')
                else:
                    result.successful = False
                    result.reason = 'color_1 must be an integer array of length 3 [r, g, b]'

            elif param.name == 'color_2':
                if param.type_ == Parameter.Type.INTEGER_ARRAY and len(param.value) == 3:
                    self.color_2_ = param.value
                    self.get_logger().info(f'Parameter "color_2" updated to: {list(param.value)}')
                    # Update pen color if currently on right side
                    if self.current_side_ == 'right':
                        self.call_set_pen_service('right')
                else:
                    result.successful = False
                    result.reason = 'color_2 must be an integer array of length 3 [r, g, b]'

            elif param.name == 'velocity_left':
                if param.type_ == Parameter.Type.DOUBLE:
                    self.velocity_left_ = param.value
                    self.get_logger().info(f'Parameter "velocity_left" updated to: {param.value}')
                else:
                    result.successful = False
                    result.reason = 'velocity_left must be a double'

            elif param.name == 'velocity_right':
                if param.type_ == Parameter.Type.DOUBLE:
                    self.velocity_right_ = param.value
                    self.get_logger().info(f'Parameter "velocity_right" updated to: {param.value}')
                else:
                    result.successful = False
                    result.reason = 'velocity_right must be a double'

            elif param.name == 'angular_velocity_left':
                if param.type_ == Parameter.Type.DOUBLE:
                    self.angular_velocity_left_ = param.value
                    self.get_logger().info(f'Parameter "angular_velocity_left" updated to: {param.value}')
                else:
                    result.successful = False
                    result.reason = 'angular_velocity_left must be a double'

            elif param.name == 'angular_velocity_right':
                if param.type_ == Parameter.Type.DOUBLE:
                    self.angular_velocity_right_ = param.value
                    self.get_logger().info(f'Parameter "angular_velocity_right" updated to: {param.value}')
                else:
                    result.successful = False
                    result.reason = 'angular_velocity_right must be a double'

        return result


def main(args=None):
    rclpy.init(args=args)
    node = TurtleControllerNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
