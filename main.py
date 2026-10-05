"""Program 1 (uczący): rysujesz figury i zapisujesz je do dane.csv albo generujesz 50+50.
Po każdym dodaniu danych model uczy się od nowa i zapisuje granica.json dla rozpoznaj.py.
"""
import csv
import os
import tkinter as tk

import numpy as np
from PIL import Image, ImageDraw

import generuj as gen
import model as m
from cechy import GRUBOSC, cechy

ROZMIAR = 300


class Aplikacja:
    def __init__(self, root):
        self.root = root
        root.title("Uczenie: koło czy kwadrat")

        self.canvas = tk.Canvas(root, width=ROZMIAR, height=ROZMIAR,
                                bg="white", highlightthickness=1,
                                highlightbackground="black")
        self.canvas.pack(padx=10, pady=10)
        self.canvas.bind("<ButtonPress-1>", self.start)
        self.canvas.bind("<B1-Motion>", self.ruch)
        self.canvas.bind("<ButtonRelease-1>", self.koniec)

        panel = tk.Frame(root)
        panel.pack(pady=(0, 5))
        tk.Button(panel, text="Wyczyść", command=self.wyczysc).grid(row=0, column=0, padx=3)
        tk.Button(panel, text="To koło", command=lambda: self.zapisz("kolo")).grid(row=0, column=1, padx=3)
        tk.Button(panel, text="To kwadrat", command=lambda: self.zapisz("kwadrat")).grid(row=0, column=2, padx=3)
        tk.Button(panel, text="Generuj 50+50", command=self.generuj).grid(row=0, column=3, padx=3)

        self.status = tk.Label(root, text="Narysuj figurę albo wygeneruj dane.",
                               width=52, wraplength=380, justify="center")
        self.status.pack(pady=(0, 10))

        self.nowy_rysunek()

    def nowy_rysunek(self):
        self.canvas.delete("all")
        self.obraz = Image.new("1", (ROZMIAR, ROZMIAR), 0)
        self.rysik = ImageDraw.Draw(self.obraz)
        self.punkty = []
        self.domkniety = False

    def wyczysc(self):
        self.nowy_rysunek()

    def linia(self, a, b):
        self.canvas.create_line(*a, *b, width=GRUBOSC, capstyle=tk.ROUND)
        self.rysik.line([a, b], fill=1, width=GRUBOSC)

    def start(self, e):
        # nowe pociągnięcie po skończonej figurze czyści płótno
        if self.domkniety:
            self.nowy_rysunek()
        self.punkty = [(e.x, e.y)]

    def ruch(self, e):
        p = (e.x, e.y)
        self.linia(self.punkty[-1], p)
        self.punkty.append(p)

    def koniec(self, _):
        if len(self.punkty) > 1:
            self.linia(self.punkty[-1], self.punkty[0])  # domknięcie obrysu
            self.domkniety = True

    def ucz(self):
        """Uczy na całym dane.csv i zapisuje granica.json. Zwraca tekst do statusu."""
        wynik = m.ucz()
        if wynik is None:
            X, y = m.wczytaj_dane()
            return (f"Próbek: {len(y)}. Za mało do uczenia (min. {m.MIN_PROBEK}, "
                    f"po {m.MIN_NA_KLASE} każdej figury).")
        return (f"Próbek: {wynik['probek']}, dokładność na teście: {wynik['dokladnosc']:.0%}\n"
                f"{m.wzor(wynik['granica'])}")

    def zapisz(self, etykieta):
        if not self.domkniety:
            self.status.config(text="Najpierw narysuj figurę.")
            return
        try:
            c = cechy(np.array(self.obraz, dtype=bool))
        except ValueError as err:
            self.status.config(text=f"Błąd: {err}")
            return
        nowy = not os.path.exists(m.SCIEZKA_DANYCH) or os.path.getsize(m.SCIEZKA_DANYCH) == 0
        with open(m.SCIEZKA_DANYCH, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if nowy:
                w.writerow(m.KOLUMNY + ["etykieta"])
            w.writerow([f"{c[0]:.4f}", f"{c[1]:.4f}", etykieta])
        self.nowy_rysunek()
        self.status.config(text=f"Zapisano: {etykieta} (cv {c[0]:.3f}, rozp_p {c[1]:.2f})\n{self.ucz()}")

    def generuj(self):
        """Dopisuje 50 kół i 50 kwadratów (na przemian), uczy i zapisuje granicę."""
        self.status.config(text="Generuję...")
        self.root.update_idletasks()
        stara = m.wczytaj_granice()
        wiersze = gen.dopisz(50)
        przed = ""
        if stara is not None:  # uczciwy test: stara granica na nowej, niewidzianej porcji
            X = np.array([[float(r[0]), float(r[1])] for r in wiersze])
            y = np.array([r[2] for r in wiersze])
            przed = f"Stara granica na nowych figurach: {m.dokladnosc(stara, X, y):.0%}\n"
        self.status.config(text=f"Dopisano {len(wiersze)} próbek.\n{przed}{self.ucz()}")


if __name__ == "__main__":
    root = tk.Tk()
    Aplikacja(root)
    root.mainloop()
