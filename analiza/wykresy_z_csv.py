import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def znajdz_cloud_dir():
    """
    Repo może mieć:
      - ./cloud
    albo:
      - ./projekt_balistyczny/cloud
    Zwraca ścieżkę do katalogu cloud.
    """
    kandydaci = [
        os.path.join(os.getcwd(), "cloud"),
        os.path.join(os.getcwd(), "projekt_balistyczny", "cloud"),
    ]
    for c in kandydaci:
        if os.path.isdir(c):
            return c
    raise FileNotFoundError("Nie znalazłem katalogu 'cloud/'. Sprawdź strukturę repo.")


def wczytaj_csv(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


def to_float(x):
    try:
        return float(x)
    except Exception:
        return None


def main():
    cloud_dir = znajdz_cloud_dir()
    csv_path = os.path.join(cloud_dir, "wyniki_z_azure", "zestawienie.csv")
    out_dir = os.path.join(cloud_dir, "wyniki_z_azure", "wykresy")

    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"Brak pliku: {csv_path}")

    os.makedirs(out_dir, exist_ok=True)
    rows = wczytaj_csv(csv_path)

    ok = [r for r in rows if r.get("status") == "OK"]

    kat = [to_float(r.get("kat_startowy_deg")) for r in ok]
    zasieg = [to_float(r.get("zasieg_m")) for r in ok]
    tlotu = [to_float(r.get("czas_lotu_s")) for r in ok]
    t_exec = [to_float(r.get("czas_trwania_s")) for r in ok]

    # 1) zasięg vs kąt
    plt.figure()
    plt.plot(kat, zasieg, marker="o")
    plt.xlabel("Kąt [deg]")
    plt.ylabel("Zasięg [m]")
    plt.title("Zasięg vs kąt")
    plt.savefig(os.path.join(out_dir, "zasieg_vs_kat.png"), dpi=200, bbox_inches="tight")
    plt.close()

    # 2) czas lotu vs kąt
    plt.figure()
    plt.plot(kat, tlotu, marker="o")
    plt.xlabel("Kąt [deg]")
    plt.ylabel("Czas lotu [s]")
    plt.title("Czas lotu vs kąt")
    plt.savefig(os.path.join(out_dir, "czas_lotu_vs_kat.png"), dpi=200, bbox_inches="tight")
    plt.close()

    # 3) czas wykonania
    if any(x is not None for x in t_exec):
        plt.figure()
        plt.plot(list(range(len(t_exec))), t_exec, marker="o")
        plt.xlabel("Nr zadania (kolejność w CSV)")
        plt.ylabel("Czas wykonania [s]")
        plt.title("Czas wykonania zadania (VM+Docker)")
        plt.savefig(os.path.join(out_dir, "czas_wykonania.png"), dpi=200, bbox_inches="tight")
        plt.close()

    print("Wygenerowano wykresy w:", out_dir)


if __name__ == "__main__":
    main()