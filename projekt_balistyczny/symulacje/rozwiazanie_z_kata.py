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


def policz(dane):
    """
    Zwraca słownik z wynikami obliczeń + (opcjonalnie) trajektorię w postaci list.
    Nie używa pandas.
    """
    v0_kmh = dane["v0"]
    v0_mps = v0_kmh / 3.6

    drag = dane["drag"]
    sight_height = dane.get("sight_height", 0.05)
    target_distance = float(dane.get("target_distance", 500))
    look_angle_deg = float(dane.get("look_angle", 25.0))

    zero = Shot(
        weapon=Weapon(sight_height=Distance.Meter(sight_height)),
        ammo=Ammo(DragModel(drag, TableG7), mv=Velocity.MPS(v0_mps))
    )

    calc = Calculator()
    calc.set_weapon_zero(zero, Distance.Meter(100))

    new_shot = copy.copy(zero)
    new_shot.look_angle = Angular.Degree(look_angle_deg)
    new_elevation = calc.barrel_elevation_for_target(new_shot, Distance.Meter(target_distance))

    hold = Angular.Mil(
        (new_elevation >> Angular.Mil) - (zero.weapon.zero_elevation >> Angular.Mil)
    )

    horizontal = Distance(
        math.cos(new_shot.look_angle >> Angular.Radian) * target_distance,
        Distance.Meter(1).units
    )

    total_range = Distance.Meter(target_distance + 200)
    new_shot.relative_angle = hold
    card = calc.fire(new_shot, trajectory_range=total_range)

    # Trajektoria bez pandas: bierzemy z card.trajectory (lista punktów)
    traj_x = []
    traj_y = []
    traj_d = []

    traj = getattr(card, "trajectory", None)
    if traj:
        for p in traj:
            dist = getattr(p, "distance", None)

            # spróbuj kilku nazw osi Y (różne wersje biblioteki)
            yobj = None
            for cand in ("drop", "height", "y", "path"):
                if hasattr(p, cand):
                    yobj = getattr(p, cand)
                    break

            if dist is not None:
                try:
                    traj_d.append(float(dist >> Distance.Meter))
                except Exception:
                    pass

            if yobj is not None:
                try:
                    traj_y.append(float(yobj >> Distance.Meter))
                except Exception:
                    # czasem to już jest float
                    try:
                        traj_y.append(float(yobj))
                    except Exception:
                        pass

        traj_x = traj_d[:]

    # jeśli y nie wyszło, wyrównaj długości (żeby nie robić śmieci)
    if traj_x and traj_y and len(traj_x) != len(traj_y):
        n = min(len(traj_x), len(traj_y))
        traj_x = traj_x[:n]
        traj_y = traj_y[:n]


    wynik = {
        "target_distance_m": target_distance,
        "look_angle_deg": look_angle_deg,
        "required_barrel_elevation_rad": float(new_elevation >> Angular.Radian),
        "zero_barrel_elevation_rad": float(zero.weapon.zero_elevation >> Angular.Radian),
        "hold_mil": float(hold >> Angular.Mil),
        "horizontal_range_m": float(horizontal >> Distance.Meter),
        "v0_kmh": v0_kmh,
        "drag": drag,
        "trajektoria": {
            "x_m": traj_x,
            "y_m": traj_y
        }
    }
    return wynik


def main():
    # Dane wejściowe (stdin JSON)
    dane = json.load(sys.stdin)

    tryb_json = bool(dane.get("tryb_json", False))
    zapisz = bool(dane.get("zapisz_wyniki", False))

    if not tryb_json:
        # historia tylko w trybie interaktywnym
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

    wynik = policz(dane)

    if tryb_json:
        # W chmurze: czysty JSON na stdout
        print(json.dumps(wynik, ensure_ascii=False))
        return

    # Tryb lokalny (stare zachowanie – printy i wykres)
    print("--- PARAMETRY SYMULACJI ---")
    print(f"Odległość do celu: {wynik['target_distance_m']:.2f} m")
    print(f"Kąt patrzenia: {wynik['look_angle_deg']}°")
    print(f"Uniesienie lufy (wymagane): {wynik['required_barrel_elevation_rad']:.6f} rad")
    print(f"Uniesienie lufy dla zera: {wynik['zero_barrel_elevation_rad']:.6f} rad")
    print(f"Korekta względem zera: {wynik['hold_mil']:.3f} mil")
    print(f"Poziomy zasięg do celu: {wynik['horizontal_range_m']:.2f} m")

    # wykres z trajektorii (jeśli jest)
    x = wynik["trajektoria"]["x_m"]
    y = wynik["trajektoria"]["y_m"]
    if x and y and len(x) == len(y):
        plt.figure()
        plt.plot(x, y)
        plt.xlabel("x [m]")
        plt.ylabel("y [m]")
        plt.title("Trajektoria")
        plt.show()

    if zapisz:
        os.makedirs("wyniki", exist_ok=True)
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        zapisz_dane_msgpack(NAZWA_PROGRAMU, {
            "data": ts,
            "target_distance_m": wynik["target_distance_m"],
            "look_angle_deg": wynik["look_angle_deg"],
            "required_barrel_elevation_rad": wynik["required_barrel_elevation_rad"],
            "zero_barrel_elevation_rad": wynik["zero_barrel_elevation_rad"],
            "hold_mil": wynik["hold_mil"],
            "horizontal_range_m": wynik["horizontal_range_m"],
            "v0_kmh": wynik["v0_kmh"],
            "drag": wynik["drag"]
        })


if __name__ == "__main__":
    main()
