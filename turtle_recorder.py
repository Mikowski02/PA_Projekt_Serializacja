import os
import math
import time
import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from turtlesim.msg import Pose
from geometry_msgs.msg import Vector3
import msgpack

class TurtleRecorder(Node):
    def __init__(self):
        super().__init__('turtle_recorder')
        self.sub = self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)
        self.pub = self.create_publisher(Vector3, '/turtle1/relative_vector', 10)
        self.origin = None
        self.start_time = None
        self.data = {"time": [], "dx": [], "dy": [], "dtheta": [], "v": [], "w": []}

    def pose_callback(self, msg):
        now = time.time()
        if self.origin is None:
            self.origin = (msg.x, msg.y, msg.theta)
            self.start_time = now
            print(f"Start: x={msg.x:.2f}, y={msg.y:.2f}, theta={msg.theta:.2f}")

        # wektor wzgledny
        dt = round(now - self.start_time, 3)
        dx = round(msg.x - self.origin[0], 4)
        dy = round(msg.y - self.origin[1], 4)
        dtheta = round(math.atan2(math.sin(msg.theta - self.origin[2]), math.cos(msg.theta - self.origin[2])), 4)

        self.data["time"].append(dt)
        self.data["dx"].append(dx)
        self.data["dy"].append(dy)
        self.data["dtheta"].append(dtheta)
        self.data["v"].append(round(float(msg.linear_velocity), 4))
        self.data["w"].append(round(float(msg.angular_velocity), 4))

        # wektor na zywo
        vec = Vector3()
        vec.x = float(dx)
        vec.y = float(dy)
        vec.z = float(dtheta)
        self.pub.publish(vec)

# MessagePack
def save_data(path, data):
    with open(path, "wb") as f:
        msgpack.pack(data, f)

def main():
    rclpy.init()
    node = TurtleRecorder()
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vector_time")

    print("Rejestrator uruchomiony. Nasluchiwanie /turtle1/pose...")
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

    if len(node.data["time"]) > 0:
        save_data(path, node.data)
        print(f"Zapisano {len(node.data['time'])} probek do pliku {os.path.basename(path)}")
    else:
        print("Brak danych do zapisu.")

if __name__ == "__main__":
    main()
