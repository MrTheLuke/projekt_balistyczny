# symulacje/zerowanie_proste.py

import sys
import os
import json
import logging
from datetime import datetime
# import matplotlib.pyplot as plt  # wykresy zakomentowane

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "py_ballistics")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from py_ballisticcalc.unit import Distance, Velocity, Angular
from py_ballisticcalc.drag_model import DragModel
from py_ballisticcalc.drag_tables import TableG7
from py_ballisticcalc import Ammo, Weapon, Shot, Calculator
from py_ballisticcalc.logger import logger

from serializacja import zapisz_dane_msgpack, wczytaj_dane_msgpack

logger.setLevel(logging.WARNING)
NAZWA_PROGRAMU = "zerowanie_proste"

# === Wyświetl wcześniejsze symulacje ===
print("--- Poprzednie wyniki symulacji ---")
wczesniejsze = wczytaj_dane_msgpack(NAZWA_PROGRAMU)
if not wczesniejsze:
    print("Brak zapisanych wyników.")
else:
    for i, wynik in enumerate(sorted(wczesniejsze, key=lambda x: x['data'])):
        print(f"\n[{i+1}] {wynik['data']}")
        print(f"  Odległość zera: {wynik['zero_distance_m']} m")
        print(f"  Prędkość: {wynik['v0_kmh']} km/h ({wynik['v0_mps']:.2f} m/s)")
        print(f"  Kąt: {wynik['barrel_elevation_deg']:.5f}° / {wynik['barrel_elevation_rad']:.5f} rad")

# === Główne dane ===
dane = json.load(sys.stdin)
zapisz = dane.get("zapisz_wyniki", False)
v0_kmh = dane["v0"]
v0_mps = v0_kmh / 3.6
drag = dane["drag"]
zero_distance = Distance.Meter(dane.get("zero_distance", 100.0))
sight_height = dane.get("sight_height", 0.05)

if zero_distance.unit_value > 300:
    print("Uwaga: dystans zerowania może być za duży dla wybranej amunicji.")

# Konfiguracja strzału
zero = Shot(
    weapon=Weapon(sight_height=Distance.Meter(sight_height)),
    ammo=Ammo(DragModel(drag, TableG7), mv=Velocity.MPS(v0_mps))
)
calc = Calculator()

# Wyznaczenie kąta
try:
    traj_range = Distance.Meter(zero_distance.unit_value + 200)
    calc._calc.trajectory_range = traj_range
    zero_elevation = calc.set_weapon_zero(zero, zero_distance)
except Exception as e:
    print(f"Błąd wyznaczania zerowania: {e}")
    sys.exit(1)

zero_deg = zero_elevation >> Angular.Degree
zero_rad = zero_elevation >> Angular.Radian

print(f"Prędkość początkowa: {v0_kmh} km/h ({v0_mps:.2f} m/s)")
print(f"Podniesienie lufy dla zera {zero_distance.unit_value:.1f} m: {zero_deg:.5f}° ({zero_rad:.5f} rad)")

# === Zapis wyników do pliku JSON oraz binarnego (msgpack) ===
if zapisz:
    os.makedirs("wyniki", exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    prefix = f"{NAZWA_PROGRAMU}_{ts}"

    # JSON
    with open(f"wyniki/{prefix}_wyniki.json", "w") as f:
        json.dump({
            "zero_distance_m": zero_distance.unit_value,
            "barrel_elevation_deg": round(zero_deg, 5),
            "barrel_elevation_rad": round(zero_rad, 5),
            "v0_kmh": round(v0_kmh, 2),
            "v0_mps": round(v0_mps, 5),
            "drag_coefficient": drag
        }, f, indent=4)

    # MSGPACK
    zapisz_dane_msgpack(NAZWA_PROGRAMU, {
        "data": ts,
        "zero_distance_m": zero_distance.unit_value,
        "barrel_elevation_deg": float(zero_deg),
        "barrel_elevation_rad": float(zero_rad),
        "v0_kmh": float(v0_kmh),
        "v0_mps": float(v0_mps),
        "drag_coefficient": float(drag)
    })
