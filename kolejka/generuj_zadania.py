import json
import os

def main():
    # Kilkanaście symulacji: kombinacje
    katy_deg = [5, 10, 15, 20]
    predkosci_mps = [600, 700, 800, 900]   # 4x4 = 16 zadań

    # Ustaw to bezpieczniej niż 4000 m (żeby mniej ERRORów)
    # Jeśli chcesz testować awarie, zwiększ target_distance.
    target_distance = 3000
    look_angle = 25.0
    drag = 0.2

    zadania = []
    i = 1
    for v in predkosci_mps:
        for kat in katy_deg:
            zadania.append({
                "id": f"zadanie_{i:02d}",
                "opis": "seria_docker",
                "tryb_json": True,
                "kat_startowy_deg": kat,
                "predkosc_poczatkowa_mps": v,
                "drag": drag,
                "target_distance": target_distance,
                "look_angle": look_angle
            })
            i += 1

    os.makedirs("kolejka", exist_ok=True)
    out_path = os.path.join("kolejka", "zadania.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(zadania, f, indent=2, ensure_ascii=False)

    print(f"Zapisano: {out_path} (liczba zadań: {len(zadania)})")

if __name__ == "__main__":
    main()
