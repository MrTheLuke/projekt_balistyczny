# symulacja.py
# Plik odpowiedzialny za uruchomienie symulacji balistycznej przez interfejs py_ballistics

import os
import subprocess
import numpy as np
import matplotlib.pyplot as plt
import datetime
import json

# Funkcja odpowiedzialna za wykonanie symulacji balistycznej
# przy użyciu zewnętrznego projektu py_ballistics
def wykonaj_symulacje(konfiguracja):
    """
    Funkcja wykonuje symulację na podstawie dostarczonej konfiguracji.
    Argument:
        konfiguracja (dict): Słownik z parametrami pocisku i warunków.
    """
    # Zapisywanie konfiguracji tymczasowej do pliku JSON (lub TOML jeśli wymagane)
    tymczasowy_plik = "dane/tymczasowa_konfiguracja.json"
    with open(tymczasowy_plik, "w") as f:
        json.dump(konfiguracja, f)

    # Upewniamy się, że ścieżka do py_ballistics została podana poprawnie (np. wirtualne środowisko)
    sciezka_do_pyballistics = konfiguracja.get("sciezka_pyballistics", "../py_ballistics")
    skrypt_wywolujacy = os.path.join(sciezka_do_pyballistics, "run_simulation.py")

    if not os.path.isfile(skrypt_wywolujacy):
        print("Nie znaleziono skryptu run_simulation.py w py_ballistics.")
        return

    # Wywołanie symulacji przez subprocess (lub os.system, ale subprocess jest bezpieczniejszy)
    print("\n[INFO] Uruchamianie symulacji...")
    try:
        wynik = subprocess.run([
            "python", skrypt_wywolujacy, tymczasowy_plik
        ], capture_output=True, text=True, check=True)

        print("\n[WYNIK SYMULACJI - Terminal]")
        print(wynik.stdout)

        # Zapisywanie wyników do pliku
        teraz = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        plik_wyniku = f"wyniki/wynik_{teraz}.txt"
        with open(plik_wyniku, "w") as f:
            f.write(wynik.stdout)

        print(f"\n[INFO] Wyniki zapisane w: {plik_wyniku}")

    except subprocess.CalledProcessError as e:
        print("\n[BŁĄD SYMULACJI]")
        print(e.stderr)

# Komentarz do uruchamiania:
# Program można wywołać poprzez interfejs terminalowy np. komendą:
# python main.py
