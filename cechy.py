"""Ekstrakcja cech geometrycznych kształtu z obrazu za pomocą OpenCV.

Cechy:
1. wypelnienie_prostokata (Rectangularity / Box Ratio) = Pole otoczki / Pole minimalnego prostokąta otaczającego (minAreaRect).
   - Niezmiennik geometryczny: dla koła oraz DOWOLNEJ elipsy (nawet mocno spłaszczonej lub obróconej)
     stosunek ten wynosi teoretycznie pi / 4 ~ 0.785 (w rysunku odręcznym ~0.74 - 0.81).
   - Dla kwadratu i prostokąta wynosi teoretycznie 1.0 (w rysunku odręcznym ~0.86 - 0.99).
   Dzięki temu odręczne elipsy i jajowate koła nigdy nie są mylone z kwadratami!
2. liczba_rogow = liczba wierzchołków wielokąta z algorytmu approxPolyDP (z progiem 0.03 * obwód).
   - Dla kwadratu: regularnie 4.
   - Dla koła / elipsy: 6 - 16 (brak kątów prostych i płaskich boków).
"""
import numpy as np
import cv2

GRUBOSC = 4   # grubość linii pędzla przy rysowaniu
MIN_BOK = 15  # minimalny rozmiar obwiedni figury w pikselach


def cechy(obraz):
    """Przyjmuje obraz jako numpy array (bool/uint8) lub PIL Image i zwraca (wypelnienie_prostokata, liczba_rogow)."""
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

    contours, _ = cv2.findContours(arr, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise ValueError("Nie wykryto konturu figury.")

    cnt = max(contours, key=cv2.contourArea)
    hull = cv2.convexHull(cnt)

    area_hull = float(cv2.contourArea(hull))
    perimeter = float(cv2.arcLength(hull, True))

    if perimeter <= 0 or area_hull <= 0:
        raise ValueError("Figura ma zerowy obwód lub pole.")

    # 1. Wypełnienie minimalnego zorientowanego prostokąta otaczającego
    rect = cv2.minAreaRect(hull)
    rect_area = float(rect[1][0] * rect[1][1])
    wypelnienie_prostokata = (area_hull / rect_area) if rect_area > 0 else 0.0

    # 2. Liczba wierzchołków z wielokąta approxPolyDP (próg 0.03 * obwód)
    approx = cv2.approxPolyDP(hull, 0.03 * perimeter, True)
    liczba_rogow = float(len(approx))

    return float(wypelnienie_prostokata), float(liczba_rogow)
