#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from geometry_msgs.msg import Twist


class DistanceSensor(Node):
    """
    Симулятор датчика расстояния.
    Публикует расстояние в топик /distance с частотой 5 Гц.
    Расстояние изменяется в зависимости от движения робота (cmd_vel):
    - Стоим: 3.0 м
    - Вперёд: уменьшается на 0.2 м каждые 0.2 с до минимума 0.5 м
    - Назад: увеличивается на 0.2 м каждые 0.2 с до максимума 3.0 м
    """

    def __init__(self):
        super().__init__('distance_sensor')
        self.distance = 3.0
        self.moving_forward = False
        self.moving_backward = False

        # Publisher
        self.publisher_ = self.create_publisher(Float32, '/distance', 10)

        # Subscriber to cmd_vel
        self.subscription = self.create_subscription(
            Twist, '/cmd_vel', self.cmd_vel_callback, 10
        )

        # Timer for 5 Hz (0.2 seconds)
        self.timer = self.create_timer(0.2, self.update_distance)

        self.get_logger().info('Distance Sensor started')

    def cmd_vel_callback(self, msg):
        """Обновляет флаги движения на основе полученной команды."""
        self.moving_forward = (msg.linear.x > 0)
        self.moving_backward = (msg.linear.x < 0)

    def update_distance(self):
        """Изменяет расстояние в зависимости от движения и публикует."""
        if self.moving_forward:
            self.distance -= 0.2
            if self.distance < 0.5:
                self.distance = 0.5
        elif self.moving_backward:
            self.distance += 0.2
            if self.distance > 3.0:
                self.distance = 3.0
        else:
            self.distance = 3.0

        msg = Float32()
        msg.data = self.distance
        self.publisher_.publish(msg)

        # Логирование для отладки (можно убрать)
        self.get_logger().info(f'Distance: {self.distance:.2f} m')


def main(args=None):
    rclpy.init(args=args)
    node = DistanceSensor()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()