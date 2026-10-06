"""Ekstrakcja cech geometrycznych kształtu z obrazu za pomocą OpenCV.

Cechy:
1. kolistosc (Circularity) = 4 * pi * Pole / (Obwód^2)
   Dla idealnego koła = 1.0 (odręczne koło ~0.88 - 0.99).
   Dla kwadratu = pi/4 ~ 0.785 (odręczny kwadrat ~0.65 - 0.83).
2. liczba_rogow = liczba wierzchołków wielokąta z algorytmu approxPolyDP (otoczka convex hull).
   Dla kwadratu = 4.
   Dla koła = zazwyczaj 6 - 16 (brak ostrych załamań pod kątem prostym).
"""
import numpy as np
import cv2

GRUBOSC = 4   # grubość linii pędzla przy rysowaniu
MIN_BOK = 15  # minimalny rozmiar obwiedni figury w pikselach


def cechy(obraz):
    """Przyjmuje obraz jako numpy array (bool/uint8) lub PIL Image i zwraca (kolistosc, liczba_rogow)."""
    if hasattr(obraz, "convert"):
        arr = np.array(obraz.convert("L"), dtype=np.uint8)
    else:
        arr = np.asarray(obraz)
        if arr.dtype == bool:
            arr = (arr * 255).astype(np.uint8)
        elif arr.dtype != np.uint8:
            arr = (arr > 0).astype(np.uint8) * 255

    ys, xs = np.nonzero(arr)
    if len(ys) == 0:
        raise ValueError("Pusty rysunek - narysuj figurę przed sprawdzeniem.")
    if ys.max() - ys.min() + 1 < MIN_BOK or xs.max() - xs.min() + 1 < MIN_BOK:
        raise ValueError("Rysunek jest zbyt mały.")

    # Wykrywanie zewnętrznego konturu
    contours, _ = cv2.findContours(arr, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise ValueError("Nie wykryto konturu figury.")

    cnt = max(contours, key=cv2.contourArea)
    hull = cv2.convexHull(cnt)

    area = float(cv2.contourArea(hull))
    perimeter = float(cv2.arcLength(hull, True))

    if perimeter <= 0 or area <= 0:
        raise ValueError("Figura ma zerowy obwód lub pole.")

    # 1. Kolistość izoperymetryczna
    kolistosc = (4.0 * np.pi * area) / (perimeter ** 2)

    # 2. Liczba wierzchołków z wielokąta approxPolyDP
    approx = cv2.approxPolyDP(hull, 0.04 * perimeter, True)
    liczba_rogow = float(len(approx))

    return float(kolistosc), float(liczba_rogow)
