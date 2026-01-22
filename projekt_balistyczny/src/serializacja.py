# src/serializacja.py
import msgpack
import os
from datetime import datetime

SCIEZKA_FOLDERU = "wyniki/serializacja"

def zapisz_dane_msgpack(nazwa_programu, dane: dict):
    os.makedirs(SCIEZKA_FOLDERU, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nazwa_pliku = f"{nazwa_programu}_{ts}.msgpack"
    pelna_sciezka = os.path.join(SCIEZKA_FOLDERU, nazwa_pliku)
    with open(pelna_sciezka, "wb") as f:
        packed = msgpack.packb(dane, use_bin_type=True)
        f.write(packed)

def wczytaj_dane_msgpack(nazwa_programu):
    dane_lista = []
    if not os.path.exists(SCIEZKA_FOLDERU):
        return dane_lista

    for plik in os.listdir(SCIEZKA_FOLDERU):
        if plik.startswith(nazwa_programu) and plik.endswith(".msgpack"):
            with open(os.path.join(SCIEZKA_FOLDERU, plik), "rb") as f:
                dane = msgpack.unpackb(f.read(), raw=False)
                dane_lista.append(dane)
    return dane_lista
