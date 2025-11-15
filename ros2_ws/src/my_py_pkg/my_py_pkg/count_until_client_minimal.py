import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from my_robot_interfaces.action import CountUntil


class CountUntilClientNode(Node):
    def __init__(self):
        super().__init__('count_until_client')
        self.action_client_ = ActionClient(self, CountUntil, 'count_until')

    def send_goal(self, goal_number, delay):
        self.get_logger().info('Waiting for action server...')
        self.action_client_.wait_for_server()

        goal = CountUntil.Goal()
        goal.goal_number = goal_number
        goal.delay = delay

        self.get_logger().info(f'Sending goal: count to {goal_number} with delay {delay}s')

        self.action_client_.send_goal_async(
            goal,
            feedback_callback=self.feedback_callback
        ).add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        self.goal_handle_ = future.result()

        if not self.goal_handle_.accepted:
            self.get_logger().warn('Goal was rejected')
            return

        self.get_logger().info('Goal accepted')
        self.goal_handle_.get_result_async().add_done_callback(self.result_callback)

    def feedback_callback(self, feedback_msg):
        current_number = feedback_msg.feedback.current_number
        self.get_logger().info(f'Feedback: current number = {current_number}')

    def result_callback(self, future):
        result = future.result().result
        self.get_logger().info(f'Result: reached number = {result.reached_number}')


def main(args=None):
    rclpy.init(args=args)
    node = CountUntilClientNode()
    node.send_goal(10, 1.0)
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
