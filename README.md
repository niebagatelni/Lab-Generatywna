# Klasyfikator Kształtów (Koło/Elipsa vs Kwadrat) — Wariant 2

Projekt łączy najlepsze cechy głębokich sieci neuronowych (odporność na niedoskonałości odręcznego rysunku, spłaszczone elipsy, drżenie ręki i zniekształcenia) z lekkością klasycznego uczenia maszynowego (plik modelu JSON ważący poniżej 1 KB, brak zależności od TensorFlow, błyskawiczne douczanie w locie z poziomu GUI).

---

## 🛠 Wymagania i Instalacja

Program wymaga środowiska Python 3.10+ oraz bibliotek:

```bash
pip install opencv-python scikit-learn matplotlib pillow numpy
```

---

## 🚀 Jak używać programu?

### 1. Aplikacja Główna (Active Learning GUI)
Główny interfejs z możliwością rysowania, natychmiastowego rozpoznawania oraz douczania modelu:

```bash
python main.py
```

**Dostępne przyciski:**
* **Rozpoznaj** — sprawdza narysowaną figurę, wyświetla rozpoznaną klasę (`KOŁO / ELIPSA` lub `KWADRAT`), procentową pewność oraz wartości cech na żywo.
* **To koło / To kwadrat** — zapisuje Twój odręczny rysunek do bazy `dane.csv` i natychmiast przelicza model w locie (*Active Learning*), adaptując granicę do Twojego stylu rysowania.
* **Generuj 50+50 próbek** — generuje w pamięci RAM realistyczne odręczne figury (w tym spłaszczone elipsy i zniekształcone kwadraty) i natychmiast doucza model.
* **Wyczyść** — czyści płótno do nowego rysunku.

---

### 2. Szybkie Rozpoznawanie (Lekka inferencja)
Minimalistyczny program służący wyłącznie do rozpoznawania (czyta wagi z `granica.json` bez użycia biblioteki `scikit-learn`):

```bash
python rozpoznaj.py
```

---

### 3. Animacja Uczenia i Granica Decyzyjna 2D
Wizualizuje przestrzeń cech 2D oraz dynamicznie przerysowuje linię granicy decyzyjnej w miarę dokładania kolejnych próbek:

```bash
python wykres.py
```

* Opcjonalnie: `python wykres.py dane.csv 0.04` (określenie pliku i interwału animacji w sekundach).
* Końcowy stan wykresu zapisywany jest do pliku `wykres.png`.

---

### 4. Narzędzia Konsolowe
* **Generowanie danych syntetycznych**:
  ```bash
  python generuj.py 300
  ```
  *(Generuje 300 kół/elips i 300 kwadratów bezpośrednio do pliku `dane.csv`)*.

* **Trening modelu z konsoli**:
  ```bash
  python model.py
  ```
  *(Trenuje model liniowy na danych z `dane.csv` i zapisuje wagi do `granica.json`)*.

---

## 🧠 Jak to działa pod spodem?

Zamiast polegać na podatnym na zniekształcenia promieniu, program analizuje kształt za pomocą dwóch potężnych niezmienników geometrycznych:

1. **Wypełnienie minimalnego prostokąta otaczającego ($\text{Box Ratio}$)**:
   $$\text{Wypełnienie} = \frac{\text{Pole otoczki}}{\text{Pole minimalnego prostokąta zorientowanego (minAreaRect)}}$$
   * **Niezmiennik geometrii euklidesowej**: Dla koła oraz dla **KAŻDEJ elipsy** (niezależnie od tego, jak mocno jest spłaszczona lub obrócona) pole wynosi $\pi a b$, a pole jej prostokąta otaczającego to $4 a b$. Stosunek ten wynosi ZAWSZE $\frac{\pi}{4} \approx 0.785$! W odręcznym rysunku: $\approx 0.75 - 0.81$.
   * Dla kwadratu i prostokąta wynosi teoretycznie $1.0$ (w rysunku odręcznym: $\approx 0.88 - 0.98$).
   * Dzięki temu **nawet mocno jajowate elipsy nigdy nie są mylone z kwadratami**.
2. **Liczba wykrytych wierzchołków ($\text{approxPolyDP}$)**:
   * Wyznaczana z otoczki wypukłej (`Convex Hull`).
   * Dla kwadratu: stabilnie **4** wierzchołki.
   * Dla koła / elipsy: **6 – 16** wierzchołków (łuki i krzywizny nie zapadają się do 4 kątów prostych).

Decyzja podejmowana jest za pomocą równania liniowego zapisanego w `granica.json`:
$$z = w_1 \cdot \text{wypełnienie} + w_2 \cdot \text{rogi} + b$$
Jeśli $z > 0$, figura to **Kwadrat**, w przeciwnym razie **Koło / Elipsa**.
Pewność obliczana jest z funkcji sigmoidalnej odległości od granicy.
