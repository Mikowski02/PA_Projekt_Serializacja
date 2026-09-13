# Rejestrator Wektora Względnego Żółwia (ROS 2 & MessagePack)

Węzeł ROS 2 integrujący się z symulatorem `turtlesim`. Skrypt automatycznie zeruje pozycję startową żółwia, wylicza jego wektor przemieszczenia w czasie, publikuje go w czasie rzeczywistym na dodatkowy topic oraz serializuje zebrane dane do pliku binarnego `vector_time`.

---

## 1. Jak to działa w ekosystemie ROS 2?

1. **Subskrypcja `/turtle1/pose`**:
   Węzeł nasłuchuje pozycji żółwia wysyłanej przez `turtlesim_node`.
2. **Automatyczne zerowanie punktu startowego**:
   Niezależnie od tego, w którym miejscu planszy żółw się znajduje w momencie uruchomienia skryptu, pierwsza odebrana pozycja zostaje zapamiętana jako punkt odniesienia:
   $$(x_0, y_0, \theta_0)$$
   Od tego momentu pozycja startowa traktowana jest jako $(0, 0, 0)$.
3. **Wyliczanie wektora przemieszczenia**:
   Dla każdego kolejnego punktu w czasie $t$ wyliczany jest wektor ruchu:
   $$\Delta x = x - x_0, \quad \Delta y = y - y_0, \quad \Delta \theta = \theta - \theta_0$$
4. **Dodatkowy topic `/turtle1/relative_vector`**:
   Skrypt działa jednocześnie jako nadawca – w czasie rzeczywistym publikuje bieżący wektor przemieszczenia na nowy topic `/turtle1/relative_vector` (`geometry_msgs/msg/Vector3`), co pozwala na podgląd na żywo w innych narzędziach ROS 2.
5. **Zapis do pliku binarnego (`vector_time`)**:
   Po wciśnięciu `Ctrl+C` zgromadzona trajektoria zostaje zserializowana za pomocą biblioteki `msgpack` bezpośrednio do pliku `vector_time`.

---

## 2. Omówienie kodu `simple_serialization.py`

### Klasa `TurtleVectorTracker(Node)`
* Dziedziczy po `rclpy.node.Node` i tworzy węzeł o nazwie `turtle_vector_tracker`.
* `self.sub`: Subskrybuje `/turtle1/pose` (`turtlesim/msg/Pose`).
* `self.pub`: Tworzy nowy topic `/turtle1/relative_vector` (`geometry_msgs/msg/Vector3`).
* `self.origin`: Zmienna przechowująca współrzędne początkowe $(x_0, y_0, \theta_0)$. Przed odebraniem pierwszej wiadomości ma wartość `None`.
* `pose_callback(msg)`:
  * Gdy `self.origin is None`, przypisuje aktualną pozycję żółwia jako punkt $(0, 0, 0)$ oraz zapisuje czas początkowy.
  * Wylicza różnice $(\Delta x, \Delta y, \Delta \theta)$ oraz czas trwania $\Delta t$.
  * Zapisuje próbki do bufora `self.data`.
  * Publikuje komunikat `Vector3` na topic `/turtle1/relative_vector`.

### Funkcje zapisu i odczytu
* `save_data(path, data)`: Otwiera plik w trybie binarnym (`"wb"`) i wywołuje `msgpack.pack(data, f)`.
* `load_data(path)`: Otwiera plik w trybie binarnym (`"rb"`) i rekonstruuje strukturę za pomocą `msgpack.unpack(f)`.

### Funkcja `main()`
* Inicjalizuje ROS 2 (`rclpy.init()`).
* Uruchamia pętlę zdarzeń `rclpy.spin(node)`.
* Przechwytuje bezpiecznie przerwanie `Ctrl+C` (`KeyboardInterrupt`, `ExternalShutdownException`), niszczy węzeł i zamyka kontekst ROS 2.
* Jeśli zebrano próbki, zapisuje je do pliku `vector_time`, wczytuje z powrotem i wyświetla w konsoli podsumowanie (czas trwania i wektor końcowy).

---

## 3. Instrukcja uruchomienia krok po kroku

Otwórz 3 terminale (w każdym załaduj środowisko ROS 2):

### Terminal 1: Uruchomienie planszy turtlesim
```bash
ros2 run turtlesim turtlesim_node
```

### Terminal 2: Uruchomienie rejestratora i dodatkowego topicu
W katalogu projektu:
```bash
python3 simple_serialization.py
```
*Skrypt wyświetli punkt startowy żółwia i zacznie rejestrację wektora względnego.*

### Terminal 3: Sterowanie żółwiem (klawisze strzałek)
```bash
ros2 run turtlesim turtle_teleop_key
```

---

## 4. Opcjonalny podgląd dodatkowego topicu na żywo

W osobnym terminalu możesz sprawdzić, co nasz skrypt publikuje w czasie rzeczywistym:
```bash
ros2 topic echo /turtle1/relative_vector
```
Zobaczysz bieżący wektor przesunięcia względem pozycji początkowej:
```yaml
x: 0.452
y: 0.128
z: 0.080
```

---

## 5. Zakończenie rejestracji

W oknie Terminala 2 wciśnij **Ctrl+C**. Węzeł zakończy nasłuchiwanie i wypisze podsumowanie:

```text
Zapisano 84 próbek do vector_time
Czas: 0.0s - 4.2s
Wektor końcowy: dx=1.842, dy=0.915, dtheta=0.521
```

W katalogu zostanie utworzony binarny plik `vector_time`.
