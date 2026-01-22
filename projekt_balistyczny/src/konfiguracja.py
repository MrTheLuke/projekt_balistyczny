import json

class Konfiguracja:
    def __init__(self):
        self.predkosc_poczatkowa = 800.0
        self.masa = 0.008
        self.opor_powietrza = 0.15

    @staticmethod
    def z_pliku_json(sciezka):
        with open(sciezka, "r") as f:
            dane = json.load(f)

        k = Konfiguracja()
        k.predkosc_poczatkowa = dane.get("predkosc_poczatkowa", dane.get("v0", 800))
        k.masa = dane.get("masa", dane.get("mass", 0.008))
        k.opor_powietrza = dane.get("opor_powietrza", dane.get("drag", 0.15))
        return k
