import json
import os
from datetime import datetime

SCIEZKA_WEJSCIE_DOCKER = "/wejscie/parametry.json"
SCIEZKA_WYNIKI_DOCKER = "/wyniki"

SCIEZKA_WEJSCIE_LOKALNIE = os.path.join("cloud", "parametry.json")
SCIEZKA_WYNIKI_LOKALNIE = os.path.join("cloud", "wyniki")


def wybierz_sciezki():
    if os.path.isdir(SCIEZKA_WYNIKI_DOCKER) and os.path.isdir("/wejscie"):
        return "DOCKER/VM", SCIEZKA_WEJSCIE_DOCKER, SCIEZKA_WYNIKI_DOCKER
    return "LOKALNIE", SCIEZKA_WEJSCIE_LOKALNIE, SCIEZKA_WYNIKI_LOKALNIE


def wczytaj_parametry(sciezka):
    with open(sciezka, "r", encoding="utf-8") as f:
        return json.load(f)


def uruchom_symulacje(parametry):
    # TODO: podmienić na prawdziwe wywołanie najprostszego scenariusza z repo,
    # np. subprocess.run(["python3", "main.py", ...], check=True)

    return {
        "status": "OK",
        "czas_uruchomienia": datetime.now().isoformat(),
        "parametry_wejsciowe": parametry,
        "wynik_symulacji": {
            "zasieg_m": 123.45,
            "czas_lotu_s": 6.78
        }
    }


def zapisz_wynik(wynik, sciezka):
    os.makedirs(os.path.dirname(sciezka), exist_ok=True)
    with open(sciezka, "w", encoding="utf-8") as f:
        json.dump(wynik, f, indent=4, ensure_ascii=False)


def main():
    tryb, sciezka_wejscie, folder_wyniki = wybierz_sciezki()
    sciezka_wynik_json = os.path.join(folder_wyniki, "wynik.json")

    print(f"=== START SYMULACJI (tryb: {tryb}) ===")
    print(">>> [INFO] Wejście:", sciezka_wejscie)
    print(">>> [INFO] Wyniki:", folder_wyniki)

    if not os.path.exists(sciezka_wejscie):
        raise FileNotFoundError(f"Brak pliku wejściowego: {sciezka_wejscie}")

    parametry = wczytaj_parametry(sciezka_wejscie)
    wynik = uruchom_symulacje(parametry)
    zapisz_wynik(wynik, sciezka_wynik_json)

    print(f"=== KONIEC SYMULACJI, wynik zapisany w: {sciezka_wynik_json} ===")


if __name__ == "__main__":
    main()
