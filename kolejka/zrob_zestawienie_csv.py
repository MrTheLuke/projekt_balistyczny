import csv
import json
import os

ROOT = os.path.join("cloud", "wyniki_z_azure")
STATUS_PATH = os.path.join(ROOT, "status.json")
OUT = os.path.join(ROOT, "zestawienie.csv")


def safe_get(d, path, default=None):
    cur = d
    for p in path:
        if not isinstance(cur, dict) or p not in cur:
            return default
        cur = cur[p]
    return cur


def main():
    status_map = {}
    if os.path.isfile(STATUS_PATH):
        with open(STATUS_PATH, "r", encoding="utf-8") as f:
            s = json.load(f)
        for z in s.get("zadania", []):
            status_map[z.get("id")] = z

    rows = []
    for zad_id in sorted(os.listdir(ROOT)):
        folder = os.path.join(ROOT, zad_id)
        if not os.path.isdir(folder) or zad_id.startswith("_"):
            continue

        wynik_path = os.path.join(folder, "wynik.json")
        st = status_map.get(zad_id, {})

        row = {
            "id": zad_id,
            "status": st.get("status", "UNKNOWN"),
            "czas_start": st.get("czas_start", ""),
            "czas_koniec": st.get("czas_koniec", ""),
            "kat_startowy_deg": "",
            "predkosc_poczatkowa_mps": "",
            "zasieg_m": "",
            "czas_lotu_s": "",
            "blad": st.get("blad", "")
        }

        if os.path.isfile(wynik_path):
            with open(wynik_path, "r", encoding="utf-8") as f:
                d = json.load(f)
            row["kat_startowy_deg"] = safe_get(d, ["parametry_wejsciowe", "kat_startowy_deg"], "")
            row["predkosc_poczatkowa_mps"] = safe_get(d, ["parametry_wejsciowe", "predkosc_poczatkowa_mps"], "")
            row["zasieg_m"] = safe_get(d, ["wynik_symulacji", "zasieg_m"], "")
            row["czas_lotu_s"] = safe_get(d, ["wynik_symulacji", "czas_lotu_s"], "")

            # jeśli w statusie nie ma OK/ERROR, a wynik istnieje, ustaw OK
            if row["status"] == "UNKNOWN":
                row["status"] = "OK"

        rows.append(row)

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "id", "status", "czas_start", "czas_koniec",
                "kat_startowy_deg", "predkosc_poczatkowa_mps",
                "zasieg_m", "czas_lotu_s", "blad"
            ]
        )
        writer.writeheader()
        writer.writerows(rows)

    print("Zapisano:", OUT)


if __name__ == "__main__":
    main()
