import numpy as np

GRUBOSC = 3   # grubość linii konturu (px), używana przy rysowaniu
MIN_BOK = 15  # minimalny rozmiar figury (px), poniżej tego odrzucamy rysunek


def cechy(obrys):
    """obrys: tablica 2D, True = piksel linii konturu (już domkniętego).
    Pracuje wyłącznie na konturze. Środek = średnia położeń pikseli konturu,
    r = odległość każdego piksela konturu od środka.
    Zwraca (cv_promienia, rozpietosc_p):
      cv_promienia = odchylenie standardowe r / średnia r   -> koło ~0,04, kwadrat ~0,11 (idealny kwadrat 0,10)
      rozpietosc_p = (p95 - p5) / p95, gdzie p95 i p5 to 95. i 5. percentyl r
                     (jak (r_max - r_min) / r_max, ale odporna na pojedyncze odstające piksele)
    Obie cechy nie zależą od rozmiaru ani od obrotu figury.
    """
    ys, xs = np.nonzero(obrys)
    if len(ys) == 0:
        raise ValueError("Pusty rysunek.")
    if ys.max() - ys.min() + 1 < MIN_BOK or xs.max() - xs.min() + 1 < MIN_BOK:
        raise ValueError("Figura jest za mała.")

    r = np.hypot(ys - ys.mean(), xs - xs.mean())
    cv = r.std() / r.mean()
    p5, p95 = np.percentile(r, [5, 95])
    rozpietosc_p = (p95 - p5) / p95
    return float(cv), float(rozpietosc_p)
