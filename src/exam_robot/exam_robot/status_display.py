#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, String


class StatusDisplay(Node):
    """
    Узел для отображения статуса робота.
    Подписывается на /battery_level и /distance, публикует /robot_status с частотой 2 Гц.
    Определяет статус по следующим правилам:
    - Батарея ≥ 20% И distance ≥ 1.0м → "ALL OK"
    - Батарея < 20% → "WARNING: Low battery"
    - Distance < 1.0м → "WARNING: Obstacle close"
    - Батарея < 10% ИЛИ distance < 0.7м → "CRITICAL"
    Логирует каждое изменение статуса.
    """

    def __init__(self):
        super().__init__('status_display')

        # Храним последние полученные значения
        self.battery = 100.0      # начальное значение (будет быстро обновлено)
        self.distance = 3.0        # начальное значение
        self.previous_status = ""  # для отслеживания изменений

        # Подписки
        self.battery_sub = self.create_subscription(
            Float32, '/battery_level', self.battery_callback, 10
        )
        self.distance_sub = self.create_subscription(
            Float32, '/distance', self.distance_callback, 10
        )

        # Publisher статуса
        self.status_pub = self.create_publisher(String, '/robot_status', 10)

        # Таймер для публикации с частотой 2 Гц (0.5 секунды)
        self.timer = self.create_timer(0.5, self.publish_status)

        self.get_logger().info('Status Display node started')

    def battery_callback(self, msg):
        self.battery = msg.data

    def distance_callback(self, msg):
        self.distance = msg.data

    def determine_status(self):
        """
        Определяет статус на основе текущих значений battery и distance.
        Возвращает строку статуса.
        """
        # Сначала проверяем CRITICAL условия (наивысший приоритет)
        if self.battery < 10.0 or self.distance < 0.7:
            return "CRITICAL"
        # Затем проверяем предупреждения
        if self.battery < 20.0:
            return "WARNING: Low battery"
        if self.distance < 1.0:
            return "WARNING: Obstacle close"
        return "ALL OK"

    def publish_status(self):
        status = self.determine_status()
        msg = String()
        msg.data = status
        self.status_pub.publish(msg)

        # Логируем только при изменении статуса
        if status != self.previous_status:
            self.get_logger().info(f'Status changed: {status}')
            self.previous_status = status


def main(args=None):
    rclpy.init(args=args)
    node = StatusDisplay()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()