import sys, os, json, logging
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "py_ballistics")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from py_ballisticcalc.unit import Distance, Velocity, Angular
from py_ballisticcalc.drag_model import DragModel
from py_ballisticcalc.drag_tables import TableG7
from py_ballisticcalc import Ammo, Weapon, Shot, Calculator, Wind
from py_ballisticcalc.logger import logger
from serializacja import zapisz_dane_msgpack, wczytaj_dane_msgpack

logger.setLevel(logging.WARNING)
NAZWA_PROGRAMU = "rozwiazanie_z_karty"

# Wyświetlenie historii
print("--- Poprzednie wyniki symulacji ---")
historia = wczytaj_dane_msgpack(NAZWA_PROGRAMU)
if not historia:
    print("Brak zapisanych wyników.")
else:
    for i, w in enumerate(sorted(historia, key=lambda x: x['data'])):
        print(f"\n[{i+1}] {w['data']}")
        print(f"  Dystans: {w['target_distance_m']} m")
        print(f"  Drop przed: {w['target_drop_before']} m")
        print(f"  Drop po: {w['target_drop_after']} m")
        print(f"  Korekta: {w['hold_radians']:.5f} rad")

# Wczytanie danych
dane = json.load(sys.stdin)
zapisz = dane.get("zapisz_wyniki", False)

v0_mps = dane["v0"] / 3.6
drag = dane["drag"]
sight_height = dane.get("sight_height", 0.05)
target_distance = Distance.Meter(dane.get("target_distance", 500))

zero = Shot(
    weapon=Weapon(sight_height=Distance.Meter(sight_height)),
    ammo=Ammo(DragModel(drag, TableG7), mv=Velocity.MPS(v0_mps)),
    winds=[Wind(Velocity.MPS(2.24), Angular.OClock(3))]
)

calc = Calculator()
calc.set_weapon_zero(zero, Distance.Meter(100))

range_card = calc.fire(zero, trajectory_range=Distance.Meter(1000))
new_target = range_card.get_at_distance(target_distance)

drop_m = new_target.target_drop.unit_value
distance_m = new_target.distance.unit_value
hold = new_target.drop_adj

range_card.shot.relative_angle = Angular(-hold.unit_value, hold.units)
adjusted_result = calc.fire(range_card.shot, trajectory_range=Distance.Meter(1000))
adjusted = adjusted_result.get_at_distance(target_distance)
adjusted_drop_m = adjusted.target_drop.unit_value

print(f"Tor zera trafia {drop_m:.2f} m przy dystansie {distance_m:.2f} m")
print(f"Korekta celownika dla dystansu {distance_m:.2f} m to {hold}")
print(f"Po korekcie: upadek przy dystansie {adjusted.distance.unit_value:.2f} m wynosi {adjusted_drop_m:.2f} m")

if zapisz:
    os.makedirs("wyniki", exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    prefix = f"{NAZWA_PROGRAMU}_{ts}"

    with open(f"wyniki/{prefix}_wyniki.json", "w") as f:
        json.dump({
            "target_distance_m": distance_m,
            "target_drop_before": drop_m,
            "hold_radians": hold.unit_value,
            "target_drop_after": adjusted_drop_m
        }, f, indent=4)

    zapisz_dane_msgpack(NAZWA_PROGRAMU, {
        "data": ts,
        "target_distance_m": distance_m,
        "target_drop_before": drop_m,
        "hold_radians": hold.unit_value,
        "target_drop_after": adjusted_drop_m,
        "v0_kmh": dane["v0"],
        "drag": drag
    })
