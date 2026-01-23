import os
import sys
import pkgutil
import importlib
import inspect

def main():
    repo = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # repo może mieć kod w ./projekt_balistyczny/...
    kandydaci = [
        repo,
        os.path.join(repo, "projekt_balistyczny"),
    ]
    for p in kandydaci:
        if p not in sys.path:
            sys.path.insert(0, p)

    try:
        import symulacje
    except Exception:
        print("Nie mogę zaimportować pakietu 'symulacje'.")
        print("Sprawdź czy istnieje folder projekt_balistyczny/symulacje/ i czy ma __init__.py.")
        raise

    print("Znalezione moduły i funkcje w 'symulacje':\n")
    for m in pkgutil.iter_modules(symulacje.__path__):
        mod_name = f"symulacje.{m.name}"
        try:
            mod = importlib.import_module(mod_name)
        except Exception as e:
            print(f"- {mod_name}: import ERROR ({e})")
            continue

        fns = []
        for name, obj in vars(mod).items():
            if callable(obj) and inspect.isfunction(obj) and obj.__module__ == mod.__name__:
                fns.append((name, str(inspect.signature(obj))))

        if not fns:
            print(f"- {mod_name}: (brak funkcji)")
        else:
            print(f"- {mod_name}:")
            for name, sig in fns:
                print(f"    {name}{sig}")
        print()

if __name__ == "__main__":
    main()
