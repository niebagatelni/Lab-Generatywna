"""Moduł uczenia klasyfikatora liniowego: dane.csv -> granica.json.

Uczenie: python model.py
Równanie granicy decyzyjnej: z = w1 * wypelnienie_prostokata + w2 * liczba_rogow + b
"""
import csv
import json
import os
import sys
import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

FOLDER = os.path.dirname(os.path.abspath(__file__))
SCIEZKA_DANYCH = os.path.join(FOLDER, "dane.csv")
SCIEZKA_GRANICY = os.path.join(FOLDER, "granica.json")
KOLUMNY = ["wypelnienie_prostokata", "liczba_rogow"]
MIN_PROBEK = 10
MIN_NA_KLASE = 3


def wczytaj_dane(sciezka=SCIEZKA_DANYCH):
    if not os.path.exists(sciezka):
        return np.empty((0, len(KOLUMNY))), np.empty(0, dtype=str)
    with open(sciezka, newline="", encoding="utf-8") as f:
        wiersze = list(csv.DictReader(f))
    if not wiersze:
        return np.empty((0, len(KOLUMNY))), np.empty(0, dtype=str)

    X = np.array([[float(w[k]) for k in KOLUMNY] for w in wiersze]).reshape(-1, len(KOLUMNY))
    y = np.array([w["etykieta"] for w in wiersze], dtype=str)
    return X, y


def dopasuj(X, y):
    model = make_pipeline(StandardScaler(), LogisticRegression(random_state=42))
    model.fit(X, y)
    skaler, regresja = model[0], model[-1]

    w = regresja.coef_[0] / skaler.scale_
    b = float(regresja.intercept_[0] - np.sum(regresja.coef_[0] * skaler.mean_ / skaler.scale_))
    klasy = [str(k) for k in regresja.classes_]

    return {
        "cechy": KOLUMNY,
        "w": [float(x) for x in w],
        "b": b,
        "klasa_ujemna": klasy[0],
        "klasa_dodatnia": klasy[1]
    }


def przewiduj(granica, X):
    z = np.asarray(X, dtype=float) @ np.array(granica["w"]) + granica["b"]
    return np.where(z > 0, granica["klasa_dodatnia"], granica["klasa_ujemna"])


def dokladnosc(granica, X, y):
    if len(y) == 0:
        return 0.0
    return float(np.mean(przewiduj(granica, X) == np.asarray(y)))


def zapisz_granice(granica, sciezka=SCIEZKA_GRANICY):
    with open(sciezka, "w", encoding="utf-8") as f:
        json.dump(granica, f, indent=2, ensure_ascii=False)


def wczytaj_granice(sciezka=SCIEZKA_GRANICY):
    try:
        with open(sciezka, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def wzor(granica):
    w1, w2 = granica["w"]
    return f"z = {w1:.2f}·wypełnienie + {w2:.2f}·rogi {granica['b']:+.2f}"


def ucz(sciezka_danych=SCIEZKA_DANYCH, sciezka_granicy=SCIEZKA_GRANICY):
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
        raise SystemExit(
            f"Za mało danych w {SCIEZKA_DANYCH} (wymagane min. {MIN_PROBEK} próbek, po {MIN_NA_KLASE} na klasę)."
        )
    print(f"Próbek: {wynik['probek']}, dokładność na zbiorze testowym: {wynik['dokladnosc']:.1%}")
    print(f"Zapisano granicę do {SCIEZKA_GRANICY}:\n  {wzor(wynik['granica'])}")
