#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from std_msgs.msg import Int32MultiArray
import serial

class SerialThrusterWrapper(Node):
    def __init__(self):
        super().__init__("serial_thruster_wrapper")

        self.declare_parameter("port", "/dev/ttyUSB0")
        self.declare_parameter("baudrate", 115200)
        self.declare_parameter("deadzone", 0.05)

        port = self.get_parameter("port").value
        baudrate = self.get_parameter("baudrate").value
        self.deadzone_ = self.get_parameter("deadzone").value

        try:
            self.ser = serial.Serial(port, baudrate, timeout=0.1)
            self.get_logger().info(f"Connected to serial port: {port} at {baudrate} baud")
        except serial.SerialException as e:
            self.get_logger().error(f"Failed to open serial port {port}: {e}")
            self.ser = None

        self.T1_ = 1500
        self.T2_ = 1500
        self.T3_ = 1500

        self.create_subscription(Joy, "/joy", self.joy_callback, 10)
        self.publisher = self.create_publisher(Int32MultiArray, "/motor_cmd", 10)
        self.create_timer(0.1, self.publish_and_send_serial)

    def scaleJoystick(self, raw_val):
        if abs(raw_val) < self.deadzone_:
            val = 0.0
        else:
            val = raw_val

        if val >= 0.0:
            return int(round(1500 + 400 * val))
        return int(round(1500 + 200 * val))

    def joy_callback(self, msg):
        if len(msg.axes) < 4:
            return

        self.T1_ = self.scaleJoystick(msg.axes[1])
        self.T2_ = self.scaleJoystick(-msg.axes[0])
        self.T3_ = self.scaleJoystick(-msg.axes[3])

    def publish_and_send_serial(self):
        values = [self.T1_, self.T2_, self.T3_, 1500]

        msg = Int32MultiArray()
        msg.data = values
        self.publisher.publish(msg)

        if self.ser and self.ser.is_open:
            data_str = f"{self.T1_},{self.T2_},{self.T3_},1500\n"
            self.ser.write(data_str.encode('utf-8'))

    def destroy_node(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = SerialThrusterWrapper()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()
