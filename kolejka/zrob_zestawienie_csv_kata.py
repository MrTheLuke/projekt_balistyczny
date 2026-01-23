import csv
import json
import os

BASE_OUT = os.path.join("cloud", "wyniki_kolejka")
IN_JSON = os.path.join(BASE_OUT, "wyniki_zbiorcze.json")
OUT_CSV = os.path.join(BASE_OUT, "zestawienie.csv")

def safe_get(d, path, default=""):
    cur = d
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur

def main():
    if not os.path.isfile(IN_JSON):
        raise FileNotFoundError("Brak cloud/wyniki_kolejka/wyniki_zbiorcze.json. Uruchom najpierw kolejkę.")

    with open(IN_JSON, "r", encoding="utf-8") as f:
        wyniki = json.load(f)

    fields = [
        "id", "status", "czas_start", "czas_koniec",
        "kat_startowy_deg", "predkosc_poczatkowa_mps", "drag", "target_distance",
        "hold_mil", "horizontal_range_m",
        "required_barrel_elevation_rad", "zero_barrel_elevation_rad",
        "blad"
    ]

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()

        for r in wyniki:
            ws = r.get("wynik_symulacji") or {}
            row = {
                "id": r.get("id", ""),
                "status": r.get("status", ""),
                "czas_start": r.get("czas_start", ""),
                "czas_koniec": r.get("czas_koniec", ""),
                "kat_startowy_deg": r.get("kat_startowy_deg", ""),
                "predkosc_poczatkowa_mps": r.get("predkosc_poczatkowa_mps", ""),
                "drag": r.get("drag", ""),
                "target_distance": r.get("target_distance", ""),
                "hold_mil": ws.get("hold_mil", ""),
                "horizontal_range_m": ws.get("horizontal_range_m", ""),
                "required_barrel_elevation_rad": ws.get("required_barrel_elevation_rad", ""),
                "zero_barrel_elevation_rad": ws.get("zero_barrel_elevation_rad", ""),
                "blad": (r.get("blad", "") or "")[:200].replace("\n", " ")
            }
            w.writerow(row)

    print(f"Zapisano: {OUT_CSV}")

if __name__ == "__main__":
    main()
