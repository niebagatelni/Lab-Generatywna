# Klasyfikator Ksztaltow: Kolo czy Kwadrat

Lekki klasyfikator ksztaltow geometrycznych rysowanych odrecznie. Zamiast ciezkich sieci neuronowych projekt wykorzystuje analize konturow (OpenCV) oraz model regresji liniowej zapisany w pliku JSON (< 1 KB).

## Wymagania

Wymagany Python 3.10+ oraz biblioteki:

```bash
pip install opencv-python scikit-learn matplotlib pillow numpy
```

## Szybki start

### 1. Aplikacja glowna (GUI)
Uruchomienie glownego okna programu z mozliwoscia rysowania i douczania:

```bash
python main.py
```

Opis przyciskow w aplikacji:
- Rozpoznaj: klasyfikuje narysowany ksztalt jako KOLO lub KWADRAT i wyswietla pewnosc w procentach.
- To kolo / To kwadrat: zapisuje Twoj rysunek z podana etykieta i natychmiast doucza model w czasie rzeczywistym.
- Generuj 50+50 probek: generuje w locie nowe syntetyczne figury i aktualizuje model.
- Wyczysc: resetuje plotno.

### 2. Samodzielne rozpoznawanie (lekka inferencja)
Minimalistyczny program tylko do sprawdzania rysunkow (uzywa wylacznie pliku granica.json, bez biblioteki scikit-learn):

```bash
python rozpoznaj.py
```

### 3. Wizualizacja i animacja granicy 2D
Animowane przedstawienie przestrzeni cech oraz wyznaczonej prostej decyzyjnej:

```bash
python wykres.py
```

Wykres koncowy jest rowniez zapisywany do pliku wykres.png.

### 4. Skrypty konsolowe
- Generowanie syntetycznych danych do dane.csv:
  ```bash
  python generuj.py 300
  ```
- Trening modelu liniowego i aktualizacja granica.json:
  ```bash
  python model.py
  ```

## Jak dziala model

Kazdy rysunek jest sprowadzany do dwoch cech geometrycznych:
1. Wypelnienie minimalnego prostokata otaczajacego (stosunek pola otoczki wypuklej do pola prostokata zorientowanego):
   Dla kola wynosi zawsze okolo 0.785 (pi/4), a dla kwadratu okolo 0.90 - 1.0.
2. Liczba wierzcholkow wielokata (approxPolyDP):
   Dla kwadratu regularnie 4, dla kola 6 - 16.

Decyzja podejmowana jest z rownania liniowego w granica.json:
z = w1 * wypelnienie + w2 * rogi + b
Wartosc z > 0 oznacza kwadrat, a z <= 0 oznacza kolo.
