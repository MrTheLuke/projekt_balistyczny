import json
import os
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

DOMYSLNY_IMAGE = "balistyka:1"

def wczytaj_zadania(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def zapisz_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def run_cmd(cmd, timeout=None):
    p = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
    return p.returncode, p.stdout, p.stderr

def przygotuj_folder_zadania(base_out, zadanie):
    task_id = zadanie.get("id", "bez_id")
    out_dir = os.path.join(base_out, task_id)
    in_dir = os.path.join(out_dir, "wejscie")
    wyn_dir = os.path.join(out_dir, "wyniki")

    os.makedirs(in_dir, exist_ok=True)
    os.makedirs(wyn_dir, exist_ok=True)

    # parametry.json dla kontenera
    param_path = os.path.join(in_dir, "parametry.json")
    zapisz_json(zadanie, param_path)

    return out_dir, in_dir, wyn_dir, param_path

def uruchom_jedno_zadanie(image, base_out, zadanie):
    task_id = zadanie.get("id", "bez_id")
    start = datetime.now().isoformat()

    out_dir, in_dir, wyn_dir, param_path = przygotuj_folder_zadania(base_out, zadanie)


    in_dir_abs = os.path.abspath(in_dir)
    wyn_dir_abs = os.path.abspath(wyn_dir)


    # Kontener czyta: /wejscie/parametry.json
    # Kontener zapisuje: /wyniki/wynik.json + trajektoria*.png
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{in_dir_abs}:/wejscie",
        "-v", f"{wyn_dir_abs}:/wyniki",
        image
    ]



    rc, stdout, stderr = run_cmd(cmd)

    koniec = datetime.now().isoformat()

    wynik_json_path = os.path.join(wyn_dir, "wynik.json")
    status = "ERROR"
    wynik = None

    if os.path.isfile(wynik_json_path):
        try:
            with open(wynik_json_path, "r", encoding="utf-8") as f:
                wynik = json.load(f)
            status = wynik.get("status", "ERROR")
        except Exception:
            status = "ERROR"

    # log per zadanie
    log_path = os.path.join(out_dir, "log.txt")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("CMD:\n")
        f.write(" ".join(cmd) + "\n\n")
        f.write("STDOUT:\n")
        f.write(stdout[-4000:] if isinstance(stdout, str) else "")
        f.write("\n\nSTDERR:\n")
        f.write(stderr[-4000:] if isinstance(stderr, str) else "")

    # zwrot do zestawienia
    return {
        "id": task_id,
        "status": status if rc == 0 else "ERROR",
        "czas_start": start,
        "czas_koniec": koniec,
        "kat_startowy_deg": zadanie.get("kat_startowy_deg"),
        "predkosc_poczatkowa_mps": zadanie.get("predkosc_poczatkowa_mps"),
        "drag": zadanie.get("drag"),
        "target_distance": zadanie.get("target_distance"),
        "blad": (None if (rc == 0 and status == "OK") else (stderr[-2000:] if isinstance(stderr, str) else "ERROR")),
        "wynik_symulacji": (wynik.get("wynik_symulacji") if isinstance(wynik, dict) else None)
    }

def main():
    image = os.environ.get("DOCKER_IMAGE", DOMYSLNY_IMAGE)
    max_parallel = int(os.environ.get("MAX_PARALLEL", "3"))

    zadania_path = os.path.join("kolejka", "zadania.json")
    base_out = os.path.join("cloud", "wyniki_kolejka")

    if not os.path.isfile(zadania_path):
        raise FileNotFoundError("Brak kolejka/zadania.json. Uruchom najpierw: python3 kolejka/generuj_zadania.py")

    zadania = wczytaj_zadania(zadania_path)
    os.makedirs(base_out, exist_ok=True)

    print(f">>> IMAGE: {image}")
    print(f">>> MAX_PARALLEL: {max_parallel}")
    print(f">>> Liczba zadań: {len(zadania)}")
    print(f">>> Wyniki: {base_out}")

    wyniki = []
    with ThreadPoolExecutor(max_workers=max_parallel) as ex:
        fut_map = {ex.submit(uruchom_jedno_zadanie, image, base_out, z): z for z in zadania}
        for fut in as_completed(fut_map):
            r = fut.result()
            wyniki.append(r)
            print(f"OK: {r['id']} status={r['status']} v={r['predkosc_poczatkowa_mps']} kat={r['kat_startowy_deg']}")

    # zapis zbiorczy (JSON)
    out_all = os.path.join(base_out, "wyniki_zbiorcze.json")
    zapisz_json(sorted(wyniki, key=lambda x: x["id"]), out_all)
    print(f">>> Zapisano: {out_all}")

if __name__ == "__main__":
    main()
