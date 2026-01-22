import sys, os
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "py_ballistics")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from py_ballisticcalc.drag_model import BCPoint, DragModelMultiBC
from py_ballisticcalc.drag_tables import TableG1, TableG7
from serializacja import zapisz_dane_msgpack

os.makedirs("wyniki", exist_ok=True)

CD_PROG = 3000  # próg CD

class ModelBalistyczny:
    def __init__(self, nazwa, bc_points, tabela, masa_grain, srednica_inch, styl=None, szerokosc=2):
        self.nazwa = nazwa
        self.bc_points = bc_points
        self.tabela = tabela
        self.masa = masa_grain
        self.srednica = srednica_inch
        self.styl = styl
        self.szerokosc = szerokosc

    def generuj_model(self):
        return DragModelMultiBC(self.bc_points, self.tabela, weight=self.masa, diameter=self.srednica)

    def zakresy_mach_cd_powyzej(self, model, prog=CD_PROG):
        mach_lista = [p.Mach for p in model.drag_table if p.CD >= prog]
        if not mach_lista:
            return None
        return [round(min(mach_lista), 3), round(max(mach_lista), 3)]


modele = [
    ModelBalistyczny(
        "G1 Single BC",
        [BCPoint(0.462, Mach=1)],
        TableG1,
        masa_grain=168,
        srednica_inch=0.308,
        styl="solid"
    ),
    ModelBalistyczny(
        "G1 Multi BC (Sierra)",
        [
            BCPoint(.462, V=792.48),
            BCPoint(.4545, V=716.28),
            BCPoint(.4145, V=563.88),
            BCPoint(.405, V=487.68),
        ],
        TableG1,
        masa_grain=168,
        srednica_inch=0.308,
        styl="dashed"
    ),
    ModelBalistyczny(
        "G7 Single BC",
        [BCPoint(0.224, Mach=1)],
        TableG7,
        masa_grain=168,
        srednica_inch=0.308,
        styl="dashdot"
    ),
    ModelBalistyczny(
        "G7 Multi BC (Litz)",
        [
            BCPoint(.211, V=457.2),
            BCPoint(.214, V=609.6),
            BCPoint(.222, V=762.0),
            BCPoint(.226, V=914.4),
        ],
        TableG7,
        masa_grain=168,
        srednica_inch=0.308,
        styl="dotted"
    ),
]

fig, ax = plt.subplots(figsize=(10, 6))
ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
wyniki = []

for model in modele:
    dm = model.generuj_model()
    dane = [{"Mach": p.Mach, "CD": p.CD} for p in dm.drag_table]
    df = pd.DataFrame(dane)
    df.plot(x="Mach", y="CD", label=model.nazwa, linestyle=model.styl, linewidth=model.szerokosc, ax=ax)


    przekroczenia = df[df["CD"] >= CD_PROG]
    if not przekroczenia.empty:
        graniczne = przekroczenia.iloc[[0, -1]]
        ax.scatter(graniczne["Mach"], graniczne["CD"], color="red", s=40, zorder=5, label=None)


    zakres = model.zakresy_mach_cd_powyzej(dm, prog=CD_PROG)
    wyniki.append({
        "model": model.nazwa,
        "zakres_mach_CD>3000": zakres
    })

#próg
ax.axhline(CD_PROG, color='red', linestyle='--', label='CD = 3000')


ax.set_title("Porównanie modeli oporu (DragModelMultiBC)")
ax.set_ylabel("CD (współczynnik oporu)")
ax.set_xlabel("Mach")
ax.spines[['right', 'top']].set_visible(False)
ax.grid(True)
ax.legend()

sciezka_png = f"wyniki/wielokrotny_model_bc_{ts}_wykres.png"
plt.savefig(sciezka_png)
plt.show()

print("\n=== PRZEDZIAŁY Macha (CD >= 3000) ===")
for w in wyniki:
    if w['zakres_mach_CD>3000']:
        print(f"{w['model']}: CD >= 3000 dla Mach ∈ [{w['zakres_mach_CD>3000'][0]}, {w['zakres_mach_CD>3000'][1]}]")
    else:
        print(f"{w['model']}: brak wartości CD >= 3000")

zapisz_dane_msgpack("wielokrotny_model_bc", {
    "data": ts,
    "wyniki": wyniki
})