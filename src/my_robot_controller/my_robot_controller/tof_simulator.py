 #!/usr/bin/env python3
  import math
  from rclpy.node import Node
  import rclpy
  from geometry_msgs.msg import Twist
  from sensor_msgs.msg import Range


  class ToFSimulator(Node):
      def __init__(self):
          super().__init__("tof_simulator")

          # Parameters
          self.declare_parameter("min_range", 0.03)
          self.declare_parameter("max_range", 2.0)
          self.declare_parameter("publish_hz", 50.0)
          self.declare_parameter("base_distance", 1.0)  # initial distance to obstacle ahead
          self.declare_parameter("turn_gain", 0.2)       # meters per rad/s
          self.declare_parameter("forward_gain", 1.0)    # meters per (m/s)

          self.min_range = float(self.get_parameter("min_range").value)
          self.max_range = float(self.get_parameter("max_range").value)
          self.publish_hz = float(self.get_parameter("publish_hz").value)
          self.base_distance = float(self.get_parameter("base_distance").value)
          self.turn_gain = float(self.get_parameter("turn_gain").value)
          self.forward_gain = float(self.get_parameter("forward_gain").value)

          self.vx = 0.0
          self.wz = 0.0

          self.pub_left = self.create_publisher(Range, "/tof/left", 10)
          self.pub_right = self.create_publisher(Range, "/tof/right", 10)
          self.sub_cmd = self.create_subscription(Twist, "/cmd_vel", self.on_cmd_vel, 10)

          self.timer = self.create_timer(1.0 / self.publish_hz, self.on_timer)

      def on_cmd_vel(self, msg: Twist):
          self.vx = msg.linear.x
          self.wz = msg.angular.z

      def clamp(self, value: float) -> float:
          return max(self.min_range, min(self.max_range, value))

      def on_timer(self):
          dt = 1.0 / self.publish_hz

          # Forward motion decreases distance
          self.base_distance -= self.forward_gain * self.vx * dt
          self.base_distance = self.clamp(self.base_distance)

          # Turning creates asymmetry
          delta = self.turn_gain * self.wz
          left_range = self.clamp(self.base_distance - delta)
          right_range = self.clamp(self.base_distance + delta)

          now = self.get_clock().now().to_msg()

          msg_left = Range()
          msg_left.header.stamp = now
          msg_left.header.frame_id = "tof_left"
          msg_left.radiation_type = Range.INFRARED
          msg_left.field_of_view = math.radians(15.0)
          msg_left.min_range = self.min_range
          msg_left.max_range = self.max_range
          msg_left.range = left_range

          msg_right = Range()
          msg_right.header.stamp = now
          msg_right.header.frame_id = "tof_right"
          msg_right.radiation_type = Range.INFRARED
          msg_right.field_of_view = math.radians(15.0)
          msg_right.min_range = self.min_range
          msg_right.max_range = self.max_range
          msg_right.range = right_range

          self.pub_left.publish(msg_left)
          self.pub_right.publish(msg_right)


  def main():
      rclpy.init()
      node = ToFSimulator()
      rclpy.spin(node)
      node.destroy_node()
      rclpy.shutdown()


  if __name__ == "__main__":
      main()