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

        # Timer częstotliwości 
        self._timer_dt = 0.01
        self._start_ros_time = None
        self._recording_start = data["time"][0]

        self.timer = self.create_timer(self._timer_dt, self.timer_callback)
        print(f"Odtwarzacz gotowy. Liczba punktow: {self.total}")
        print(f"Czas trwania nagrania: {data['time'][-1] - data['time'][0]:.3f}s")

    def timer_callback(self):
        if self._start_ros_time is None:
            self._start_ros_time = self.get_clock().now()

        # Czas od startu odtwarzania (sekundy)
        elapsed = (self.get_clock().now() - self._start_ros_time).nanoseconds * 1e-9

        # Wyślij wszystkie próbki, których timestamp już minął
        while self.idx < self.total and \
              (self.data["time"][self.idx] - self._recording_start) <= elapsed:

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

        # Koniec odtwarzania
        if self.idx >= self.total:
            self.stop_turtle()
            print("Odtwarzanie trajektorii zakonczone.")
            raise SystemExit

    def stop_turtle(self):
        try:
            if rclpy.ok():
                cmd = Twist()
                self.pub_cmd.publish(cmd)
        except Exception:
            pass

# MessagePack
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
