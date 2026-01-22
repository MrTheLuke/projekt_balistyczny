from src.interfejs import wybierz_konfiguracje
from src.symulacja import uruchom_symulacje
import subprocess
import os

def main():
    print("=== Program balistyczny z wykorzystaniem py_ballisticcalc ===\n")

    konfiguracja = wybierz_konfiguracje()
    if not konfiguracja:
        print("Nie wczytano konfiguracji.")
        return

    print("\n--- Dostępne symulacje ---")
    print("1. Zerowanie proste")
    print("2. Trajektoria z przestrzenią zagrożenia")
    print("3. Rozwiązanie z karty zasięgu")
    print("4. Rozwiązanie z kąta patrzenia")
    print("5. Porównanie modeli DragModelMultiBC")

    wybor = input("Wybierz symulację (1-5): ")

    if wybor == "5":
        subprocess.run(["python3", os.path.join("symulacje", "wielokrotny_model_bc.py")])
        return

    zapisz = input("Czy zapisać wyniki do plików? (t/n): ").strip().lower()
    zapisz_wyniki = zapisz == "t"

    if wybor in ["1", "2", "3", "4"]:
        uruchom_symulacje(int(wybor), konfiguracja, zapisz_wyniki)
    else:
        print("Niepoprawny wybór.")

if __name__ == "__main__":
    main()
