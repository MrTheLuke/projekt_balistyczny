# src/interfejs.py

from src.konfiguracja import Konfiguracja
import os

def wczytaj_float(opis, domyslna, jednostka, min_val=None, max_val=None):
    """
    Funkcja pomocnicza – odczytuje liczbę zmiennoprzecinkową z terminala
    """
    while True:
        try:
            wpis = input(f"{opis} [{domyslna} {jednostka}]: ")
            if not wpis:
                return domyslna
            wartosc = float(wpis)
            if (min_val is not None and wartosc < min_val) or (max_val is not None and wartosc > max_val):
                print(f"Podaj wartość z zakresu [{min_val}, {max_val}]")
                continue
            return wartosc
        except ValueError:
            print("Nieprawidłowa liczba. Spróbuj ponownie.")

def konfiguruj_recznie():
    print("\n--- Konfiguracja ręczna ---")
    konfig = Konfiguracja()
    konfig.masa = wczytaj_float("Masa pocisku", konfig.masa, "kg", 0.001, 100)
    konfig.predkosc_poczatkowa = wczytaj_float("Prędkość początkowa", konfig.predkosc_poczatkowa, "m/s", 1, 2000)
    konfig.kat_wystrzalu = wczytaj_float("Kąt wystrzału", konfig.kat_wystrzalu, "stopni", 0, 90)
    konfig.opor_powietrza = wczytaj_float("Opór powietrza", konfig.opor_powietrza, "-", 0.0, 1.0)
    konfig.wysokosc_startowa = wczytaj_float("Wysokość startowa", konfig.wysokosc_startowa, "m", 0, 10000)
    konfig.g = wczytaj_float("Przyspieszenie ziemskie", konfig.g, "m/s²", 0, 20)
    return konfig

def wybierz_konfiguracje():
    print("=== KONFIGURACJA SYMULACJI ===")
    print("1 - Wczytaj z pliku tekstowego (.txt)")
    print("2 - Wybierz gotową konfigurację (AK-47, moździerz, czołg)")
    print("3 - Wprowadź dane ręcznie")

    wybor = input("Wybierz opcję [1/2/3]: ").strip()

    if wybor == "1":
        sciezka = input("Podaj ścieżkę do pliku konfiguracyjnego (.txt): ").strip()
        if not os.path.exists(sciezka):
            print("Plik nie istnieje.")
            return None
        return Konfiguracja.z_pliku_txt(sciezka)

    elif wybor == "2":
        print("\n--- Gotowe konfiguracje ---")
        print("1 - AK-47")
        print("2 - Moździerz")
        print("3 - Pocisk czołgowy")
        gotowe = {"1": "ak47", "2": "mozdzierz", "3": "czolg"}
        podwybor = input("Wybierz rodzaj pocisku: ").strip()
        return Konfiguracja.gotowa_konfiguracja(gotowe.get(podwybor, "ak47"))

    elif wybor == "3":
        return konfiguruj_recznie()
    
    else:
        print("Nieprawidłowy wybór.")
        return None

def interfejs_startowy():
    konfig = wybierz_konfiguracje()
    if konfig:
        print("\nKonfiguracja zakończona.")
        sciezka_json = konfig.zapisz_do_pliku("konfiguracja_symulacji.json")
        print(f"Zapisano konfigurację do: {sciezka_json}")
        return sciezka_json
    else:
        print("Nie udało się utworzyć konfiguracji.")
        return None
