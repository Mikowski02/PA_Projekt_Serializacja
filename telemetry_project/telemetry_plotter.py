import numpy as np
import msgpack
import matplotlib.pyplot as plt

class TrajectorySession:
    def __init__(self, description="", timestamp="", sample_count=0):
        self.description = description
        self.timestamp = timestamp
        self.sample_count = sample_count
        self.x = np.array([], dtype=np.float64)
        self.y = np.array([], dtype=np.float64)

def dnc_telemetry(code, data):
    if code == 1:
        desc, timestamp, count, x_buf, y_buf = msgpack.unpackb(data)
        session = TrajectorySession(desc, timestamp, count)
        session.x = np.frombuffer(x_buf, dtype=np.float64)
        session.y = np.frombuffer(y_buf, dtype=np.float64)
        return session
    return msgpack.ExtType(code, data)

def main():
    with open('trajectory_data.dat', 'rb') as f:
        session = msgpack.load(f, ext_hook=dnc_telemetry)

    print(f"Wczytano sesję: {session.description}")
    print(f"Data: {session.timestamp} | Liczba próbek: {session.sample_count}")

    if session.sample_count == 0 or len(session.x) == 0:
        print("Brak danych trajektorii do wyświetlenia.")
        return

    plt.figure(figsize=(8, 6))
    plt.plot(session.x, session.y, 'b-', label='Trajektoria robota', linewidth=1.5)
    plt.scatter(session.x[0], session.y[0], c='green', s=100, zorder=5, label='Start', marker='o')
    plt.scatter(session.x[-1], session.y[-1], c='red', s=100, zorder=5, label='Koniec', marker='X')

    plt.title(f"{session.description}\nData wykonania: {session.timestamp}")
    plt.xlabel("X [m]")
    plt.ylabel("Y [m]")
    plt.axis('equal')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    main()
