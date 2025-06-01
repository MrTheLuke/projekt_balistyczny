# main.py

import os
import sys
import subprocess
from src.konfiguracja import Konfiguracja
from src.interfejs import wybierz_konfiguracje, zapytaj_parametry
from src.symulacja import uruchom_symulacje, wyswietl_wyniki
from src.optymalizacja import przeprowadz_optymalizacje

# Ścieżka do py_ballistics (ustawić zgodnie z lokalizacją środowiska)
SCIEZKA_PY_BALLISTICS = os.path.join(os.getcwd(), "py_ballistics")  # zmień jeśli inna

def main():
    print("=== Program balistyczny z wykorzystaniem py_ballistics ===\n")

    print("1. Wczytaj gotową konfigurację")
    print("2. Wprowadź parametry ręcznie")
    print("3. Przeprowadź optymalizację")
    wybor = input("Wybierz opcję (1-3): ")

    if wybor == "1":
        konfiguracja = wybierz_konfiguracje()
    elif wybor == "2":
        konfiguracja = zapytaj_parametry()
    elif wybor == "3":
        przeprowadz_optymalizacje(SCIEZKA_PY_BALLISTICS)
        return
    else:
        print("Nieprawidłowy wybór.")
        return

    # Zapisz konfigurację i uruchom symulację
    sciezka_do_danych = konfiguracja.zapisz_do_pliku("dane_konfiguracji.json")
    uruchom_symulacje(SCIEZKA_PY_BALLISTICS, sciezka_do_danych)

    # Wyświetlenie wyników
    wyswietl_wyniki("wyniki.txt")

if __name__ == "__main__":
    main()

"""
# w katalogu głównym projektu
# >>> python main.py
"""
