"""Generuje syntetyczne koła i kwadraty (na przemian) i dopisuje ich cechy do dane.csv.

Użycie: python generuj.py [liczba_na_klase]   (domyślnie 50)
"""
import csv
import math
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw

import model as m
from cechy import GRUBOSC, cechy

ROZMIAR = 300
SCIEZKA = m.SCIEZKA_DANYCH


def _drzenie(p, sila):
    return (p[0] + random.uniform(-sila, sila), p[1] + random.uniform(-sila, sila))


def punkty_kola():
    rx = random.uniform(20, 140)
    ry = rx * random.uniform(0.85, 1.15)  # lekko spłaszczone
    cx = random.uniform(rx + 2, ROZMIAR - rx - 2)
    cy = random.uniform(ry + 2, ROZMIAR - ry - 2)
    n = 90
    start = random.uniform(0, 2 * math.pi)
    # odległość od środka lekko faluje, jak przy ręcznym rysowaniu
    faza, amp = random.uniform(0, 6.28), random.uniform(0.0, 0.04)
    pts = []
    for i in range(n):
        a = start + 2 * math.pi * i / n
        f = 1 + amp * math.sin(3 * a + faza)
        pts.append((cx + rx * f * math.cos(a), cy + ry * f * math.sin(a)))
    return [_drzenie(p, 1.0) for p in pts]


def punkty_kwadratu():
    a = random.uniform(30, 250)
    b = a * random.uniform(0.9, 1.1)
    kat = math.radians(random.uniform(-12, 12))
    cx = ROZMIAR / 2 + random.uniform(-1, 1) * (ROZMIAR - max(a, b) * 1.45) / 2
    cy = ROZMIAR / 2 + random.uniform(-1, 1) * (ROZMIAR - max(a, b) * 1.45) / 2
    rog = [(-a / 2, -b / 2), (a / 2, -b / 2), (a / 2, b / 2), (-a / 2, b / 2)]
    rog = [(cx + x * math.cos(kat) - y * math.sin(kat),
            cy + x * math.sin(kat) + y * math.cos(kat)) for x, y in rog]
    pts = []
    sila = random.uniform(0.5, 3.0)
    for i in range(4):
        p, q = rog[i], rog[(i + 1) % 4]
        for t in np.linspace(0, 1, 25, endpoint=False):
            pts.append(_drzenie((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t), sila))
    return pts


def obrys(punkty):
    obraz = Image.new("1", (ROZMIAR, ROZMIAR), 0)
    rysik = ImageDraw.Draw(obraz)
    p = punkty + [punkty[0]]  # domknięcie jak w main.py
    rysik.line(p, fill=1, width=GRUBOSC)
    return np.array(obraz, dtype=bool)


def _jedna(gen):
    """Losuje figurę, aż się zmieści na płótnie i da policzyć cechy."""
    while True:
        pts = gen()
        if any(not (2 <= x <= ROZMIAR - 3 and 2 <= y <= ROZMIAR - 3) for x, y in pts):
            continue  # figura wystaje poza płótno
        try:
            return cechy(obrys(pts))
        except ValueError:
            continue


def generuj(n):
    """n kół i n kwadratów, na przemian: koło, kwadrat, koło, kwadrat..."""
    wiersze = []
    for _ in range(n):
        for etykieta, gen in (("kolo", punkty_kola), ("kwadrat", punkty_kwadratu)):
            c = _jedna(gen)
            wiersze.append((f"{c[0]:.4f}", f"{c[1]:.4f}", etykieta))
    return wiersze


def dopisz(n, sciezka=SCIEZKA):
    """Dopisuje do CSV n kół i n kwadratów na przemian (nie kasuje istniejących wierszy).
    Zwraca dopisane wiersze."""
    wiersze = generuj(n)
    nowy = not os.path.exists(sciezka) or os.path.getsize(sciezka) == 0
    with open(sciezka, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if nowy:
            w.writerow(m.KOLUMNY + ["etykieta"])
        w.writerows(wiersze)
    return wiersze


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    dopisz(n)
    print(f"Dopisano {2 * n} próbek do {SCIEZKA}")
