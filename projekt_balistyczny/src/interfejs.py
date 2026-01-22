import os
from src.konfiguracja import Konfiguracja

def wybierz_konfiguracje():
    folder = "konfiguracje"
    pliki = [f for f in os.listdir(folder) if f.endswith(".json")]

    if not pliki:
        print("Brak dostępnych konfiguracji.")
        return None

    print("--- Dostępne konfiguracje ---")
    for i, f in enumerate(pliki):
        print(f"{i+1}. {f}")

    while True:
        wybor = input("Wybierz numer konfiguracji: ")
        try:
            idx = int(wybor) - 1
            if 0 <= idx < len(pliki):
                return Konfiguracja.z_pliku_json(os.path.join(folder, pliki[idx]))
        except:
            pass
        print("Błąd wyboru.")
