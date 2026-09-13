# Serializacja wektora żółwia w czasie (MessagePack)

Projekt binarnego zapisu i odczytu parametrów kinematycznych robota (czas, pozycja x, y, orientacja theta) za pomocą biblioteki `msgpack`.

## Uruchomienie

```bash
python3 simple_serialization.py
```

## Działanie

Skrypt generuje próbki trajektorii i zapisuje je bezpośrednio do pliku binarnego `vector_time`, a następnie wczytuje i wyświetla odtworzone parametry.
