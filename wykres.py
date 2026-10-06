"""Animacja procesu uczenia i adaptacji granicy decyzyjnej 2D.
Wizualizuje przestrzeń cech: Wypełnienie prostokąta otaczającego vs Liczba rogów.
Dla kół i elips wypełnienie wynosi zawsze ~0.785, dla kwadratów ~0.90 - 1.0.

Użycie z konsoli:
    python wykres.py [dane.csv] [odstep_w_sekundach] [--save-only]
"""
import os
import sys
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

import model as m

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KOLORY = {"kolo": "#1f77b4", "kwadrat": "#d62728"}
ETYKIETY_PL = {"kolo": "Koła", "kwadrat": "Kwadraty"}


def animuj(sciezka_danych=m.SCIEZKA_DANYCH, odstep=0.04, save_only=False):
    X, y = m.wczytaj_dane(sciezka_danych)
    if len(y) == 0:
        raise SystemExit(f"Brak danych w {sciezka_danych}.")

    fig, ax = plt.subplots(figsize=(9, 6), dpi=100)

    # Ustalenie granic osi wykresu
    xmin = max(0.65, float(X[:, 0].min()) - 0.05)
    xmax = min(1.05, float(X[:, 0].max()) + 0.05)
    ymin = 2.0
    ymax = max(11.0, float(X[:, 1].max()) + 2.0)

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_xlabel("Wypełnienie prostokąta otaczającego (Pole otoczki / Pole minAreaRect)", fontsize=11)
    ax.set_ylabel("Liczba wierzchołków / rogów (approxPolyDP)", fontsize=11)
    ax.grid(True, linestyle=":", alpha=0.6)

    # Delikatny jitter wizualny na dyskretnej osi Y
    np.random.seed(42)
    jitter_y = np.random.uniform(-0.18, 0.18, size=len(y))

    punkty = {
        et: ax.scatter([], [], c=KOLORY[et], label=ETYKIETY_PL[et], alpha=0.75, s=35, edgecolors="none")
        for et in ("kolo", "kwadrat")
    }
    linia, = ax.plot([], [], "k--", linewidth=2.2, label="Granica decyzyjna (w1·x + w2·y + b = 0)")
    ax.legend(loc="upper left", fontsize=10)

    xs = np.linspace(xmin, xmax, 200)

    def klatka(k):
        n = k + 1
        for et, sc in punkty.items():
            mask = (y[:n] == et)
            if np.any(mask):
                x_pts = X[:n, 0][mask]
                y_pts = (X[:n, 1] + jitter_y[:n])[mask]
                sc.set_offsets(np.column_stack((x_pts, y_pts)))
            else:
                sc.set_offsets(np.empty((0, 2)))

        opis = f"Próbki: {n}/{len(y)}"
        yn = y[:n]
        if min((yn == "kolo").sum(), (yn == "kwadrat").sum()) >= 2:
            g = m.dopasuj(X[:n], yn)
            (w1, w2), b = g["w"], g["b"]
            if abs(w2) > 1e-9:
                ys = -(w1 * xs + b) / w2
                linia.set_data(xs, ys)
            dokl = m.dokladnosc(g, X[:n], yn)
            opis += f" | {m.wzor(g)} | Dokładność: {dokl:.1%}"

        ax.set_title(opis, fontsize=10, pad=10)

        if n == len(y):
            out_img = os.path.join(m.FOLDER, "wykres.png")
            fig.savefig(out_img, dpi=120, bbox_inches="tight")
            print(f"Zapisano wykres końcowy do: {out_img}")

        return list(punkty.values()) + [linia]

    if save_only:
        klatka(len(y) - 1)
        plt.close(fig)
        return

    animacja = FuncAnimation(
        fig, klatka, frames=len(y), interval=int(odstep * 1000), repeat=False, blit=False
    )
    plt.tight_layout()
    plt.show()
    return fig, klatka, animacja


if __name__ == "__main__":
    sciezka = m.SCIEZKA_DANYCH
    odstep = 0.04
    save_only = False

    args = sys.argv[1:]
    if "--save-only" in args:
        save_only = True
        args.remove("--save-only")

    if len(args) > 0 and not args[0].replace(".", "", 1).isdigit():
        sciezka = args[0]
        args = args[1:]
    if len(args) > 0:
        odstep = float(args[0])

    animuj(sciezka, odstep, save_only=save_only)
