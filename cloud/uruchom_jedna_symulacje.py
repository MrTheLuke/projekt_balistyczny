import json
import math
import os
from datetime import datetime

# -------------------------------------------------------
# Tryb działania:
# - Docker/VM: wejście w /wejscie, wyjście w /wyniki
# - Lokalnie: wejście w cloud/parametry.json, wyjście w cloud/wyniki/
# -------------------------------------------------------

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


def zapisz_wynik(wynik, sciezka):
    os.makedirs(os.path.dirname(sciezka), exist_ok=True)
    with open(sciezka, "w", encoding="utf-8") as f:
        json.dump(wynik, f, indent=4, ensure_ascii=False)


def symulacja_rzut_ukosny_bez_oporu(v0_mps, kat_deg, h0_m=0.0, g=9.80665):
    """
    Najprostsza realna symulacja: rzut ukośny bez oporu powietrza (SI).

    Zwraca:
    - czas_lotu_s
    - zasieg_m
    - h_max_m
    """
    theta = math.radians(float(kat_deg))
    v0 = float(v0_mps)
    h0 = float(h0_m)

    vx = v0 * math.cos(theta)
    vy = v0 * math.sin(theta)

    # czas lotu: rozwiązanie y(t)=h0 + vy t - 0.5 g t^2 = 0
    # t = (vy + sqrt(vy^2 + 2 g h0))/g  (dodatni pierwiastek)
    disc = vy * vy + 2.0 * g * h0
    if disc < 0:
        # fizycznie nie powinno wyjść dla g>0 i h0>=0
        disc = 0.0
    t_f = (vy + math.sqrt(disc)) / g

    zasieg = vx * t_f

    # maks wysokość: h_max = h0 + vy^2/(2g) jeśli vy>0, inaczej h0
    if vy > 0:
        h_max = h0 + (vy * vy) / (2.0 * g)
    else:
        h_max = h0

    return {
        "czas_lotu_s": round(t_f, 6),
        "zasieg_m": round(zasieg, 6),
        "h_max_m": round(h_max, 6)
    }


def uruchom_symulacje(parametry):
    """
    Wersja A: realna symulacja (najprostszy model).
    Parametry oczekiwane w JSON:
      - kat_startowy_deg
      - predkosc_poczatkowa_mps
    Opcjonalnie:
      - wysokosc_startowa_m
    """
    kat = parametry.get("kat_startowy_deg")
    v0 = parametry.get("predkosc_poczatkowa_mps")
    h0 = parametry.get("wysokosc_startowa_m", 0.0)

    if kat is None or v0 is None:
        raise ValueError("Brak wymaganych pól w parametry.json: kat_startowy_deg oraz predkosc_poczatkowa_mps")

    wynik_modelu = symulacja_rzut_ukosny_bez_oporu(v0_mps=v0, kat_deg=kat, h0_m=h0)

    return {
        "status": "OK",
        "czas_uruchomienia": datetime.now().isoformat(),
        "model": "rzut_ukosny_bez_oporu",
        "parametry_wejsciowe": {
            "kat_startowy_deg": kat,
            "predkosc_poczatkowa_mps": v0,
            "wysokosc_startowa_m": h0
        },
        "wynik_symulacji": wynik_modelu
    }


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