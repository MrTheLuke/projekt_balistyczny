# Projekt balistyczny – symulacje lokalne i chmurowe (Docker + Azure VM)

Projekt umożliwia uruchamianie symulacji balistycznych:
- lokalnie (Docker),
- z użyciem kolejkowania + równoległego uruchamiania zadań,
- oraz z wykorzystaniem maszyny wirtualnej Azure (VM).

Symulacje wykorzystują silnik balistyczny (`py_ballistics`)

---

## 1. Klonowanie projektu

git clone https://github.com/MrTheLuke/projekt_balistyczny.git
cd projekt_balistyczny

## 3. Budowa obrazu Docker
Jednorazowo:
bash docker/uruchom.sh build

Domyślny obraz:
nazwa: balistyka
tag: 1

## 4. Pojedyncza symulacja (Docker)
Uruchomienie jednej symulacji na podstawie ustawień w cloud/parametry.json:
bash docker/uruchom.sh single

Wyniki zapisywane są w:
cloud/wyniki/wynik.json
cloud/wyniki/trajektoria.png (jeśli dostępna)

## 5. Kolejkowanie i równoległość (Docker)
5.1 Przygotowanie zadań do kolejki - generowanie zestawu symulacji.
python3 kolejka/generuj_zadania.py

Plik wynikowy:
kolejka/zadania.json

5.2 Uruchomienie kolejki (równolegle)
MAX_PARALLEL=4 bash docker/uruchom.sh kolejka

Wyniki:
cloud/wyniki_kolejka/
 ├── zadanie_01/
 ├── zadanie_02/
 ├── ...
 └── wyniki_zbiorcze.json
Każde zadanie ma własny katalog z wynik.json.

## 6. Analiza wyników
python3 kolejka/zrob_zestawienie_csv.py

Wynik:
cloud/wyniki_z_azure/zestawienie.csv

Wykresy zbiorcze
python3 analiza/wykresy_z_csv.py
Wynik:
cloud/wyniki_z_azure/wykresy/

## 7. Uruchamianie na Azure VM
Założenie: połączenie z konkretną maszyną wirtualną jest skonfigurowane a sama maszyna ma potrzebne pakiety i repo z projektem

7.1 Uruchomienie kolejki na VM
FORCE=1 MAX_PARALLEL=2 python3 kolejka/uruchom_kolejke_vm.py

Skrypt automatycznie:
- uruchamia VM (jeśli wyłączona),
- loguje się przez SSH,
- uruchamia Docker i kolejkę,
- pobiera wyniki,
- wyłącza VM.

7.3 Konfiguracja VM
Pliki odpowiedzialne za integrację z Azure:

kolejka/
 ├── uruchom_kolejke_vm.py     # logika start/stop VM, SSH, docker
azure/
 ├── config_vm.json           # nazwa VM, resource group, region
docker/
 ├── uruchom.sh               # wrapper build/single/kolejka


## 10. Uwagi końcowe
Jeśli symulacja zwraca RangeError, oznacza to fizycznie
nieosiągalne parametry (np. zbyt mała prędkość).

Parametry wejściowe nie są sztucznie korygowane –
błędy pochodzą bezpośrednio z modelu fizycznego.





##
##
##
## STRUKTURA PROJEKTU

## 1.
projekt_balistyczny jest kontynuacją projektu uruchamiającego bibliotekę z symulatorem balistycznym napisaną w pythonie, którego pierwotna wersja była:
- uruchamiana lokalnie,
- realizowana głównie jako skrypty CLI (czytające dane ze stdin, wypisujące wyniki na stdout).

W ramach rozwinięcia o elementy "chmurowe" został wykorzystany jeden z programów symulacyjnych.

## 2. Struktura katalogów
projekt_balistyczny/
│
├── projekt_balistyczny/        # oryginalny projekt symulatora
│   ├── symulacje/              # skrypty
│   ├── py_ballistics/          # biblioteka py_ballisticcalc
│   ├── src/                    # narzędzia pomocnicze (serializacja itp.)
│   └── ...
│
├── cloud/                      # WARSTWA URUCHOMIENIOWA
│   ├── parametry.json          # dane wejściowe pojedynczej symulacji
│   ├── scenariusze.json        # mapowanie scenariusz → skrypt CLI
│   ├── uruchom_jedna_symulacje.py
│   ├── wyniki/                 # wyniki pojedynczego uruchomienia
│   └── wyniki_kolejka/         # wyniki symulacji wsadowych
│
├── kolejka/                    # KOLEJKOWANIE I RÓWNOLEGŁOŚĆ
│   ├── przygotuj_zadania.py    # generowanie zestawu zadań
│   ├── uruchom_kolejke_docker.py
│   ├── uruchom_kolejke_vm.py
│   └── zadania.json
│
├── docker/                     # DOCKER I AUTOMATYZACJA (NOWE)
│   ├── Dockerfile
│   └── uruchom.sh
│
├── analiza/                    # ANALIZA WYNIKÓW (NOWE)
│   └── wykresy_z_csv.py
│
└── README.md


## 3. Warstwa uruchomieniowa (cloud)
cloud/uruchom_jedna_symulacje.py

Pełni rolę:
- adaptera między Dockerem / VM / lokalnym uruchomieniem,
- kontrolera błędów,
- generatora wykresów trajektorii.

Główne zadania:
- Wykrywa tryb pracy (lokalnie, w Dockerze, na VM)
- Wczytuje: parametry i scenariusze.
- Na podstawie scenariusza wybiera konkretny skrypt i go uruchamia
- wydobywa JSON z stdout (nawet jeśli są logi).
- Tworzy: wynik.json, trajektoria.png (jeśli dostępna).

## 4. Kolejkowanie i równoległość
kolejka/przygotuj_zadania.py
Generuje:
- kombinacje kąt × prędkość,
- plik zadania.json.

kolejka/uruchom_kolejke_docker.py
- uruchamia wiele kontenerów Dockera równolegle,
- każde zadanie ma osobny katalog z wynikami

kolejka/uruchom_kolejke_vm.py
- Rozszerzenie o:   start / stop Azure VM, SSH, uruchamianie Dockera zdalnie.


## 6. Docker i automatyzacja
docker/Dockerfile
- instalacja:   numpy, scipy, matplotlib, typing_extensions, msgpack,

docker/uruchom.sh
- skrypty pod działania jedną komendą:
-- bash docker/uruchom.sh build
-- bash docker/uruchom.sh single
-- bash docker/uruchom.sh kolejka


## 7. Analiza wyników
analiza/wykresy_z_csv.py
- przetwarza zbiorcze wyniki
- generuje wykresy porównawcze