Dużo nie zmieniłem, dodałem coś podobnego do tego jak ja trenowałem mój model - czyli wobble + rotacja. Działa, wygenerowałem dużo rzeczy i trochę poduczyłem i powinno działać.

## Wymagania

Wymagane biblioteki:

```bash
pip install opencv-python scikit-learn matplotlib pillow numpy
```

### 1. Główna aplikacja 
Rysowanie i douczanie

```bash
python main.py
```

Opis przyciskow w aplikacji:
- Rozpoznaj: klasyfikuje narysowany ksztalt jako KOLO lub KWADRAT i wyswietla pewnosc w procentach.
- To kolo / To kwadrat: zapisuje Twoj rysunek z podana etykieta i natychmiast doucza model w czasie rzeczywistym.
- Generuj 50+50 probek: generuje w locie nowe syntetyczne figury i aktualizuje model.
- Wyczysc: resetuje płótno.

### 2. Wizualizacja i animacja granicy 2D
Animowane przedstawienie przestrzeni cech oraz wyznaczonej prostej decyzyjnej:

```bash
python wykres.py
```

Wykres koncowy jest rowniez zapisywany do pliku wykres.png.

### 3. Skrypty konsolowe
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
