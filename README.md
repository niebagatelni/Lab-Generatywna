# Klasyfikator Kształtów (Koło vs Kwadrat) — Wariant 2

Projekt łączy najlepsze cechy głębokich sieci neuronowych (odporność na niedoskonałości odręcznego rysunku, drżenie ręki i zniekształcenia) z lekkością klasycznego uczenia maszynowego (plik modelu JSON ważący poniżej 1 KB, brak zależności od TensorFlow, błyskawiczne douczanie w locie z poziomu GUI).

---

## 🛠 Wymagania i Instalacja

Program wymaga środowiska Python 3.10+ oraz kilku podstawowych bibliotek:

```bash
pip install opencv-python scikit-learn matplotlib pillow numpy
```

---

## 🚀 Jak używać programu?

### 1. Aplikacja Główna (Active Learning GUI)
Główny interfejs z możliwością rysowania, rozpoznawania oraz douczania modelu:

```bash
python main.py
```

**Dostępne przyciski:**
* **Rozpoznaj** — sprawdza narysowaną figurę, wyświetla rozpoznaną klasę (`KOŁO` / `KWADRAT`), procentową pewność oraz wartości wyliczonych cech.
* **To koło / To kwadrat** — zapisuje Twój odręczny rysunek do bazy `dane.csv` i natychmiast przelicza model w locie (*Active Learning*), adaptując granicę do Twojego stylu rysowania.
* **Generuj 50+50 próbek** — generuje w pamięci RAM realistyczne odręczne figury z losowym szumem i natychmiast doucza model.
* **Wyczyść** — czyści płótno do nowego rysunku.

---

### 2. Szybkie Rozpoznawanie (Lekka inferencja)
Minimalistyczny program służący wyłącznie do rozpoznawania (czyta wagi z `granica.json` bez użycia biblioteki `scikit-learn`):

```bash
python rozpoznaj.py
```

---

### 3. Animacja Uczenia i Granica Decyzyjna 2D
Wizualizuje przestrzeń cech 2D oraz dynamicznie przerysowuje linię granicy decyzyjnej w miarę dokładania kolejnych punktów:

```bash
python wykres.py
```

* Opcjonalnie: `python wykres.py dane.csv 0.05` (określenie pliku i interwału animacji w sekundach).
* Końcowy stan wykresu zapisywany jest do pliku `wykres.png`.

---

### 4. Narzędzia Konsolowe
* **Generowanie danych syntetycznych**:
  ```bash
  python generuj.py 50
  ```
  *(Generuje 50 kół i 50 kwadratów bezpośrednio do pliku `dane.csv`)*.

* **Trening modelu z konsoli**:
  ```bash
  python model.py
  ```
  *(Trenuje regresję logistyczną, wyznacza dokładność na odłożonym zbiorze testowym 20% i zapisuje wagi do `granica.json`)*.

---

## 🧠 Jak to działa pod spodem?

Zamiast przekazywać surowe piksele do ciężkiej sieci neuronowej, rysunek sprowadzany jest do dwóch niezmienniczych cech geometrycznych:

1. **Kolistość izoperymetryczna ($\text{Circularity}$)**:
   $$\text{Kolistość} = \frac{4 \cdot \pi \cdot \text{Pole}}{\text{Obwód}^2}$$
   * Dla idealnego koła: $1.0$ (dla odręcznego: $\approx 0.90 - 0.99$).
   * Dla kwadratu: $\frac{\pi}{4} \approx 0.785$ (dla odręcznego: $\approx 0.70 - 0.83$).
2. **Liczba wykrytych rogów / wierzchołków ($\text{approxPolyDP}$)**:
   * Wyznaczana z otoczki wypukłej konturu (`Convex Hull`).
   * Dla kwadratu: regularnie **4**.
   * Dla koła: **6 – 16** (brak kątów prostych).

Decyzja podejmowana jest za pomocą równania liniowego zapisanego w `granica.json`:
$$z = w_1 \cdot \text{kolistość} + w_2 \cdot \text{rogi} + b$$
Jeśli $z > 0$, figura to **Kwadrat**, w przeciwnym razie **Koło**.
Pewność obliczana jest z funkcji sigmoidalnej odległości od granicy.
