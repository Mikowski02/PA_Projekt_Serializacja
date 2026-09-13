# ROS2 Telemetry Recorder & Plotter

Projekt zaliczeniowy z przedmiotu **„Automatyzacja procesów projektowania z wykorzystaniem Pythona”** (dr Stanisław Gepner, Politechnika Warszawska).

System akwizycji, binarnej serializacji (`msgpack` + bufor numeryczny `numpy`) oraz wizualizacji trajektorii robota (`matplotlib`).

---

## Struktura plików

- `telemetry_recorder.py` – Węzeł ROS2 subskrybujący `/odom` i zapisujący trajektorię do `trajectory_data.dat` przy użyciu `msgpack.ExtType(code=1)`.
- `telemetry_plotter.py` – Autonomiczny skrypt (bez zależności od ROS2) deserializujący dane binarne (`np.frombuffer`) i generujący wykres 2D trajektorii $y(x)$.

---

## Instrukcja uruchomienia i testowania całego potoku

### Krok 1: Uruchomienie rejestratora danych
W pierwszym terminalu przejdź do folderu projektu i uruchom węzeł rejestratora:
```bash
python3 telemetry_recorder.py "Eksperyment Ground Truth - Test przeszkod"
```

### Krok 2: Generowanie przykładowego ruchu na topicu `/odom`
W drugim terminalu możesz opublikować testowe komunikaty odometrii za pomocą narzędzia `ros2 topic pub` (lub uruchomić węzeł symulacji / robota):
```bash
# Publikacja przykładowego punktu (można wywołać wielokrotnie ze zmienionymi współrzędnymi X i Y):
ros2 topic pub -r 10 /odom nav_msgs/msg/Odometry "{header: {frame_id: 'odom'}, child_frame_id: 'base_link', pose: {pose: {position: {x: 1.0, y: 0.5, z: 0.0}}}}"
```

### Krok 3: Zakończenie nagrywania
W oknie pierwszego terminala wciśnij **Ctrl+C** (`KeyboardInterrupt`). Węzeł przechwyci sygnał i bezpiecznie zrzuci bufor do pliku binarnego `trajectory_data.dat`.

### Krok 4: Wizualizacja trajektorii
W dowolnym środowisku z zainstalowanym `numpy`, `msgpack` oraz `matplotlib` (nie wymaga ROS2):
```bash
python3 telemetry_plotter.py
```
Zostanie wyświetlony wykres z siatką (`plt.grid()`), oznaczeniem punktu początkowego i końcowego, zachowaniem proporcji osi (`plt.axis('equal')`) oraz tytułem zawierającym opis sesji i datę.
