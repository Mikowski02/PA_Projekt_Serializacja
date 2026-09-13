import os
import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from geometry_msgs.msg import Twist, Vector3
import msgpack

class TurtlePlayer(Node):
    def __init__(self, data):
        super().__init__('turtle_player')
        self.pub_cmd = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.pub_vec = self.create_publisher(Vector3, '/turtle1/target_vector', 10)
        self.data = data
        self.total = len(data["time"])
        self.idx = 0

        dt = 0.05
        if self.total > 1:
            dt = max(0.01, (data["time"][-1] - data["time"][0]) / self.total)

        self.timer = self.create_timer(dt, self.timer_callback)
        print(f"Odtwarzacz gotowy. Liczba punktow: {self.total}, krok: {dt:.3f}s")

    def timer_callback(self):
        if self.idx >= self.total:
            self.stop_turtle()
            print("Odtwarzanie trajektorii zakonczone.")
            raise SystemExit

        vec = Vector3()
        vec.x = float(self.data["dx"][self.idx])
        vec.y = float(self.data["dy"][self.idx])
        vec.z = float(self.data["dtheta"][self.idx])
        self.pub_vec.publish(vec)

        cmd = Twist()
        cmd.linear.x = float(self.data["v"][self.idx])
        cmd.angular.z = float(self.data["w"][self.idx])
        self.pub_cmd.publish(cmd)

        self.idx += 1

    def stop_turtle(self):
        cmd = Twist()
        self.pub_cmd.publish(cmd)

def load_data(path):
    with open(path, "rb") as f:
        return msgpack.unpack(f)

def main():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vector_time")
    if not os.path.exists(path):
        print(f"Blad: Plik {os.path.basename(path)} nie istnieje.")
        return

    data = load_data(path)
    if not data or len(data.get("time", [])) == 0:
        print("Brak probek w pliku.")
        return

    rclpy.init()
    node = TurtlePlayer(data)
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException, SystemExit):
        node.stop_turtle()
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == "__main__":
    main()
