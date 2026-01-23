import json
import os
import sys
import importlib
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


SCIEZKA_WEJSCIE_DOCKER = "/wejscie/parametry.json"
SCIEZKA_WYNIKI_DOCKER = "/wyniki"

SCIEZKA_WEJSCIE_LOKALNIE = os.path.join("cloud", "parametry.json")
SCIEZKA_WYNIKI_LOKALNIE = os.path.join("cloud", "wyniki")

SCENARIUSZE_PATH = os.path.join("cloud", "scenariusze.json")


def wybierz_sciezki():
    if os.path.isdir(SCIEZKA_WYNIKI_DOCKER) and os.path.isdir("/wejscie"):
        return "DOCKER/VM", SCIEZKA_WEJSCIE_DOCKER, SCIEZKA_WYNIKI_DOCKER
    return "LOKALNIE", SCIEZKA_WEJSCIE_LOKALNIE, SCIEZKA_WYNIKI_LOKALNIE


def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def dodaj_repo_do_sys_path():
    root = repo_root()
    if root not in sys.path:
        sys.path.insert(0, root)


def wczytaj_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def zapisz_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def narysuj_trajektorie(wynik, folder):
    if not isinstance(wynik, dict):
        return None

    traj = wynik.get("trajektoria") or wynik.get("traj") or wynik.get("trajectory")
    if not isinstance(traj, dict):
        return None

    x = traj.get("x_m") or traj.get("x")
    y = traj.get("y_m") or traj.get("y")
    if not x or not y:
        return None

    plt.figure()
    plt.plot(x, y)
    plt.xlabel("x [m]")
    plt.ylabel("y [m]")
    plt.title("Trajektoria")
    out = os.path.join(folder, "trajektoria.png")
    plt.savefig(out, dpi=200, bbox_inches="tight")
    plt.close()
    return out


def main():
    tryb, wejscie, folder_wyniki = wybierz_sciezki()
    os.makedirs(folder_wyniki, exist_ok=True)

    print(f"=== START SYMULACJI (tryb: {tryb}) ===")
    print(">>> [INFO] Wejście:", wejscie)
    print(">>> [INFO] Wyniki:", folder_wyniki)

    parametry = wczytaj_json(wejscie)
    scen = wczytaj_json(SCENARIUSZE_PATH)
    cfg = scen["scenariusz_1"]

    modul = cfg["modul"]
    funkcja = cfg["funkcja"]

    # aliasy kluczy (częsty problem w Twoim repo)
    if "kat_startowy_deg" in parametry and "kat_deg" not in parametry:
        parametry["kat_deg"] = parametry["kat_startowy_deg"]
    if "predkosc_poczatkowa_mps" in parametry and "v0_mps" not in parametry:
        parametry["v0_mps"] = parametry["predkosc_poczatkowa_mps"]
    if "predkosc_poczatkowa_mps" in parametry and "v0" not in parametry:
        parametry["v0"] = parametry["predkosc_poczatkowa_mps"]

    dodaj_repo_do_sys_path()
    mod = importlib.import_module(modul)
    fn = getattr(mod, funkcja)

    wynik_surowy = fn(parametry)

    wykres = narysuj_trajektorie(wynik_surowy, folder_wyniki)

    out = {
        "status": "OK",
        "czas_uruchomienia": datetime.now().isoformat(),
        "scenariusz": {"modul": modul, "funkcja": funkcja, "opis": cfg.get("opis", "")},
        "parametry_wejsciowe": parametry,
        "wynik_symulacji": wynik_surowy,
        "pliki": {"trajektoria_png": wykres}
    }

    zapisz_json(out, os.path.join(folder_wyniki, "wynik.json"))
    print("=== KONIEC SYMULACJI ===")


if __name__ == "__main__":
    main()
