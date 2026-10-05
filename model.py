"""Uczenie: dane.csv -> granica decyzyjna zapisana w granica.json.

Użycie z konsoli: python model.py
(program rozpoznający czyta tylko granica.json, nie potrzebuje scikit-learn)
"""
import csv
import json
import os

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

FOLDER = os.path.dirname(os.path.abspath(__file__))
SCIEZKA_DANYCH = os.path.join(FOLDER, "dane.csv")
SCIEZKA_GRANICY = os.path.join(FOLDER, "granica.json")
KOLUMNY = ["cv_promienia", "rozpietosc_p"]
MIN_PROBEK = 10   # tyle danych potrzeba, żeby uczyć
MIN_NA_KLASE = 3  # i tyle przykładów każdej figury


def wczytaj_dane(sciezka=SCIEZKA_DANYCH):
    if not os.path.exists(sciezka):
        return np.empty((0, len(KOLUMNY))), np.empty(0, dtype=str)
    with open(sciezka, newline="", encoding="utf-8") as f:
        wiersze = list(csv.DictReader(f))
    X = np.array([[float(w[k]) for k in KOLUMNY] for w in wiersze]).reshape(-1, len(KOLUMNY))
    y = np.array([w["etykieta"] for w in wiersze], dtype=str)
    return X, y


def dopasuj(X, y):
    """Uczy regresję logistyczną i zwraca granicę jako wzór na surowych cechach:
    z = w1*cv_promienia + w2*rozpietosc_p + b;  z > 0 -> klasa dodatnia (kwadrat), z <= 0 -> ujemna (koło).
    Skaler i regresję łączymy w jedne wagi dla nieprzeskalowanych cech."""
    # skalowanie cech: bez niego regularyzacja spłaszcza pewność do ok. 50%
    model = make_pipeline(StandardScaler(), LogisticRegression())
    model.fit(X, y)
    skaler, regresja = model[0], model[-1]
    w = regresja.coef_[0] / skaler.scale_
    b = float(regresja.intercept_[0] - np.sum(regresja.coef_[0] * skaler.mean_ / skaler.scale_))
    klasy = [str(k) for k in regresja.classes_]
    return {"cechy": KOLUMNY, "w": [float(x) for x in w], "b": b,
            "klasa_ujemna": klasy[0], "klasa_dodatnia": klasy[1]}


def przewiduj(granica, X):
    z = np.asarray(X, dtype=float) @ np.array(granica["w"]) + granica["b"]
    return np.where(z > 0, granica["klasa_dodatnia"], granica["klasa_ujemna"])


def dokladnosc(granica, X, y):
    return float(np.mean(przewiduj(granica, X) == np.asarray(y)))


def zapisz_granice(granica, sciezka=SCIEZKA_GRANICY):
    with open(sciezka, "w", encoding="utf-8") as f:
        json.dump(granica, f, indent=2, ensure_ascii=False)


def wczytaj_granice(sciezka=SCIEZKA_GRANICY):
    """Zwraca granicę z pliku albo None, gdy pliku nie ma lub jest uszkodzony."""
    try:
        with open(sciezka, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def wzor(granica):
    w1, w2 = granica["w"]
    return f"z = {w1:.2f}·cv + {w2:.2f}·rozp {granica['b']:+.2f}"


def ucz(sciezka_danych=SCIEZKA_DANYCH, sciezka_granicy=SCIEZKA_GRANICY):
    """Uczy na całym CSV i zapisuje granicę. Dokładność liczona na 20% danych odłożonych
    na bok (granica z tej części nie widziała), a zapisana granica uczy się na wszystkim.
    Zwraca słownik z wynikiem albo None, gdy danych jest za mało."""
    X, y = wczytaj_dane(sciezka_danych)
    if len(y) < MIN_PROBEK or min((y == "kolo").sum(), (y == "kwadrat").sum()) < MIN_NA_KLASE:
        return None
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    dokl = dokladnosc(dopasuj(X_tr, y_tr), X_te, y_te)
    granica = dopasuj(X, y)
    zapisz_granice(granica, sciezka_granicy)
    return {"granica": granica, "probek": len(y), "dokladnosc": dokl}


if __name__ == "__main__":
    wynik = ucz()
    if wynik is None:
        raise SystemExit(f"Za mało danych w {SCIEZKA_DANYCH} (min. {MIN_PROBEK} próbek, po {MIN_NA_KLASE} każdej figury).")
    print(f"Próbek: {wynik['probek']}, dokładność na danych testowych: {wynik['dokladnosc']:.1%}")
    print(f"Zapisano granicę: {SCIEZKA_GRANICY}\n  {wzor(wynik['granica'])}")
