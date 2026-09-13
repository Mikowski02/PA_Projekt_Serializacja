# Akwizycja, Binarna Serializacja i Repetycja Trajektorii Planarnej w ROS 2

Moduł do rejestracji, relatywizacji przestrzennej oraz odtwarzania wektora stanu robota kołowego na płaszczyźnie $SE(2)$ w środowisku ROS 2 z wykorzystaniem binarnego formatu MessagePack.

---

## 1. Model Kinematyczny i Relatywizacja Przestrzenna

Stan kinematyczny robota mobilnego na płaszczyźnie opisany jest wektorem w przestrzeni konfiguracyjnej:
$$\mathbf{q}(t) = \begin{bmatrix} x(t) \\ y(t) \\ \theta(t) \end{bmatrix} \in SE(2)$$

W celach uniezależnienia rejestracji od globalnego punktu startowego symulatora (np. arbitralnej pozycji początkowej w `turtlesim`), węzeł dokonuje transformacji do lokalnego układu odniesienia związanego ze stanem początkowym $\mathbf{q}_0 = \mathbf{q}(t_0)$:
$$\Delta x(t) = x(t) - x_0, \quad \Delta y(t) = y(t) - y_0, \quad \Delta \theta(t) = \theta(t) - \theta_0$$
Punkt początkowy w chwili $t_0$ definiuje bazę $\Delta \mathbf{q}(t_0) = [0, 0, 0]^T$.

---

## 2. Architektura Systemu i Analiza Przepływu Danych

Projekt został rozdzielony na dwa ortogonalne węzły ROS 2:

```text
[ turtlesim_node ] ---> Topic: /turtle1/pose ---> [ turtle_recorder.py ] ---> Topic: /turtle1/relative_vector
                                                            |
                                                 (Ctrl+C: zrzut do pliku)
                                                            v
                                                   Plik: vector_time
                                                            |
                                                 (Odczyt i deserializacja)
                                                            v
[ turtlesim_node ] <--- Topic: /turtle1/cmd_vel <--- [ turtle_player.py ] ---> Topic: /turtle1/target_vector
```

### 2.1. Węzeł 1: `turtle_recorder.py` (Rejestrator / Topic Akwizycji)
* **Topic wejściowy**: `/turtle1/pose` (`turtlesim/msg/Pose`, częstotliwość $\approx 62.5\text{ Hz}$).
* **Topic wyjściowy (czas rzeczywisty)**: `/turtle1/relative_vector` (`geometry_msgs/msg/Vector3`). Publikuje na bieżąco wektor przemieszczenia $[\Delta x, \Delta y, \Delta \theta]^T$.
* **Dynamika czasowa i mechanizm zapisu**:
  * **Buforowanie w RAM**: Próbki trajektorii wraz ze stemplem czasowym $\Delta t = t - t_0$ oraz wektorem prędkości $[v, \omega]^T$ są buforowane w pamięci operacyjnej ($O(1)$ amortized append). Bezpośredni zapis strumieniowy do pamięci dyskowej w pętli zwrotnej wprowadzałby niedeterministyczny narzut czasowy (I/O latency jitter), zakłócając synchronizację próbkowania.
  * **Zrzut binarny**: Zrzut do pliku `vector_time` następuje po przechwyceniu sygnału przerwania procesu (`SIGINT` / Ctrl+C). Cała struktura jest serializowana jednorazowo funkcją `msgpack.pack()`, co ogranicza operację I/O do pojedynczego zapisu sekwencyjnego o złożoności $O(N)$.

### 2.2. Węzeł 2: `turtle_player.py` (Odtwarzacz / Topic Sterowania)
* **Deserializacja**: Odczytuje plik `vector_time` metodą `msgpack.unpack()`, rekonstruując macierz trajektorii.
* **Topic referencyjny**: `/turtle1/target_vector` (`geometry_msgs/msg/Vector3`) – publikuje aktualnie zadany punkt wektora przemieszczenia.
* **Topic wykonawczy**: `/turtle1/cmd_vel` (`geometry_msgs/msg/Twist`) – generator sygnałów sterujących przesyła w pętli timera o zadanym kroku $\Delta t$ prędkości liniowe $v(t)$ i kątowe $\omega(t)$ bezpośrednio do sterownika robota.
* **Zakończenie trajektorii**: Po wyczerpaniu zadanego profilu węzeł publikuje zerowy wektor prędkości ($v=0, \omega=0$) i zamyka kontekst wykonawczy.

---

## 3. Efektywność Formatowania Binarnego

Zastosowanie formatu MessagePack eliminuje narzut formatów tekstowych (JSON, CSV):
* **Zachowanie precyzji numerycznej**: Zmienne zmiennoprzecinkowe reprezentowane są w standardzie IEEE 754 bez błędów konwersji tekstowej i zaokrągleń.
* **Kompaktowość**: Rozmiar pliku wynikowego jest zredukowany o ok. 20–40% w stosunku do reprezentacji tekstowej.
* **Złożoność obliczeniowa**: Brak parsowania leksykalnego przy deserializacji umożliwia natychmiastowe odtworzenie profilu ruchu.

---

## 4. Weryfikacja Doświadczalna

### Etap 1: Rejestracja trajektorii
```bash
# Terminal 1: Węzeł symulatora
ros2 run turtlesim turtlesim_node

# Terminal 2: Akwizycja i relatywizacja
python3 turtle_recorder.py

# Terminal 3: Sterowanie manualne (zadawanie ruchu)
ros2 run turtlesim turtle_teleop_key
```
*Po wykonaniu manewru wciśnij Ctrl+C w Terminalu 2, generując plik `vector_time`.*

### Etap 2: Podgląd topicu wektora na żywo (opcjonalnie)
```bash
# Terminal 4: Monitorowanie względnego wektora ruchu
ros2 topic echo /turtle1/relative_vector
```

### Etap 3: Repetycja trajektorii
W celu powtórzenia zarejestrowanego profilu ruchu:
```bash
python3 turtle_player.py
```
*Żółw odtworzy zarejestrowaną sekwencję kinematyczną, a na topicu `/turtle1/target_vector` publikowany będzie aktualny wektor zadany.*
