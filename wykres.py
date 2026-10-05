"""Program 3: animacja uczenia. Co 0,5 s dokłada kolejny punkt z dane.csv (w kolejności z pliku),
uczy granicę na dotychczasowych punktach i przerysowuje ją.

Użycie: python wykres.py [dane.csv] [odstęp_w_sekundach]
Zamknięcie okna przerywa animację.
"""
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

import model as m

KOLORY = {"kolo": "tab:blue", "kwadrat": "tab:red"}


def animuj(sciezka_danych=m.SCIEZKA_DANYCH, odstep=0.5):
    X, y = m.wczytaj_dane(sciezka_danych)
    if len(y) == 0:
        raise SystemExit(f"Brak danych w {sciezka_danych}.")

    fig, ax = plt.subplots()
    xmax, ymax = X[:, 0].max() * 1.15, X[:, 1].max() * 1.15
    ax.set_xlim(0, xmax)
    ax.set_ylim(0, ymax)
    ax.set_xlabel("CV promienia (odch. std / średnia odległość od środka)")
    ax.set_ylabel("Rozpiętość promienia (p95 - p5) / p95")
    ax.grid(alpha=0.3)

    punkty = {et: ax.scatter([], [], c=k, label=et, alpha=0.7) for et, k in KOLORY.items()}
    linia, = ax.plot([], [], "k--", label="granica")
    ax.legend(loc="upper left")
    xs = np.linspace(0, xmax, 200)

    def klatka(k):
        n = k + 1
        for et, sc in punkty.items():
            d = X[:n][y[:n] == et]
            sc.set_offsets(d if len(d) else np.empty((0, 2)))
        opis = f"Punkty: {n}/{len(y)}"
        yn = y[:n]
        if min((yn == "kolo").sum(), (yn == "kwadrat").sum()) >= 2:  # potrzebne obie figury
            g = m.dopasuj(X[:n], yn)
            (w1, w2), b = g["w"], g["b"]
            if abs(w2) > 1e-9:
                linia.set_data(xs, -(w1 * xs + b) / w2)  # z = w1*x + w2*y + b = 0
            opis += f"   |   {m.wzor(g)}   |   dokładność: {m.dokladnosc(g, X[:n], yn):.0%}"
        ax.set_title(opis, fontsize=10)
        if n == len(y):
            fig.savefig(os.path.join(m.FOLDER, "wykres.png"), dpi=120, bbox_inches="tight")
        return list(punkty.values()) + [linia]

    animacja = FuncAnimation(fig, klatka, frames=len(y), interval=odstep * 1000,
                             repeat=False, blit=False)
    plt.show()
    return fig, klatka, animacja


if __name__ == "__main__":
    sciezka = sys.argv[1] if len(sys.argv) > 1 else m.SCIEZKA_DANYCH
    animuj(sciezka, float(sys.argv[2]) if len(sys.argv) > 2 else 0.5)
