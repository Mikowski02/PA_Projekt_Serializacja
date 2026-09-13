import sys
from datetime import datetime
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
import numpy as np
import msgpack

class TrajectorySession:
    def __init__(self, description=""):
        self.description = description
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.sample_count = 0
        self.x = []
        self.y = []

def enc_telemetry(obj):
    if isinstance(obj, TrajectorySession):
        x_bytes = np.array(obj.x, dtype=np.float64).tobytes()
        y_bytes = np.array(obj.y, dtype=np.float64).tobytes()
        return msgpack.ExtType(1, msgpack.packb([
            obj.description, obj.timestamp, obj.sample_count, x_bytes, y_bytes
        ]))
    raise TypeError(f"Object of type {type(obj)} is not serializable")

class TelemetryRecorder(Node):
    def __init__(self, session):
        super().__init__('telemetry_recorder')
        self.session = session
        self.sub = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        self.get_logger().info(f"Rejestrator uruchomiony dla: {session.description}")

    def odom_callback(self, msg):
        self.session.x.append(msg.pose.pose.position.x)
        self.session.y.append(msg.pose.pose.position.y)
        self.session.sample_count += 1

def main():
    rclpy.init()
    desc = sys.argv[1] if len(sys.argv) > 1 else "Eksperyment Ground Truth"
    session = TrajectorySession(desc)
    node = TelemetryRecorder(session)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info(f"Zapisywanie {session.sample_count} próbek...")
        with open('trajectory_data.dat', 'wb') as f:
            msgpack.dump(session, f, default=enc_telemetry)
        node.get_logger().info("Zapisano pomyślnie do trajectory_data.dat")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
