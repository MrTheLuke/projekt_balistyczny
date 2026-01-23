import json
import os
import sys
import subprocess
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


def wczytaj_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def zapisz_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def wydobadz_json_ze_stdout(stdout_text):
    """
    Wiele skryptów CLI wypisuje logi + JSON.
    Szukamy OSTATNIEGO obiektu JSON w stdout i próbujemy go zparsować.
    """
    s = stdout_text.strip()
    if not s:
        return None

    # szybka próba: cały stdout jest JSON
    try:
        return json.loads(s)
    except Exception:
        pass

    # wolniejsza: znajdź ostatnie '{' i próbuj parsować od tego miejsca
    last_brace = s.rfind("{")
    while last_brace != -1:
        candidate = s[last_brace:]
        try:
            return json.loads(candidate)
        except Exception:
            last_brace = s.rfind("{", 0, last_brace)
    return None


def narysuj_trajektorie(wynik, folder, ident):

    """
    Obsługuje:
      wynik["trajektoria"]["x_m"], ["y_m"] lub ["x"],["y"]
    """
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
    ident = "lokalnie"
    if isinstance(wynik, dict):
        ident = str(wynik.get("id") or wynik.get("task_id") or "lokalnie")
    out = os.path.join(folder, f"trajektoria_{ident}.png")

    plt.savefig(out, dpi=200, bbox_inches="tight")
    plt.close()
    return out


def uruchom_cli(sciezka_skryptu, parametry):
    """
    Uruchamia skrypt jako CLI:
      python <skrypt>
    i podaje parametry jako JSON na stdin.
    """
    inp = json.dumps(parametry, ensure_ascii=False)
    p = subprocess.run(
        [sys.executable, sciezka_skryptu],
        input=inp,
        text=True,
        capture_output=True
    )
    return p.returncode, p.stdout, p.stderr


def main():
    tryb, wejscie, folder_wyniki = wybierz_sciezki()
    os.makedirs(folder_wyniki, exist_ok=True)
    out_json = os.path.join(folder_wyniki, "wynik.json")

    print(f"=== START SYMULACJI (tryb: {tryb}) ===")
    print(">>> [INFO] Wejście:", wejscie)
    print(">>> [INFO] Wyniki:", folder_wyniki)

    parametry = wczytaj_json(wejscie)
    scen = wczytaj_json(SCENARIUSZE_PATH)
    cfg = scen.get(parametry.get("scenariusz", "scenariusz_1"))
    if not cfg:
        raise RuntimeError("Brak scenariusza w cloud/scenariusze.json")

    # aliasy kluczy (często różne nazwy w skryptach)
    if "kat_startowy_deg" in parametry and "kat_deg" not in parametry:
        parametry["kat_deg"] = parametry["kat_startowy_deg"]
    # scenariusz_1 (rozwiazanie_z_kata.py) oczekuje v0 w km/h
    if "predkosc_poczatkowa_mps" in parametry and "v0" not in parametry:
        parametry["v0"] = float(parametry["predkosc_poczatkowa_mps"]) * 3.6

    # wymagane przez py_ballisticcalc: BC musi być > 0
    if "drag" not in parametry:
        parametry["drag"] = 0.2
    if isinstance(parametry.get("drag"), (int, float)) and parametry["drag"] <= 0:
        parametry["drag"] = 0.2



    typ = cfg.get("typ")
    if typ != "cli":
        raise RuntimeError("Na tym etapie obsługujemy tylko typ=cli")

    skrypt_rel = cfg["skrypt"]
    skrypt_abs = os.path.join(repo_root(), skrypt_rel)

    if not os.path.isfile(skrypt_abs):
        raise FileNotFoundError(f"Nie ma skryptu: {skrypt_abs}")



    rc, out, err = uruchom_cli(skrypt_abs, parametry)
    wynik_surowy = wydobadz_json_ze_stdout(out)

    status = "OK" if (rc == 0 and wynik_surowy is not None) else "ERROR"
    ident = parametry.get("id", "lokalnie")
    wykres = narysuj_trajektorie(wynik_surowy, folder_wyniki, ident) if status == "OK" else None


    wynik = {
        "status": status,
        "czas_uruchomienia": datetime.now().isoformat(),
        "scenariusz": {
            "nazwa": parametry.get("scenariusz", "scenariusz_1"),
            "opis": cfg.get("opis", ""),
            "typ": "cli",
            "skrypt": skrypt_rel
        },
        "parametry_wejsciowe": parametry,
        "wynik_symulacji": wynik_surowy,
        "pliki": {"trajektoria_png": wykres},
        "debug": {
            "returncode": rc,
            "stderr_tail": (err[-2000:] if isinstance(err, str) else None),
            "stdout_tail": (out[-2000:] if isinstance(out, str) else None)
        }
    }

    zapisz_json(wynik, out_json)
    print(f"=== KONIEC SYMULACJI, status={status}, zapis: {out_json} ===")


if __name__ == "__main__":
    main()
