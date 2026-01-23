import os
import sys
import importlib
import inspect

def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def znajdz_symulacje_dir():
    # Twoja struktura: repo/projekt_balistyczny/symulacje
    d = os.path.join(repo_root(), "projekt_balistyczny", "symulacje")
    if os.path.isdir(d):
        return d, os.path.join(repo_root(), "projekt_balistyczny")
    # awaryjnie: repo/symulacje
    d2 = os.path.join(repo_root(), "symulacje")
    if os.path.isdir(d2):
        return d2, repo_root()
    raise FileNotFoundError("Nie znalazłem folderu symulacje/")

def czy_wyglada_na_CLI(tekst):
    podejrzane = [
        "json.load(sys.stdin)",
        "sys.stdin",
        "input(",
        "argparse",
        "if __name__ == '__main__'",
        "parser.add_argument",
    ]
    return any(p in tekst for p in podejrzane)

def main():
    sym_dir, import_base = znajdz_symulacje_dir()

    if import_base not in sys.path:
        sys.path.insert(0, import_base)

    print("Folder symulacje:", sym_dir)
    print("Import base:", import_base)
    print()

    pliki = [p for p in os.listdir(sym_dir) if p.endswith(".py") and p != "__init__.py"]
    pliki.sort()

    print("Moduły w symulacje/ (z pominięciem CLI):\n")

    for plik in pliki:
        path = os.path.join(sym_dir, plik)
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            src = f.read()

        if czy_wyglada_na_CLI(src):
            print(f"- {plik}: POMINIĘTY (wygląda na CLI / czyta stdin / input)")
            continue

        mod_name = "symulacje." + os.path.splitext(plik)[0]
        try:
            mod = importlib.import_module(mod_name)
        except Exception as e:
            print(f"- {mod_name}: import ERROR ({e})")
            continue

        funkcje = []
        for name, obj in vars(mod).items():
            if callable(obj) and inspect.isfunction(obj) and obj.__module__ == mod.__name__:
                funkcje.append((name, str(inspect.signature(obj))))

        if not funkcje:
            print(f"- {mod_name}: (brak funkcji)")
        else:
            print(f"- {mod_name}:")
            for name, sig in funkcje:
                print(f"    {name}{sig}")
    print()

if __name__ == "__main__":
    main()
