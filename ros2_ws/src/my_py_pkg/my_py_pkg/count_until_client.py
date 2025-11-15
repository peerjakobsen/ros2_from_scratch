import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from my_robot_interfaces.action import CountUntil


class CountUntilClientNode(Node):
    def __init__(self):
        super().__init__('count_until_client')
        # Create an action client for the 'count_until' action
        # ActionClient(node, action_type, action_name)
        self.action_client_ = ActionClient(self, CountUntil, 'count_until')

    def send_goal(self, goal_number, delay):
        # Wait for the action server to become available before sending goal
        self.get_logger().info('Waiting for action server...')
        self.action_client_.wait_for_server()

        # Create and populate the goal message
        goal = CountUntil.Goal()
        goal.goal_number = goal_number
        goal.delay = delay

        self.get_logger().info(f'Sending goal: count to {goal_number} with delay {delay}s')

        # Send goal asynchronously with feedback callback
        # send_goal_async returns a Future that will contain the goal handle
        # We register goal_response_callback to be called when the server responds
        self.action_client_.send_goal_async(
            goal,
            feedback_callback=self.feedback_callback
        ).add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        # This callback is triggered when the server accepts or rejects the goal
        # Extract the goal handle from the Future
        self.goal_handle_ = future.result()

        # Check if the server rejected the goal
        if not self.goal_handle_.accepted:
            self.get_logger().warn('Goal was rejected')
            return

        # Goal was accepted, now request to be notified when result is available
        self.get_logger().info('Goal accepted')
        # get_result_async returns a Future that will contain the final result
        self.goal_handle_.get_result_async().add_done_callback(self.result_callback)

    def feedback_callback(self, feedback_msg):
        # This callback is triggered whenever the server publishes feedback
        # Feedback is sent periodically during goal execution to show progress
        current_number = feedback_msg.feedback.current_number
        self.get_logger().info(f'Feedback: current number = {current_number}')

        # Test: Cancel the goal if counter exceeds 2
        if current_number > 2:
            self.get_logger().info('Counter > 2, canceling goal')
            self.cancel_goal()

    def cancel_goal(self):
        # Request to cancel the currently executing goal
        self.get_logger().info('Sending cancel request')
        # cancel_goal_async returns a Future that will contain the cancel response
        self.goal_handle_.cancel_goal_async().add_done_callback(self.cancel_done_callback)

    def cancel_done_callback(self, future):
        # This callback is triggered when the server responds to the cancel request
        # Extract the cancel response from the Future
        cancel_response = future.result()
        # Check if any goals are being canceled (non-empty list means success)
        if len(cancel_response.goals_canceling) > 0:
            self.get_logger().info('Goal successfully canceled')
        else:
            self.get_logger().warn('Goal failed to cancel')

    def result_callback(self, future):
        # This callback is triggered when the action completes (succeeded, canceled, or aborted)
        # Extract the result from the Future
        # future.result() returns a wrapper, .result gets the actual CountUntil.Result
        result = future.result().result
        self.get_logger().info(f'Result: reached number = {result.reached_number}')


def main(args=None):
    # Initialize the ROS2 Python client library
    rclpy.init(args=args)

    # Create the action client node
    node = CountUntilClientNode()

    # Send a goal: count to 10 with 1 second delay between counts
    node.send_goal(10, 1.0)

    # Keep the node running to process callbacks (feedback, result, cancel)
    rclpy.spin(node)

    # Clean shutdown
    rclpy.shutdown()


if __name__ == '__main__':
    main()
