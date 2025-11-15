import rclpy
import time
from rclpy.node import Node
from rclpy.action import ActionServer, GoalResponse
from rclpy.action.server import ServerGoalHandle
from my_robot_interfaces.action import CountUntil


class CountUntilServerNode(Node):
    def __init__(self):
        super().__init__('count_until_server')
        self.action_server_ = ActionServer(
            self,
            CountUntil,
            'count_until',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback
        )
        self.get_logger().info('Action server has been started')

    def goal_callback(self, goal_request):
        self.get_logger().info('Received goal request')

        if goal_request.goal_number <= 0:
            self.get_logger().warn(f'Rejecting goal: goal_number {goal_request.goal_number} is <= 0')
            return GoalResponse.REJECT

        self.get_logger().info(f'Accepting goal: count to {goal_request.goal_number}')
        return GoalResponse.ACCEPT

    def execute_callback(self, goal_handle):
        target_number = goal_handle.request.goal_number
        delay = goal_handle.request.delay

        counter = 0
        self.get_logger().info(f'Executing goal: counting to {target_number} with delay {delay}s')

        for i in range(target_number):
            counter += 1
            self.get_logger().info(f'Counter: {counter}')
            time.sleep(delay)

        goal_handle.succeed()

        result = CountUntil.Result()
        result.reached_number = counter
        return result


def main(args=None):
    rclpy.init(args=args)
    node = CountUntilServerNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
