import os
import math
import msgpack

def save_data(path, data):
    with open(path, "wb") as f:
        msgpack.pack(data, f)

def load_data(path):
    with open(path, "rb") as f:
        return msgpack.unpack(f)

def generate_turtle_data(steps=50, dt=0.1):
    t = []
    x = []
    y = []
    theta = []

    curr_x = 5.5
    curr_y = 5.5
    curr_theta = 0.0

    for i in range(steps):
        time_stamp = round(i * dt, 2)
        curr_x += 0.1 * math.cos(curr_theta)
        curr_y += 0.1 * math.sin(curr_theta)
        curr_theta += 0.05

        t.append(time_stamp)
        x.append(round(curr_x, 3))
        y.append(round(curr_y, 3))
        theta.append(round(curr_theta, 3))

    return {
        "turtle_name": "turtle1",
        "time": t,
        "x": x,
        "y": y,
        "theta": theta
    }

def main():
    folder = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(folder, "vector_time")

    data = generate_turtle_data()
    save_data(filepath, data)
    print(f"Zapisano {len(data['time'])} próbek do {os.path.basename(filepath)}")

    loaded = load_data(filepath)
    print(f"Wczytano obiekt: {loaded['turtle_name']}")
    print(f"Czas: {loaded['time'][0]}s - {loaded['time'][-1]}s")
    print(f"Start: x={loaded['x'][0]}, y={loaded['y'][0]}")
    print(f"Koniec: x={loaded['x'][-1]}, y={loaded['y'][-1]}")

if __name__ == "__main__":
    main()
