# Serializacja trajektorii żółwika w ROS 2
Nagrywanie, binarna serializacja (MessagePackiem) i odtwarzanie trajektorii żółwia z wykorzystaniem symulatora samouczkowego turtlesim.

 `turtle_recorder.py` – subskrybuje `/turtle1/pose`, publikuje wektor względny na `/turtle1/relative_vector` i po zatrzymaniu zapisuje trasę do binarnego pliku `vector_time`.

 `turtle_player.py` – odczytuje `vector_time`, publikuje zadany wektor na `/turtle1/target_vector` i wysyła komendy prędkości `/turtle1/cmd_vel`, powtarzając ruch.

---

## Komendy
```bash
sudo apt update && sudo apt install -y python3-msgpack
cd ros2_jazzy/src
git clone https://github.com/Mikowski02/PA_Projekt_Serializacja.git
cd PA_Projekt_Serializacja
```

**Terminal 1 (Symulator):**
```bash
cd ros2_jazzy/src/PA_Projekt_Serializacja
source /opt/ros/jazzy/setup.bash
ros2 run turtlesim turtlesim_node
```

**Terminal 2 (Rejestrator):**
```bash
cd ros2_jazzy/src/PA_Projekt_Serializacja
source /opt/ros/jazzy/setup.bash
python3 turtle_recorder.py
```

**Terminal 3 (Sterowanie):**
```bash
cd ros2_jazzy/src/PA_Projekt_Serializacja
source /opt/ros/jazzy/setup.bash
ros2 run turtlesim turtle_teleop_key
```

**Terminal 4 (Podgląd wektora z topica nagrywania):**
```bash
cd ros2_jazzy/src/PA_Projekt_Serializacja
source /opt/ros/jazzy/setup.bash
ros2 topic echo /turtle1/relative_vector
```

---

## Odtwarzanie
Terminal 1 z topiciem /turtle1/pose pozostaje aktywny.

```bash
cd ros2_jazzy/src/PA_Projekt_Serializacja
source /opt/ros/jazzy/setup.bash
python3 turtle_player.py
```

**Terminal 4 (Podgląd wektora z topica odtwarzania):**
```bash
cd ros2_jazzy/src/PA_Projekt_Serializacja
source /opt/ros/jazzy/setup.bash
ros2 topic echo /turtle1/target_vector
```
