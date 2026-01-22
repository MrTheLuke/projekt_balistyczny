import sys, os, json, logging, matplotlib.pyplot as plt
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "py_ballistics")))
from py_ballisticcalc.unit import Distance, Velocity
from py_ballisticcalc.drag_model import DragModel
from py_ballisticcalc.drag_tables import TableG7
from py_ballisticcalc import Ammo, Weapon, Shot, Calculator
from py_ballisticcalc.logger import logger

logger.setLevel(logging.WARNING)
dane = json.load(sys.stdin)
zapisz = dane.get("zapisz_wyniki", False)

v0_mps = dane["v0"] / 3.6
drag = dane["drag"]
sight_height = dane.get("sight_height", 0.05)

zero = Shot(
    weapon=Weapon(sight_height=Distance.Meter(sight_height)),
    ammo=Ammo(DragModel(drag, TableG7), mv=Velocity.MPS(v0_mps))
)

calc = Calculator()
calc.set_weapon_zero(zero, Distance.Meter(100))

traj = calc.fire(
    zero,
    trajectory_range=Distance.Meter(500),
    trajectory_step=Distance.Meter(1),
    extra_data=True
)

df = traj.dataframe(True).copy()
df["distance"] = df["distance"].apply(lambda s: float(str(s).split()[0]))
df["height"] = df["height"].apply(lambda s: float(str(s).split()[0]))

# Obszar zagrożenia
danger_space = traj.danger_space(Distance.Meter(400), Distance.Meter(0.5))

fig, ax = plt.subplots()
ax.plot(df["distance"], df["height"], label="trajektoria")
danger_space.overlay(ax)
plt.xlabel("Odległość [m]")
plt.ylabel("Wysokość [m]")
plt.title("Trajektoria z przestrzenią zagrożenia")
plt.grid(True)
plt.legend()
plt.show()

if zapisz:
    os.makedirs("wyniki", exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    prefix = f"trajektoria_zagrozenia_{ts}"
    fig.savefig(f"wyniki/{prefix}_wykres.png")
    df.to_csv(f"wyniki/{prefix}_tabela.csv", index=False)
