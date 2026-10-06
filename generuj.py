"""Generator syntetycznych odręcznych kół i kwadratów w pamięci RAM.
Wzbogacony o realistyczny szum, harmoniczne falowanie i losowe obroty (zapożyczone z generatora CNN).
Wyekstrahowane cechy dopisywane są do pliku dane.csv bez tworzenia tysięcy plików PNG.

Użycie z konsoli:
    python generuj.py [liczba_na_klase]   (domyślnie 50)
"""
import csv
import math
import os
import random
import sys
import numpy as np
from PIL import Image, ImageDraw

import model as m
from cechy import cechy

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROZMIAR = 350
SCIEZKA = m.SCIEZKA_DANYCH


def generuj_odreczne_kolo(size=ROZMIAR):
    """Generuje obraz odręcznego koła z harmonicznym falowaniem promienia."""
    img = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(img)

    cx = random.uniform(size * 0.35, size * 0.65)
    cy = random.uniform(size * 0.35, size * 0.65)
    base_r = random.uniform(size * 0.16, size * 0.33)

    num_pts = random.randint(50, 90)
    wobble1 = random.uniform(0.02, 0.08) * base_r
    wobble2 = random.uniform(0.01, 0.05) * base_r
    phase1 = random.uniform(0, 2 * math.pi)
    phase2 = random.uniform(0, 2 * math.pi)
    line_w = random.randint(3, 6)

    pts = []
    tot_angle = 2 * math.pi + random.uniform(0.05, 0.25)  # lekkie nachodzenie linii
    step = tot_angle / num_pts

    for i in range(num_pts + 1):
        th = i * step
        smooth_dev = wobble1 * math.sin(th + phase1) + wobble2 * math.sin(2 * th + phase2)
        local_jitter = random.uniform(-0.02, 0.02) * base_r
        r = base_r + smooth_dev + local_jitter

        x = cx + r * math.cos(th)
        y = cy + r * math.sin(th)
        pts.append((x, y))

    draw.line(pts, fill=255, width=line_w, joint="curve")
    return img


def generuj_odreczny_kwadrat(size=ROZMIAR):
    """Generuje obraz odręcznego kwadratu z deformacją wierzchołków i drżeniem krawędzi."""
    img = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(img)

    cx = random.uniform(size * 0.35, size * 0.65)
    cy = random.uniform(size * 0.35, size * 0.65)
    half_s = random.uniform(size * 0.16, size * 0.32)
    rot = random.uniform(-0.5, 0.5)  # obrót o ok. +/- 28 stopni
    line_w = random.randint(3, 6)

    corners = [
        (-half_s, -half_s),
        (half_s, -half_s),
        (half_s, half_s),
        (-half_s, half_s)
    ]

    cos_a, sin_a = math.cos(rot), math.sin(rot)
    t_corners = []
    max_shift = half_s * 0.16

    for x, y in corners:
        xs = x + random.uniform(-max_shift, max_shift)
        ys = y + random.uniform(-max_shift, max_shift)
        xr = xs * cos_a - ys * sin_a + cx
        yr = xs * sin_a + ys * cos_a + cy
        t_corners.append((xr, yr))

    pts = []
    for i in range(4):
        p_start = t_corners[i]
        p_end = t_corners[(i + 1) % 4]
        steps = random.randint(8, 14)
        for s in range(steps):
            t = s / steps
            jitter = math.sin(t * math.pi) * random.uniform(-2.5, 2.5)
            x_int = p_start[0] + t * (p_end[0] - p_start[0]) + jitter
            y_int = p_start[1] + t * (p_end[1] - p_start[1]) + jitter
            pts.append((x_int, y_int))

    pts.append(pts[0])  # domknięcie
    draw.line(pts, fill=255, width=line_w, joint="curve")
    return img


def _probka_z_cechami(generator_fn):
    """Generuje obraz i bezpiecznie wyciąga cechy."""
    for _ in range(20):
        try:
            img = generator_fn()
            c = cechy(img)
            return c
        except ValueError:
            continue
    raise RuntimeError("Nie udało się wygenerować poprawnego kształtu po 20 próbach.")


def generuj(n):
    """Generuje n kół i n kwadratów naprzemiennie, zwracając listę krotek (kolistosc, liczba_rogow, etykieta)."""
    wiersze = []
    for _ in range(n):
        for etykieta, gen_fn in (("kolo", generuj_odreczne_kolo), ("kwadrat", generuj_odreczny_kwadrat)):
            c = _probka_z_cechami(gen_fn)
            wiersze.append((f"{c[0]:.4f}", f"{c[1]:.1f}", etykieta))
    return wiersze


def dopisz(n, sciezka=SCIEZKA):
    """Generuje i dopisuje n kół i n kwadratów do pliku CSV."""
    wiersze = generuj(n)
    naglowek = m.KOLUMNY + ["etykieta"]
    nowy = not os.path.exists(sciezka) or os.path.getsize(sciezka) == 0

    # Sprawdzenie czy istniejący plik ma aktualny nagłówek
    if not nowy:
        with open(sciezka, "r", encoding="utf-8") as f:
            pierwsza_linia = f.readline().strip().split(",")
            if pierwsza_linia != naglowek:
                nowy = True

    tryb = "w" if nowy else "a"
    with open(sciezka, tryb, newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if nowy:
            w.writerow(naglowek)
        w.writerows(wiersze)
    return wiersze


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    dopisz(n)
    print(f"Pomyślnie wygenerowano i dopisano {2 * n} próbek do {SCIEZKA}")
