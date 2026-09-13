# Serializacja Wektora Żółwia w Czasie (MessagePack)

Projekt demonstruje prosty, binarny zapis oraz odczyt wektora stanu robota (trajektorii 2D w czasie) za pomocą biblioteki **MessagePack** (`msgpack`).

---

## 1. O co chodzi w projekcie?

W robotyce i symulatorach (np. standardowym `turtlesim` w ROS 2) robot porusza się po dwuwymiarowej planszy. Jego stan w każdej chwili czasu $t$ opisuje wektor:
* **$t$** – znacznik czasu w sekundach,
* **$x, y$** – współrzędne pozycji robota na planszy,
* **$\theta$ (theta)** – kąt orientacji (kierunek, w którym robot jest zwrócony).

Zamiast trzymać te dane tylko w pamięci podręcznej RAM (skąd zniknęłyby po wyłączeniu programu), program przeprowadza **serializację**, czyli pakuje całą trajektorię do jednego, zwartego pliku binarnego o nazwie `vector_time`.

---

## 2. Pojęcia: Serializacja i Deserializacja

* **Serializacja (zapis)**: Proces konwersji złożonej struktury Pythona (słownika zawierającego listy liczb) na ciąg surowych bajtów, który można zapisać na dysku.
* **Deserializacja (odczyt)**: Proces odwrotny – wczytanie bajtów z pliku i natychmiastowe odtworzenie identycznego słownika w pamięci programu.
* **Dlaczego MessagePack (`msgpack`)?**: W odróżnieniu od formatów tekstowych takich jak JSON czy CSV, MessagePack zapisuje liczby bezpośrednio binarnie. Dzięki temu plik jest mniejszy, zapis i odczyt są znacznie szybsze, a liczby zmiennoprzecinkowe zachowują pełną precyzję bez zaokrągleń tekstowych.

---

## 3. Szczegółowe omówienie kodu `simple_serialization.py`

Skrypt składa się z czterech zwięzłych funkcji:

### `save_data(path, data)`
```python
def save_data(path, data):
    with open(path, "wb") as f:
        msgpack.pack(data, f)
```
* Otwiera plik pod wskazaną ścieżką w trybie binarnym do zapisu (`"wb"` – *write bytes*).
* Funkcja `msgpack.pack(data, f)` bezpośrednio strumieniuje obiekt Pythona do pliku w postaci binarnej.

---

### `load_data(path)`
```python
def load_data(path):
    with open(path, "rb") as f:
        return msgpack.unpack(f)
```
* Otwiera plik w trybie binarnym do odczytu (`"rb"` – *read bytes*).
* Funkcja `msgpack.unpack(f)` odczytuje strumień bajtów i odtwarza z niego oryginalny słownik Pythona wraz ze wszystkimi listami.

---

### `generate_turtle_data(steps=50, dt=0.1)`
```python
def generate_turtle_data(steps=50, dt=0.1):
    ...
```
* Generuje syntetyczny ruch robota na planszy:
  * Początek w punkcie $(5.5, 5.5)$ – jest to geometryczny środek planszy $11 \times 11$ znany z symulatora `turtlesim`.
  * W każdej z 50 iteracji (co $0.1$ s) robot przesuwa się do przodu o krok $0.1 \cdot \cos(\theta)$ w osi $X$ oraz $0.1 \cdot \sin(\theta)$ w osi $Y$, jednocześnie delikatnie skręcając ($\theta += 0.05$ rad).
* Zwraca słownik o strukturze:
  ```python
  {
      "turtle_name": "turtle1",
      "time": [0.0, 0.1, 0.2, ...],
      "x": [5.6, 5.7, ...],
      "y": [5.5, 5.51, ...],
      "theta": [0.05, 0.1, ...]
  }
  ```

---

### `main()`
```python
def main():
    folder = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(folder, "vector_time")
    ...
```
1. Wyznacza bezwzględną ścieżkę do pliku `vector_time` w folderze skryptu (dzięki temu program działa poprawnie niezależnie od tego, z jakiej lokalizacji zostanie uruchomiony w terminalu).
2. Generuje trajektorię żółwia przez `generate_turtle_data()`.
3. Zapisuje dane do pliku binarnego `vector_time` przez `save_data()`.
4. Wczytuje dane z pliku przez `load_data()` i drukuje podsumowanie: liczbę próbek, zakres czasu oraz pozycję startową i końcową.

---

## 4. Uruchomienie programu

Wymagania: zainstalowany pakiet `msgpack` (`pip install msgpack`).

Uruchomienie w terminalu:
```bash
python3 simple_serialization.py
```

### Oczekiwany wynik w konsoli:
```text
Zapisano 50 próbek do vector_time
Wczytano obiekt: turtle1
Czas: 0.0s - 4.9s
Start: x=5.6, y=5.5
Koniec: x=6.787, y=9.072
```

Po wykonaniu w katalogu pojawi się plik binarny `vector_time` o rozmiarze ok. 1.8 KB zawierający spakowany wektor ruchu robota.
