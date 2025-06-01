# src/konfiguracja.py

import json
import os

class Konfiguracja:
    """
    Klasa przechowująca dane wejściowe do symulacji.
    Umożliwia zapis do pliku w formacie JSON (dla py_ballistics) oraz odczyt z pliku tekstowego.
    """

    def __init__(self):
        # Domyślne parametry symulacji (SI)
        self.masa = 0.01              # kg
        self.predkosc_poczatkowa = 300.0  # m/s
        self.kat_wystrzalu = 45.0     # stopnie
        self.opor_powietrza = 0.1     # bezwymiarowe
        self.wysokosc_startowa = 0.0  # m
        self.g = 9.81                 # m/s^2

    def zapisz_do_pliku(self, sciezka_json):
        """
        Zapisuje konfigurację do pliku JSON zgodnie z wymaganiami py_ballistics.
        """
        dane = {
            "mass": self.masa,
            "v0": self.predkosc_poczatkowa,
            "angle": self.kat_wystrzalu,
            "drag": self.opor_powietrza,
            "height": self.wysokosc_startowa,
            "gravity": self.g,
            "units": "metric"  # <- wymuszenie jednostek metrycznych
        }

        with open(sciezka_json, "w") as f:
            json.dump(dane, f, indent=4)

        return os.path.abspath(sciezka_json)

    @staticmethod
    def z_pliku_txt(sciezka):
        """
        Tworzy obiekt konfiguracji na podstawie pliku tekstowego.
        Format pliku:
        masa=0.02
        predkosc_poczatkowa=600
        kat_wystrzalu=60
        opor_powietrza=0.2
        wysokosc_startowa=0
        g=9.81
        """
        konfig = Konfiguracja()
        with open(sciezka, "r") as f:
            for linia in f:
                if '=' in linia:
                    klucz, wartosc = linia.strip().split("=")
                    setattr(konfig, klucz, float(wartosc))
        return konfig

    @staticmethod
    def gotowa_konfiguracja(nazwa):
        """
        Zwraca predefiniowaną konfigurację pocisku.
        """
        konfig = Konfiguracja()

        if nazwa == "ak47":
            konfig.masa = 0.008
            konfig.predkosc_poczatkowa = 715
            konfig.kat_wystrzalu = 45
            konfig.opor_powietrza = 0.15
        elif nazwa == "mozdzierz":
            konfig.masa = 2.0
            konfig.predkosc_poczatkowa = 150
            konfig.kat_wystrzalu = 80
            konfig.opor_powietrza = 0.25
        elif nazwa == "czolg":
            konfig.masa = 10.0
            konfig.predkosc_poczatkowa = 1200
            konfig.kat_wystrzalu = 10
            konfig.opor_powietrza = 0.05

        return konfig
