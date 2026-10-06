"""Program rozpoznający: rysujesz figurę, a program mówi "KOŁO" albo "KWADRAT".

Używa wyłącznie granicy z granica.json - bez scikit-learn.
Działa niezawodnie także dla spłaszczonych kół (elips) oraz zniekształconych kwadratów.
"""
import json
import math
import os
import sys
import tkinter as tk
import numpy as np
from PIL import Image, ImageDraw

from cechy import GRUBOSC, cechy

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROZMIAR = 350
SCIEZKA_GRANICY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "granica.json")


def wczytaj_granice(sciezka=SCIEZKA_GRANICY):
    with open(sciezka, encoding="utf-8") as f:
        return json.load(f)


def klasyfikuj(granica, wypelnienie, rogi):
    """z = w1 * wypelnienie + w2 * rogi + b.
    z > 0 -> klasa_dodatnia (kwadrat), z <= 0 -> klasa_ujemna (kolo).
    """
    w1, w2 = granica["w"]
    z = w1 * wypelnienie + w2 * rogi + granica["b"]
    pewnosc = 1.0 / (1.0 + math.exp(-abs(z)))
    etykieta = granica["klasa_dodatnia"] if z > 0 else granica["klasa_ujemna"]
    return etykieta, pewnosc, z


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
        tk.Button(panel, text="Wyczyść", command=self.wyczysc).grid(row=0, column=0, padx=4)
        tk.Button(panel, text="Rozpoznaj", command=self.rozpoznaj).grid(row=0, column=1, padx=4)

        self.status = tk.Label(root, width=54, wraplength=380, justify="center")
        self.status.pack(pady=(0, 10))

        try:
            self.granica = wczytaj_granice()
            self.nowy_rysunek("Narysuj figurę i kliknij 'Rozpoznaj'.")
        except (OSError, ValueError, KeyError):
            self.granica = None
            self.nowy_rysunek("Brak granica.json - najpierw uruchom model.py.")

    def nowy_rysunek(self, komunikat):
        self.canvas.delete("all")
        self.obraz = Image.new("L", (ROZMIAR, ROZMIAR), 0)
        self.rysik = ImageDraw.Draw(self.obraz)
        self.punkty = []
        self.status.config(text=komunikat)

    def wyczysc(self):
        msg = "Narysuj figurę i kliknij 'Rozpoznaj'." if self.granica else "Brak granica.json - uruchom model.py."
        self.nowy_rysunek(msg)

    def linia(self, a, b):
        self.canvas.create_line(*a, *b, width=GRUBOSC, capstyle=tk.ROUND)
        self.rysik.line([a, b], fill=255, width=GRUBOSC)

    def start(self, e):
        self.punkty = [(e.x, e.y)]

    def ruch(self, e):
        p = (e.x, e.y)
        self.linia(self.punkty[-1], p)
        self.punkty.append(p)

    def koniec(self, _):
        if len(self.punkty) > 1:
            self.linia(self.punkty[-1], self.punkty[0])

    def rozpoznaj(self):
        if self.granica is None:
            self.status.config(text="Brak granica.json - najpierw uruchom model.py.")
            return
        if len(self.punkty) < 2:
            self.status.config(text="Najpierw narysuj figurę.")
            return

        try:
            wyp, rogi = cechy(self.obraz)
        except ValueError as err:
            self.status.config(text=f"Błąd: {err}")
            return

        etykieta, pewnosc, z = klasyfikuj(self.granica, wyp, rogi)
        nazwa = {"kolo": "KOŁO", "kwadrat": "KWADRAT"}.get(etykieta, etykieta.upper())
        self.status.config(
            text=f"To {nazwa} (pewność: {pewnosc:.1%})\n[wypełnienie: {wyp:.3f}, rogi: {rogi:.0f}, z: {z:+.2f}]"
        )


if __name__ == "__main__":
    root = tk.Tk()
    Aplikacja(root)
    root.mainloop()
