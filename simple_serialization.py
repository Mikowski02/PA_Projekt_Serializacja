import os
import time
import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from turtlesim.msg import Pose
from geometry_msgs.msg import Vector3
import msgpack

class TurtleVectorTracker(Node):
    def __init__(self):
        super().__init__('turtle_vector_tracker')
        self.sub = self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)
        self.pub = self.create_publisher(Vector3, '/turtle1/relative_vector', 10)
        self.origin = None
        self.start_time = None
        self.data = {"time": [], "dx": [], "dy": [], "dtheta": []}

    def pose_callback(self, msg):
        now = time.time()
        if self.origin is None:
            self.origin = (msg.x, msg.y, msg.theta)
            self.start_time = now
            print(f"Punkt startowy: x={msg.x:.2f}, y={msg.y:.2f}, theta={msg.theta:.2f}")

        dt = round(now - self.start_time, 2)
        dx = round(msg.x - self.origin[0], 3)
        dy = round(msg.y - self.origin[1], 3)
        dtheta = round(msg.theta - self.origin[2], 3)

        self.data["time"].append(dt)
        self.data["dx"].append(dx)
        self.data["dy"].append(dy)
        self.data["dtheta"].append(dtheta)

        vec_msg = Vector3()
        vec_msg.x = float(dx)
        vec_msg.y = float(dy)
        vec_msg.z = float(dtheta)
        self.pub.publish(vec_msg)

def save_data(path, data):
    with open(path, "wb") as f:
        msgpack.pack(data, f)

def load_data(path):
    with open(path, "rb") as f:
        return msgpack.unpack(f)

def main():
    rclpy.init()
    node = TurtleVectorTracker()
    folder = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(folder, "vector_time")

    print("Oczekiwanie na dane z /turtle1/pose...")
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

    if len(node.data["time"]) > 0:
        save_data(filepath, node.data)
        print(f"Zapisano {len(node.data['time'])} próbek do {os.path.basename(filepath)}")
        loaded = load_data(filepath)
        print(f"Czas: {loaded['time'][0]}s - {loaded['time'][-1]}s")
        print(f"Wektor końcowy: dx={loaded['dx'][-1]}, dy={loaded['dy'][-1]}, dtheta={loaded['dtheta'][-1]}")
    else:
        print("Brak danych do zapisu.")

if __name__ == "__main__":
    main()
