import json
import os
import sys
from datetime import datetime

# wykresy
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import importlib
import pkgutil


SCIEZKA_WEJSCIE_DOCKER = "/wejscie/parametry.json"
SCIEZKA_WYNIKI_DOCKER = "/wyniki"

SCIEZKA_WEJSCIE_LOKALNIE = os.path.join("cloud", "parametry.json")
SCIEZKA_WYNIKI_LOKALNIE = os.path.join("cloud", "wyniki")


def wybierz_sciezki():
    if os.path.isdir(SCIEZKA_WYNIKI_DOCKER) and os.path.isdir("/wejscie"):
        return "DOCKER/VM", SCIEZKA_WEJSCIE_DOCKER, SCIEZKA_WYNIKI_DOCKER
    return "LOKALNIE", SCIEZKA_WEJSCIE_LOKALNIE, SCIEZKA_WYNIKI_LOKALNIE


def wczytaj_json(sciezka):
    with open(sciezka, "r", encoding="utf-8") as f:
        return json.load(f)


def zapisz_json(dane, sciezka):
    os.makedirs(os.path.dirname(sciezka), exist_ok=True)
    with open(sciezka, "w", encoding="utf-8") as f:
        json.dump(dane, f, indent=4, ensure_ascii=False)


def narysuj_wykres_trajektorii(traj, folder_wyniki):
    x = None
    y = None

    if isinstance(traj, dict):
        if "x_m" in traj and "y_m" in traj:
            x = traj["x_m"]
            y = traj["y_m"]
        elif "punkty" in traj and isinstance(traj["punkty"], list):
            x = [p.get("x_m") for p in traj["punkty"]]
            y = [p.get("y_m") for p in traj["punkty"]]

    if not x or not y:
        return None

    plt.figure()
    plt.plot(x, y)
    plt.xlabel("x [m]")
    plt.ylabel("y [m]")
    plt.title("Trajektoria")
    sciezka_png = os.path.join(folder_wyniki, "trajektoria.png")
    plt.savefig(sciezka_png, dpi=200, bbox_inches="tight")
    plt.close()
    return sciezka_png


def dodaj_sciezke_dla_symulacje():
    """
    Szuka katalogu 'symulacje' w repo (w kontenerze /app) i dodaje jego rodzica do sys.path,
    żeby 'import symulacje' działał niezależnie od struktury.
    """
    # repo root: .../cloud/uruchom_jedna_symulacje.py -> .../
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    kandydaci = [
        repo_root,
        os.path.join(repo_root, "projekt_balistyczny"),
        os.path.join(repo_root, "src"),
    ]

    # szybkie sprawdzenie kandydatów
    for base in kandydaci:
        sym_dir = os.path.join(base, "symulacje")
        if os.path.isdir(sym_dir):
            if base not in sys.path:
                sys.path.insert(0, base)
            return base, sym_dir

    # jeśli nie znaleziono w typowych miejscach, zrób płytkie szukanie (max głębokość 3)
    for root, dirs, _files in os.walk(repo_root):
        depth = root[len(repo_root):].count(os.sep)
        if depth > 3:
            dirs[:] = []
            continue
        if "symulacje" in dirs:
            base = root
            sym_dir = os.path.join(root, "symulacje")
            if base not in sys.path:
                sys.path.insert(0, base)
            return base, sym_dir

    return None, None


def znajdz_i_uruchom_symulacje_z_repo(parametry):
    kandydaci_funkcji = ["symuluj", "uruchom", "run", "main", "simulate"]

    base, sym_dir = dodaj_sciezke_dla_symulacje()
    if not sym_dir:
        raise RuntimeError(
            "Nie znalazłem katalogu 'symulacje/' w repo. "
            "Sprawdź czy istnieje (np. projekt_balistyczny/symulacje/)."
        )

    try:
        import symulacje  # pakiet z repo (po dodaniu sys.path)
    except Exception as e:
        raise RuntimeError(
            "Znalazłem katalog 'symulacje/', ale import się nie udał.\n"
            "Upewnij się, że 'symulacje' jest pakietem (czyli ma plik __init__.py)."
        ) from e

    for m in pkgutil.iter_modules(symulacje.__path__):
        nazwa_modulu = f"symulacje.{m.name}"
        try:
            mod = importlib.import_module(nazwa_modulu)
        except Exception:
            continue

        for fn_name in kandydaci_funkcji:
            fn = getattr(mod, fn_name, None)
            if callable(fn):
                try:
                    wynik = fn(parametry)
                    return nazwa_modulu, fn_name, wynik
                except TypeError:
                    continue
                except Exception:
                    continue

    raise RuntimeError(
        "Nie udało się znaleźć uruchamialnej funkcji w 'symulacje/'.\n"
        "Wymagane: moduł w symulacje/ z funkcją np. symuluj(parametry: dict)->dict."
    )


def main():
    tryb, sciezka_wejscie, folder_wyniki = wybierz_sciezki()
    os.makedirs(folder_wyniki, exist_ok=True)
    sciezka_wynik_json = os.path.join(folder_wyniki, "wynik.json")

    print(f"=== START SYMULACJI (tryb: {tryb}) ===")
    print(">>> [INFO] Wejście:", sciezka_wejscie)
    print(">>> [INFO] Wyniki:", folder_wyniki)

    parametry = wczytaj_json(sciezka_wejscie)

    modul, funkcja, wynik_surowy = znajdz_i_uruchom_symulacje_z_repo(parametry)

    sciezka_wykresu = None
    if isinstance(wynik_surowy, dict):
        traj = wynik_surowy.get("trajektoria") or wynik_surowy.get("traj") or wynik_surowy.get("trajectory")
        if traj is not None:
            sciezka_wykresu = narysuj_wykres_trajektorii(traj, folder_wyniki)

    wynik = {
        "status": "OK",
        "czas_uruchomienia": datetime.now().isoformat(),
        "wywolanie": {"modul": modul, "funkcja": funkcja},
        "parametry_wejsciowe": parametry,
        "wynik_symulacji": wynik_surowy,
        "pliki": {"trajektoria_png": sciezka_wykresu}
    }

    zapisz_json(wynik, sciezka_wynik_json)
    print(f"=== KONIEC SYMULACJI, wynik zapisany w: {sciezka_wynik_json} ===")


if __name__ == "__main__":
    main()