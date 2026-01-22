# src/symulacje/prosty_test.py

import sys
import os
import matplotlib.pyplot as plt
from src.konfiguracja import KonfiguracjaNaboju

# Dodajemy lokalną ścieżkę do biblioteki
sys.path.append(os.path.abspath("py_ballistics"))

from py_ballistics.simulator import simulate_drag

def wykonaj_symulacje(config_path):
    # Wczytanie danych
    konfiguracja = KonfiguracjaNaboju.wczytaj_z_pliku(config_path)

    # Uruchomienie symulacji
    wynik = simulate_drag(
        v0=konfiguracja.predkosc_poczatkowa,
        m=konfiguracja.masa,
        c=konfiguracja.opor_powietrza,
        h0=konfiguracja.wysokosc,
        angle=konfiguracja.kat,
        dt=0.1
    )

    # Rysowanie wykresu
    x, y = wynik["x"], wynik["y"]
    plt.plot(x, y)
    plt.xlabel("Odległość [m]")
    plt.ylabel("Wysokość [m]")
    plt.title("Tor lotu pocisku")
    plt.grid()
    plt.show()

    # Wypisanie najważniejszych wyników
    print("=== WYNIKI SYMULACJI ===")
    print(f"Maksymalny zasięg: {max(x):.2f} m")
    print(f"Maksymalna wysokość: {max(y):.2f} m")
