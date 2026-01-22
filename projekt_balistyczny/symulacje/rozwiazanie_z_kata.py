import sys, os, json, logging, copy, math
import matplotlib.pyplot as plt
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "py_ballistics")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from py_ballisticcalc.unit import Distance, Velocity, Angular
from py_ballisticcalc.drag_model import DragModel
from py_ballisticcalc.drag_tables import TableG7
from py_ballisticcalc import Ammo, Weapon, Shot, Calculator
from py_ballisticcalc.logger import logger
from serializacja import zapisz_dane_msgpack, wczytaj_dane_msgpack

logger.setLevel(logging.WARNING)
NAZWA_PROGRAMU = "rozwiazanie_z_kata"

# Wyświetlenie historii
print("--- Poprzednie wyniki symulacji ---")
historia = wczytaj_dane_msgpack(NAZWA_PROGRAMU)
if not historia:
    print("Brak zapisanych wyników.")
else:
    for i, w in enumerate(sorted(historia, key=lambda x: x['data'])):
        print(f"\n[{i+1}] {w['data']}")
        print(f"  Dystans: {w['target_distance_m']} m")
        print(f"  Kąt: {w['look_angle_deg']}°")
        print(f"  Korekta względem zera: {w['hold_mil']:.2f} mil")

# Dane wejściowe
dane = json.load(sys.stdin)
zapisz = dane.get("zapisz_wyniki", False)

v0_mps = dane["v0"] / 3.6
drag = dane["drag"]
sight_height = dane.get("sight_height", 0.05)
target_distance = Distance.Meter(dane.get("target_distance", 500))
look_angle = Angular.Degree(dane.get("look_angle", 25.0))

zero = Shot(
    weapon=Weapon(sight_height=Distance.Meter(sight_height)),
    ammo=Ammo(DragModel(drag, TableG7), mv=Velocity.MPS(v0_mps))
)

calc = Calculator()
calc.set_weapon_zero(zero, Distance.Meter(100))

new_shot = copy.copy(zero)
new_shot.look_angle = look_angle
new_elevation = calc.barrel_elevation_for_target(new_shot, target_distance)

hold = Angular.Mil(
    (new_elevation >> Angular.Mil) - (zero.weapon.zero_elevation >> Angular.Mil)
)

horizontal = Distance(
    math.cos(new_shot.look_angle >> Angular.Radian) * target_distance.unit_value,
    target_distance.units
)

print("--- PARAMETRY SYMULACJI ---")
print(f"Odległość do celu: {target_distance.unit_value:.2f} m")
print(f"Kąt patrzenia: {look_angle}")
print(f"Uniesienie lufy (wymagane): {new_elevation}")
print(f"Uniesienie lufy dla zera: {zero.weapon.zero_elevation}")
print(f"Korekta względem zera: {hold}")
print(f"Poziomy zasięg do celu: {horizontal.unit_value:.2f} m")

total_range = Distance.Meter(target_distance.unit_value + 200)
new_shot.relative_angle = hold
card = calc.fire(new_shot, trajectory_range=total_range)

df = card.dataframe(True).drop(['height', 'energy', 'ogw', 'drag', 'flag'], axis=1)
print("\n--- TABELA TRAJEKTORII ---")
print(df.set_index("distance"))

card.plot()
plt.show()

if zapisz:
    os.makedirs("wyniki", exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    prefix = f"{NAZWA_PROGRAMU}_{ts}"
    df.to_csv(f"wyniki/{prefix}_tabela.csv", index=False)

    zapisz_dane_msgpack(NAZWA_PROGRAMU, {
        "data": ts,
        "target_distance_m": target_distance.unit_value,
        "look_angle_deg": look_angle.unit_value,
        "required_barrel_elevation_rad": new_elevation.unit_value,
        "zero_barrel_elevation_rad": zero.weapon.zero_elevation.unit_value,
        "hold_mil": hold.unit_value,
        "horizontal_range_m": horizontal.unit_value,
        "v0_kmh": dane["v0"],
        "drag": drag
    })
