#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, Bool


class BatteryNode(Node):

    def __init__(self):
        super().__init__('battery_node')
        self.battery_level = 100.0
        self.is_robot_moving = False

        self.battery_publisher = self.create_publisher(Float32, '/battery_level', 10)
        self.motor_subscriber = self.create_subscription(
            Bool, '/motor_state', self.motor_state_callback, 10
        )
        self.timer = self.create_timer(2.0, self.update_battery)
        self.get_logger().info(f'Battery Node started - Initial charge {self.battery_level}%')

    def motor_state_callback(self, msg):
        self.is_robot_moving = msg.data
        state = "MOVING" if self.is_robot_moving else "IDLE"
        self.get_logger().info(f'Motor state changed: {state}')

    def update_battery(self):
        if self.battery_level <= 0.0:
            self.battery_level = 0.0
            self.get_logger().error('Battery depleted! Robot shutdown imminent')
            return

        if self.is_robot_moving:
            discharge_rate = 5.0
            self.get_logger().warn(f'Battery draining fast (moving): -{discharge_rate}%')
        else:
            discharge_rate = 1.0

        self.battery_level -= discharge_rate
        msg = Float32()
        msg.data = max(0.0, self.battery_level)
        self.battery_publisher.publish(msg)

        if self.battery_level < 20.0 and self.battery_level > 0:
            self.get_logger().warn(f'Low battery: {self.battery_level:.1f}%')
        elif self.battery_level > 0:
            self.get_logger().info(f'Battery level: {self.battery_level:.1f}%')


def main(args=None):
    rclpy.init(args=args)
    node = BatteryNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()