#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist


class RobotController(Node):

    def __init__(self):
        super().__init__('robot_controller')

        # Текущий статус (по умолчанию ALL OK)
        self.current_status = "ALL OK"
        self.previous_status = None

        # Подписка на статус
        self.status_sub = self.create_subscription(
            String, '/robot_status', self.status_callback, 10
        )

        # Publisher команд движения
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # Таймер публикации с частотой 10 Гц
        self.timer = self.create_timer(0.1, self.publish_cmd)

        self.get_logger().info('Robot Controller started, initial mode: ALL OK')

    def status_callback(self, msg):
        """Обработчик входящих статусов."""
        new_status = msg.data
        if new_status != self.current_status:
            self.previous_status = self.current_status
            self.current_status = new_status
            self.get_logger().info(f'Mode changed: {self.current_status}')

    def get_twist_from_status(self, status):
        """Возвращает Twist, соответствующий данному статусу."""
        twist = Twist()
        if status == "ALL OK":
            twist.linear.x = 0.3
            twist.angular.z = 0.0
        elif status == "WARNING: Low battery":
            twist.linear.x = 0.1
            twist.angular.z = 0.0
        elif status == "WARNING: Obstacle close":
            twist.linear.x = 0.0
            twist.angular.z = 0.5
        elif status == "CRITICAL":
            twist.linear.x = 0.0
            twist.angular.z = 0.0
        else:
            # Неизвестный статус – останов
            self.get_logger().warn(f'Unknown status: "{status}", stopping robot')
            twist.linear.x = 0.0
            twist.angular.z = 0.0
        return twist

    def publish_cmd(self):
        """Публикует команду движения в соответствии с текущим статусом."""
        twist = self.get_twist_from_status(self.current_status)
        self.cmd_pub.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = RobotController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()