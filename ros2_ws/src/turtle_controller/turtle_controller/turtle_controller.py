#!/usr/bin/env python3
import math
import random
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtlesim.srv import SetPen
from my_robot_interfaces.srv import SetSpinning


class TurtleControllerNode(Node):
    def __init__(self):
        super().__init__("turtle_controller")
        self.cmd_vel_pub_ = self.create_publisher(Twist, "/turtle1/cmd_vel", 10)
        self.pose_sub_ = self.create_subscription(Pose, "/turtle1/pose",
                                                   self.callback_pose, 10)
        self.set_pen_client_ = self.create_client(SetPen, "/turtle1/set_pen")
        self.set_spinning_server_ = self.create_service(SetSpinning, "~/set_spinning",
                                                         self.callback_set_spinning)

        # Rotation tracking
        self.rotation_count_ = 0.0
        self.last_theta_ = 0.0
        self.last_set_pen_rotation_ = 0.0

        # Spinning state
        self.spinning_enabled_ = True

    def callback_set_spinning(self, request, response):
        self.spinning_enabled_ = request.spinning
        response.success = True
        status = "enabled" if request.spinning else "disabled"
        response.message = f"Spinning {status}"
        self.get_logger().info(f"Spinning {status}")
        return response

    def call_set_pen_service(self):
        while not self.set_pen_client_.wait_for_service(1.0):
            self.get_logger().warn("Waiting for /turtle1/set_pen service...")

        request = SetPen.Request()
        request.r = random.randint(0, 255)
        request.g = random.randint(0, 255)
        request.b = random.randint(0, 255)
        request.width = 20

        self.get_logger().info(f"Setting pen to RGB({request.r}, {request.g}, {request.b})")
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

        # Call set_pen service every 2 full rotations
        if self.rotation_count_ - self.last_set_pen_rotation_ >= 2.0:
            self.get_logger().info(f"Completed 2 rotations ({self.rotation_count_:.2f} total)")
            self.call_set_pen_service()
            self.last_set_pen_rotation_ = self.rotation_count_

        # Only publish velocity commands if spinning is enabled
        if self.spinning_enabled_:
            cmd = Twist()
            if pose.x < 5.5:
                cmd.linear.x = 1.0
                cmd.angular.z = 1.0
            else:
                cmd.linear.x = 2.0
                cmd.angular.z = 2.0
            self.cmd_vel_pub_.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = TurtleControllerNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
