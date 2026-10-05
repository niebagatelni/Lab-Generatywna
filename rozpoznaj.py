"""Program 2: rysujesz figurę, a program mówi "koło" albo "kwadrat".

Używa tylko granicy z granica.json (wyliczonej przez model.py) - bez scikit-learn.
Najpierw uruchom model.py, żeby powstał plik granica.json.
"""
import json
import math
import os
import tkinter as tk

import numpy as np
from PIL import Image, ImageDraw

from cechy import GRUBOSC, cechy

ROZMIAR = 300
SCIEZKA_GRANICY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "granica.json")


def wczytaj_granice(sciezka=SCIEZKA_GRANICY):
    with open(sciezka, encoding="utf-8") as f:
        return json.load(f)


def klasyfikuj(granica, cv, rozpietosc_p):
    """z = w1*cv + w2*rozpietosc_p + b. z > 0 -> klasa dodatnia, inaczej ujemna.
    Pewność = sigmoida z (im dalej od granicy, tym pewniej). Zwraca (etykieta, pewnosc, z)."""
    w1, w2 = granica["w"]
    z = w1 * cv + w2 * rozpietosc_p + granica["b"]
    p_dodatnia = 1 / (1 + math.exp(-z))
    if z > 0:
        return granica["klasa_dodatnia"], p_dodatnia, z
    return granica["klasa_ujemna"], 1 - p_dodatnia, z


class Aplikacja:
    def __init__(self, root):
        self.root = root
        root.title("Rozpoznawanie: koło czy kwadrat")

        self.canvas = tk.Canvas(root, width=ROZMIAR, height=ROZMIAR, bg="white",
                                highlightthickness=1, highlightbackground="black")
        self.canvas.pack(padx=10, pady=10)
        self.canvas.bind("<ButtonPress-1>", self.start)
        self.canvas.bind("<B1-Motion>", self.ruch)
        self.canvas.bind("<ButtonRelease-1>", self.koniec)

        panel = tk.Frame(root)
        panel.pack(pady=(0, 5))
        tk.Button(panel, text="Wyczyść", command=self.wyczysc).grid(row=0, column=0, padx=3)
        tk.Button(panel, text="Rozpoznaj", command=self.rozpoznaj).grid(row=0, column=1, padx=3)

        self.status = tk.Label(root, width=48)
        self.status.pack(pady=(0, 10))

        try:
            self.granica = wczytaj_granice()
            self.nowy_rysunek("Narysuj figurę.")
        except (OSError, ValueError, KeyError):
            self.granica = None
            self.nowy_rysunek("Brak granica.json - najpierw uruchom model.py.")

    def nowy_rysunek(self, komunikat):
        self.canvas.delete("all")
        self.obraz = Image.new("1", (ROZMIAR, ROZMIAR), 0)
        self.rysik = ImageDraw.Draw(self.obraz)
        self.punkty = []
        self.domkniety = False
        self.status.config(text=komunikat)

    def wyczysc(self):
        self.nowy_rysunek("Narysuj figurę." if self.granica else "Brak granica.json - najpierw uruchom model.py.")

    def linia(self, a, b):
        self.canvas.create_line(*a, *b, width=GRUBOSC, capstyle=tk.ROUND)
        self.rysik.line([a, b], fill=1, width=GRUBOSC)

    def start(self, e):
        if self.domkniety:  # nowe pociągnięcie po skończonej figurze czyści płótno
            self.wyczysc()
        self.punkty = [(e.x, e.y)]

    def ruch(self, e):
        p = (e.x, e.y)
        self.linia(self.punkty[-1], p)
        self.punkty.append(p)

    def koniec(self, _):
        if len(self.punkty) > 1:
            self.linia(self.punkty[-1], self.punkty[0])  # domknięcie obrysu
            self.domkniety = True

    def rozpoznaj(self):
        if self.granica is None:
            self.status.config(text="Brak granica.json - najpierw uruchom model.py.")
            return
        if not self.domkniety:
            self.status.config(text="Najpierw narysuj figurę.")
            return
        try:
            cv, rozp = cechy(np.array(self.obraz, dtype=bool))
        except ValueError as err:
            self.status.config(text=f"Błąd: {err}")
            return
        etykieta, pewnosc, z = klasyfikuj(self.granica, cv, rozp)
        nazwa = {"kolo": "KOŁO", "kwadrat": "KWADRAT"}.get(etykieta, etykieta)
        self.status.config(text=f"To {nazwa} (pewność {pewnosc:.0%})  [cv {cv:.3f}, rozp_p {rozp:.2f}, z {z:+.2f}]")


if __name__ == "__main__":
    root = tk.Tk()
    Aplikacja(root)
    root.mainloop()
