import subprocess
import json
import os

def uruchom_symulacje(typ, konfiguracja, zapisz_wyniki):
    dane = {
        "v0": konfiguracja.predkosc_poczatkowa,
        "mass": konfiguracja.masa,
        "drag": konfiguracja.opor_powietrza,
        "zapisz_wyniki": zapisz_wyniki
    }

    dodatkowe = {}

    if typ == 1:
        dystans = input("Podaj odległość zerowania [m] (np. 100): ")
        try:
            dodatkowe["zero_distance"] = float(dystans)
        except:
            dodatkowe["zero_distance"] = 100.0

    if typ == 2 or typ == 3 or typ == 4:
        wysokosc = input("Podaj wysokość celownika [m] (np. 0.05): ")
        try:
            dodatkowe["sight_height"] = float(wysokosc)
        except:
            dodatkowe["sight_height"] = 0.05

    if typ == 3 or typ == 4:
        dystans = input("Podaj odległość do celu [m]: ")
        try:
            dodatkowe["target_distance"] = float(dystans)
        except:
            dodatkowe["target_distance"] = 500

    if typ == 4:
        kat = input("Podaj kąt patrzenia [stopnie]: ")
        try:
            dodatkowe["look_angle"] = float(kat)
        except:
            dodatkowe["look_angle"] = 25.0

    dane.update(dodatkowe)

    pliki = {
        1: "zerowanie_proste.py",
        2: "trajektoria_zagrozenia.py",
        3: "rozwiazanie_z_karty.py",
        4: "rozwiazanie_z_kata.py"
    }

    sciezka = os.path.join("symulacje", pliki[typ])
    subprocess.run(["python3", sciezka], input=json.dumps(dane).encode())
