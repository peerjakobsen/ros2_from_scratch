import rclpy
import time
from rclpy.node import Node
from rclpy.action import ActionServer, GoalResponse, CancelResponse
from rclpy.action.server import ServerGoalHandle
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup
from my_robot_interfaces.action import CountUntil


class CountUntilServerNode(Node):
    def __init__(self):
        super().__init__('count_until_server')
        # Create an action server for the 'count_until' action
        # ActionServer requires:
        # - node: the ROS2 node instance
        # - action_type: the action interface (CountUntil)
        # - action_name: the name clients will use to connect
        # - execute_callback: function that performs the actual work
        # - goal_callback: function that validates and accepts/rejects goals
        # - cancel_callback: function that handles cancel requests
        # - callback_group: ReentrantCallbackGroup allows callbacks to run in parallel
        #   (needed for cancel to interrupt execute)
        self.action_server_ = ActionServer(
            self,
            CountUntil,
            'count_until',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            callback_group=ReentrantCallbackGroup()
        )
        self.get_logger().info('Action server has been started')

    def goal_callback(self, goal_request):
        # This callback is triggered when a client sends a goal
        # Used to validate the goal before accepting it
        # Must return GoalResponse.ACCEPT or GoalResponse.REJECT
        self.get_logger().info('Received goal request')

        # Validate: reject goals with invalid parameters
        if goal_request.goal_number <= 0:
            self.get_logger().warn(f'Rejecting goal: goal_number {goal_request.goal_number} is <= 0')
            return GoalResponse.REJECT

        # Goal is valid, accept it
        self.get_logger().info(f'Accepting goal: count to {goal_request.goal_number}')
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        # This callback is triggered when a client requests to cancel a goal
        # Runs on a separate thread (due to ReentrantCallbackGroup)
        # Must return CancelResponse.ACCEPT or CancelResponse.REJECT
        self.get_logger().info('Received cancel request')
        return CancelResponse.ACCEPT

    def execute_callback(self, goal_handle):
        # This callback performs the actual work of the action
        # Runs after goal is accepted and continues until:
        # - Goal completes successfully (goal_handle.succeed())
        # - Goal is canceled (goal_handle.canceled())
        # - Goal is aborted (goal_handle.abort())

        # Extract goal parameters
        target_number = goal_handle.request.goal_number
        delay = goal_handle.request.delay

        counter = 0
        self.get_logger().info(f'Executing goal: counting to {target_number} with delay {delay}s')

        # Create feedback message to send progress updates to client
        feedback = CountUntil.Feedback()

        # Main execution loop
        for i in range(target_number):
            # Check if client requested cancellation
            # This flag is set when cancel_callback returns ACCEPT
            if goal_handle.is_cancel_requested:
                self.get_logger().info('Goal canceled')
                # Mark goal as canceled
                goal_handle.canceled()
                # Return partial result (how far we got)
                result = CountUntil.Result()
                result.reached_number = counter
                return result

            # Increment counter
            counter += 1
            self.get_logger().info(f'Counter: {counter}')

            # Publish feedback to inform client of progress
            feedback.current_number = counter
            goal_handle.publish_feedback(feedback)

            # Wait before next iteration
            time.sleep(delay)

        # Goal completed successfully
        goal_handle.succeed()

        # Create and return final result
        result = CountUntil.Result()
        result.reached_number = counter
        return result


def main(args=None):
    # Initialize the ROS2 Python client library
    rclpy.init(args=args)

    # Create the action server node
    node = CountUntilServerNode()

    # Spin with MultiThreadedExecutor to allow callbacks to run in parallel
    # This is essential for cancel requests to interrupt the execute callback
    # Without this, cancel_callback would wait for execute_callback to finish
    rclpy.spin(node, MultiThreadedExecutor())

    # Clean shutdown
    rclpy.shutdown()


if __name__ == '__main__':
    main()
