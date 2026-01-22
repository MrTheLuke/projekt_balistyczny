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
    # cloud/uruchom_jedna_symulacje.py -> repo root
    return os.path.abspath(os.path.join(os.path.dirname(file), ".."))


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


def narysuj_trajektorie(wynik_surowy, folder_wyniki):
    """
    Szukamy trajektorii w kilku typowych formatach:
      - wynik["trajektoria"]["x_m"], ["y_m"]
      - wynik["trajektoria"]["x"], ["y"]
      - wynik["trajektoria"]["punkty"] = [{"x":..,"y":..},...]
      - wynik["trajektoria"]["punkty"] = [{"x_m":..,"y_m":..},...]
    Jeśli brak danych -> None.
    """
    if not isinstance(wynik_surowy, dict):
        return None

    traj = wynik_surowy.get("trajektoria") or wynik_surowy.get("traj") or wynik_surowy.get("trajectory")
    if not isinstance(traj, dict):
        return None

    x = None
    y = None

    if "x_m" in traj and "y_m" in traj:
        x, y = traj["x_m"], traj["y_m"]
    elif "x" in traj and "y" in traj:
        x, y = traj["x"], traj["y"]
    elif "punkty" in traj and isinstance(traj["punkty"], list) and traj["punkty"]:
        p0 = traj["punkty"][0]
        if "x_m" in p0 and "y_m" in p0:
            x = [p.get("x_m") for p in traj["punkty"]]
            y = [p.get("y_m") for p in traj["punkty"]]
        elif "x" in p0 and "y" in p0:
            x = [p.get("x") for p in traj["punkty"]]
            y = [p.get("y") for p in traj["punkty"]]

    if not x or not y:
        return None

    plt.figure()
    plt.plot(x, y)
    plt.xlabel("x [m]")
    plt.ylabel("y [m]")
    plt.title("Trajektoria")
    out = os.path.join(folder_wyniki, "trajektoria.png")
    plt.savefig(out, dpi=200, bbox_inches="tight")
    plt.close()
    return out


def uruchom_scenariusz(parametry):
    """
    parametry.json może zawierać:
      - scenariusz: "scenariusz_1" (domyślnie) albo "scenariusz_2"
      - pozostałe pola zależne od Twojego symulatora
    """
    if not os.path.exists(SCENARIUSZE_PATH):
        raise FileNotFoundError(f"Brak pliku: {SCENARIUSZE_PATH}")

    scenariusze = wczytaj_json(SCENARIUSZE_PATH)
    nazwa = parametry.get("scenariusz", "scenariusz_1")




    if nazwa not in scenariusze:
        raise ValueError(f"Nieznany scenariusz: {nazwa}. Dostępne: {list(scenariusze.keys())}")

    cfg = scenariusze[nazwa]
    modul = cfg["modul"]
    funkcja = cfg["funkcja"]

    dodaj_repo_do_sys_path()

    mod = importlib.import_module(modul)
    fn = getattr(mod, funkcja, None)
    if not callable(fn):
        raise RuntimeError(f"W module '{modul}' nie ma wywoływalnej funkcji '{funkcja}'")

    wynik_surowy = fn(parametry)  # <-- uruchomienie istniejącej symulacji z repo

    # --- aliasy kluczy: żeby symulacja z repo na pewno dostała dane ---
    # (nie psujemy oryginalnych pól, tylko dopisujemy zamienniki)
    if "kat_startowy_deg" in parametry and "kat_deg" not in parametry:
        parametry["kat_deg"] = parametry["kat_startowy_deg"]
    if "predkosc_poczatkowa_mps" in parametry and "v0_mps" not in parametry:
        parametry["v0_mps"] = parametry["predkosc_poczatkowa_mps"]
    if "predkosc_poczatkowa_mps" in parametry and "v0" not in parametry:
        parametry["v0"] = parametry["predkosc_poczatkowa_mps"]


    return nazwa, cfg.get("opis", ""), modul, funkcja, wynik_surowy


def main():
    tryb, wejscie, folder_wyniki = wybierz_sciezki()
    os.makedirs(folder_wyniki, exist_ok=True)
    out_json = os.path.join(folder_wyniki, "wynik.json")

    print(f"=== START SYMULACJI (tryb: {tryb}) ===")
    print(">>> [INFO] Wejście:", wejscie)
    print(">>> [INFO] Wyniki:", folder_wyniki)
    parametry = wczytaj_json(wejscie)
    nazwa, opis, modul, funkcja, wynik_surowy = uruchom_scenariusz(parametry)

    wykres = narysuj_trajektorie(wynik_surowy, folder_wyniki)

    wynik = {
        "status": "OK",
        "czas_uruchomienia": datetime.now().isoformat(),
        "scenariusz": {"nazwa": nazwa, "opis": opis, "modul": modul, "funkcja": funkcja},
        "parametry_wejsciowe": parametry,
        "wynik_symulacji": wynik_surowy,
        "pliki": {"trajektoria_png": wykres}
    }

    zapisz_json(wynik, out_json)
    print(f"=== KONIEC SYMULACJI, wynik zapisany w: {out_json} ===")


if __name__ == "main":
    main()