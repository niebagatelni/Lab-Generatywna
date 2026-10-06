"""Aplikacja główna z pętlą aktywnego uczenia (Active Learning).
Pozwala rysować figury, rozpoznawać je na żywo, a także oznaczać i douczać model w czasie rzeczywistym.
Doskonale radzi sobie z kołami, mocno spłaszczonymi elipsami i zniekształconymi kwadratami.
"""
import csv
import math
import os
import sys
import tkinter as tk
import numpy as np
from PIL import Image, ImageDraw

import generuj as gen
import model as m
from cechy import GRUBOSC, cechy

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROZMIAR = 350


class AplikacjaGlowna:
    def __init__(self, root):
        self.root = root
        root.title("Klasyfikator: Koło czy Kwadrat (Active Learning)")
        root.resizable(False, False)

        self.canvas = tk.Canvas(
            root, width=ROZMIAR, height=ROZMIAR,
            bg="white", highlightthickness=2, highlightbackground="#333"
        )
        self.canvas.pack(padx=14, pady=10)
        self.canvas.bind("<ButtonPress-1>", self.start)
        self.canvas.bind("<B1-Motion>", self.ruch)
        self.canvas.bind("<ButtonRelease-1>", self.koniec)

        panel = tk.Frame(root)
        panel.pack(pady=(0, 6))

        tk.Button(panel, text="Wyczyść", width=10, command=self.wyczysc).grid(row=0, column=0, padx=3, pady=2)
        tk.Button(panel, text="Rozpoznaj", width=10, font=("Helvetica", 9, "bold"),
                  bg="#2ecc71", fg="white", activebackground="#27ae60",
                  command=self.rozpoznaj).grid(row=0, column=1, padx=3, pady=2)
        tk.Button(panel, text="To koło", width=11, bg="#e8f4f8",
                  command=lambda: self.zapisz_i_ucz("kolo")).grid(row=0, column=2, padx=3, pady=2)
        tk.Button(panel, text="To kwadrat", width=11, bg="#fdf2e9",
                  command=lambda: self.zapisz_i_ucz("kwadrat")).grid(row=0, column=3, padx=3, pady=2)

        panel2 = tk.Frame(root)
        panel2.pack(pady=(0, 8))
        tk.Button(panel2, text="Generuj 50+50 próbek", width=22,
                  command=self.generuj_syntetyczne).grid(row=0, column=0, padx=4)

        self.status = tk.Label(
            root, text="Narysuj figurę i kliknij 'Rozpoznaj' lub oznacz ją przyciskami.",
            width=58, wraplength=420, justify="center", font=("Helvetica", 10), pady=4
        )
        self.status.pack(pady=(0, 10))

        self.granica = m.wczytaj_granice()
        self.nowy_rysunek()

    def nowy_rysunek(self):
        self.canvas.delete("all")
        self.obraz = Image.new("L", (ROZMIAR, ROZMIAR), 0)
        self.rysik = ImageDraw.Draw(self.obraz)
        self.punkty = []

    def wyczysc(self):
        self.nowy_rysunek()
        self.status.config(text="Płótno wyczyszczone. Narysuj figurę.")

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
            self.granica = m.wczytaj_granice()
            if self.granica is None:
                self.status.config(text="Brak wyuczonego modelu. Kliknij 'Generuj 50+50' lub uruchom model.py.")
                return

        if len(self.punkty) < 2:
            self.status.config(text="Płótno jest puste! Narysuj najpierw figurę.")
            return

        try:
            wyp, rogi = cechy(self.obraz)
        except ValueError as err:
            self.status.config(text=f"Błąd analizy: {err}")
            return

        w1, w2 = self.granica["w"]
        z = w1 * wyp + w2 * rogi + self.granica["b"]
        pewnosc = 1.0 / (1.0 + math.exp(-abs(z)))
        etykieta = self.granica["klasa_dodatnia"] if z > 0 else self.granica["klasa_ujemna"]
        nazwa = {"kolo": "KOŁO", "kwadrat": "KWADRAT"}.get(etykieta, etykieta.upper())

        self.status.config(
            text=f"Rozpoznano: {nazwa} (pewność: {pewnosc:.1%})\n"
                 f"[wypełnienie prostokąta: {wyp:.3f}, rogi: {rogi:.0f}, z: {z:+.2f}]"
        )

    def przelicz_model(self):
        wynik = m.ucz()
        if wynik is None:
            X, y = m.wczytaj_dane()
            return f"Zapisano. Próbek: {len(y)}. Za mało do uczenia (min. {m.MIN_PROBEK})."
        self.granica = wynik["granica"]
        return (f"Model zaktualizowany! Próbek: {wynik['probek']}, "
                f"dokładność na teście: {wynik['dokladnosc']:.1%}\n{m.wzor(self.granica)}")

    def zapisz_i_ucz(self, etykieta):
        if len(self.punkty) < 2:
            self.status.config(text="Najpierw narysuj figurę, aby ją zapisać.")
            return

        try:
            c = cechy(self.obraz)
        except ValueError as err:
            self.status.config(text=f"Błąd cech: {err}")
            return

        nowy = not os.path.exists(m.SCIEZKA_DANYCH) or os.path.getsize(m.SCIEZKA_DANYCH) == 0
        with open(m.SCIEZKA_DANYCH, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if nowy:
                w.writerow(m.KOLUMNY + ["etykieta"])
            w.writerow([f"{c[0]:.4f}", f"{c[1]:.1f}", etykieta])

        self.nowy_rysunek()
        status_modelu = self.przelicz_model()
        nazwa = {"kolo": "Koło", "kwadrat": "Kwadrat"}.get(etykieta, etykieta)
        self.status.config(text=f"Dodano: {nazwa} (wypełnienie {c[0]:.3f}, rogi {c[1]:.0f})\n{status_modelu}")

    def generuj_syntetyczne(self):
        self.status.config(text="Generowanie próbek syntetycznych w toku...")
        self.root.update_idletasks()
        wiersze = gen.dopisz(50)
        status_modelu = self.przelicz_model()
        self.status.config(text=f"Wygenerowano {len(wiersze)} nowych próbek.\n{status_modelu}")


if __name__ == "__main__":
    root = tk.Tk()
    AplikacjaGlowna(root)
    root.mainloop()
