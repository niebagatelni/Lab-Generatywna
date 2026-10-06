"""Generator syntetycznych odręcznych figur (koła/elipsy i zniekształcone kwadraty) w pamięci RAM.
Zawiera pełną implementację zniekształceń z projektu 'kwadraty i kolka':
- Dla kół: spłaszczanie do elips (asymetria osi), losowy obrót, harmoniczny wobble promienia, drżenie ręki.
- Dla kwadratów: losowe przesunięcia narożników, zginanie krawędzi, obrót 360 stopni i mikro-drżenie.

Użycie z konsoli:
    python generuj.py [liczba_na_klase]   (np. python generuj.py 300)
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


def generuj_odreczne_kolo_lub_elipse(size=ROZMIAR):
    """Generuje odręczne koło lub elipsę z harmonicznym falowaniem i zniekształceniami."""
    img = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(img)

    cx = random.uniform(size * 0.35, size * 0.65)
    cy = random.uniform(size * 0.35, size * 0.65)
    base_r = random.uniform(size * 0.16, size * 0.32)

    # Spłaszczanie do elipsy (od 0.55 do 1.45) oraz losowy obrót
    aspect = random.uniform(0.55, 1.45)
    rx = base_r
    ry = base_r * aspect
    rot = random.uniform(0, 2 * math.pi)

    # Harmoniczny szum promienia (wobble z projektu 'kwadraty i kolka')
    num_pts = random.randint(50, 95)
    wobble1 = random.uniform(0.03, 0.10) * base_r
    wobble2 = random.uniform(0.01, 0.06) * base_r
    phase1 = random.uniform(0, 2 * math.pi)
    phase2 = random.uniform(0, 2 * math.pi)
    line_w = random.randint(3, 7)

    cos_rot, sin_rot = math.cos(rot), math.sin(rot)
    pts = []
    tot_angle = 2 * math.pi + random.uniform(0.05, 0.30)  # nachodzenie pociągnięć
    step = tot_angle / num_pts

    for i in range(num_pts + 1):
        th = i * step
        smooth_dev = wobble1 * math.sin(th + phase1) + wobble2 * math.sin(2 * th + phase2)
        local_jit = random.uniform(-0.02, 0.02) * base_r
        lx = (rx + smooth_dev + local_jit) * math.cos(th)
        ly = (ry + smooth_dev + local_jit) * math.sin(th)

        # Obrót i translacja do środka
        gx = lx * cos_rot - ly * sin_rot + cx
        gy = lx * sin_rot + ly * cos_rot + cy
        pts.append((gx, gy))

    draw.line(pts, fill=255, width=line_w, joint="curve")
    return img


def generuj_odreczny_kwadrat(size=ROZMIAR):
    """Generuje odręczny kwadrat ze zniekształceniami wierzchołków i zgięciem boków."""
    img = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(img)

    cx = random.uniform(size * 0.35, size * 0.65)
    cy = random.uniform(size * 0.35, size * 0.65)
    half_s = random.uniform(size * 0.16, size * 0.32)
    aspect = random.uniform(0.85, 1.15)
    half_w = half_s
    half_h = half_s * aspect
    rot = random.uniform(-math.pi, math.pi)  # pełny obrót o dowolny kąt
    line_w = random.randint(3, 7)

    corners = [
        (-half_w, -half_h),
        (half_w, -half_h),
        (half_w, half_h),
        (-half_w, half_h)
    ]

    cos_a, sin_a = math.cos(rot), math.sin(rot)
    t_corners = []
    max_shift = half_s * 0.20

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
            jitter = math.sin(t * math.pi) * random.uniform(-3.5, 3.5)
            x_int = p_start[0] + t * (p_end[0] - p_start[0]) + jitter
            y_int = p_start[1] + t * (p_end[1] - p_start[1]) + jitter
            pts.append((x_int, y_int))

    pts.append(pts[0])  # domknięcie
    draw.line(pts, fill=255, width=line_w, joint="curve")
    return img


def _probka_z_cechami(generator_fn):
    """Generuje kształt w pamięci i bezpiecznie wyciąga cechy."""
    for _ in range(25):
        try:
            img = generator_fn()
            c = cechy(img)
            return c
        except ValueError:
            continue
    raise RuntimeError("Nie udało się wygenerować poprawnego kształtu.")


def generuj(n):
    """Generuje n kół/elips i n zniekształconych kwadratów naprzemiennie."""
    wiersze = []
    for _ in range(n):
        for etykieta, gen_fn in (("kolo", generuj_odreczne_kolo_lub_elipse), ("kwadrat", generuj_odreczny_kwadrat)):
            c = _probka_z_cechami(gen_fn)
            wiersze.append((f"{c[0]:.4f}", f"{c[1]:.1f}", etykieta))
    return wiersze


def dopisz(n, sciezka=SCIEZKA):
    """Dopisuje wygenerowane próbki do pliku CSV."""
    wiersze = generuj(n)
    naglowek = m.KOLUMNY + ["etykieta"]
    nowy = not os.path.exists(sciezka) or os.path.getsize(sciezka) == 0

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
    print(f"Pomyślnie wygenerowano i dopisano {2 * n} próbek (koła/elipsy + kwadraty) do {SCIEZKA}")
