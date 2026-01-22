import json
import os
import subprocess
from datetime import datetime


def run_cmd(cmd, log_path=None, check=True):
    """
    Uruchamia polecenie systemowe.
    Jeśli log_path podane, dopisuje stdout+stderr do pliku.
    """
    print(">>>", " ".join(cmd))
    if log_path:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write("\n\n===== CMD =====\n")
            f.write(" ".join(cmd) + "\n")
            f.write("===== OUTPUT =====\n")
            p = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, text=True)
            if check and p.returncode != 0:
                raise subprocess.CalledProcessError(p.returncode, cmd)
            return p.returncode
    else:
        subprocess.run(cmd, check=check)


def read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_vm_ip(rg, vm):
    cmd = ["az", "vm", "show", "-d", "-g", rg, "-n", vm, "--query", "publicIps", "-o", "tsv"]
    ip = subprocess.check_output(cmd, text=True).strip()
    if not ip:
        raise RuntimeError("Nie udało się pobrać IP VM. Sprawdź RG/VM.")
    return ip


def ssh_cmd(uservm, ip, ssh_key, remote_cmd, log_path=None, check=True):
    return run_cmd(["ssh", "-i", ssh_key, f"{uservm}@{ip}", remote_cmd], log_path=log_path, check=check)


def scp_to_vm(local_path, uservm, ip, ssh_key, remote_path, log_path=None, check=True):
    return run_cmd(["scp", "-i", ssh_key, local_path, f"{uservm}@{ip}:{remote_path}"], log_path=log_path, check=check)


def scp_from_vm(uservm, ip, ssh_key, remote_path, local_path, log_path=None, check=True):
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    return run_cmd(["scp", "-i", ssh_key, f"{uservm}@{ip}:{remote_path}", local_path], log_path=log_path, check=check)


def main():
    # --- Konfiguracja przez zmienne środowiskowe (żeby łatwo używać na różnych kontach) ---
    rg = os.environ.get("RG", "rg-balistyczny-student-norwayeast")
    vm = os.environ.get("VM", "vm-balistyczna")
    uservm = os.environ.get("USERVM", "azureuser")
    ssh_key = os.environ.get("SSH_KEY", os.path.expanduser("~/.ssh/azure_vm_key"))

    # Resume / force
    force = os.environ.get("FORCE", "0") == "1"

    # Repo na VM
    vm_repo = os.environ.get("VM_REPO", "projekt_balistyczny")
    vm_repo_path = f"~/{vm_repo}"

    # Pliki na VM
    vm_parametry_path = f"{vm_repo_path}/cloud/parametry.json"
    vm_wyniki_dir = f"{vm_repo_path}/cloud/wyniki"
    # log z uruchomienia zadania zapisujemy na VM (żeby był też w chmurze)
    vm_log_dir = f"{vm_wyniki_dir}/logi"
    # wynik zawsze jest wynik.json, ale per zadanie kopiujemy go do osobnego folderu lokalnie

    # Lokalnie
    zadania_path = os.path.join("kolejka", "zadania.json")
    lokalne_root = os.path.join("cloud", "wyniki_z_azure")
    lokalne_log_root = os.path.join(lokalne_root, "_logi")
    status_path = os.path.join(lokalne_root, "status.json")

    os.makedirs(lokalne_root, exist_ok=True)

    print(">>> Pobieram IP VM...")
    ip = get_vm_ip(rg, vm)
    print(">>> IP VM:", ip)

    zadania = read_json(zadania_path)
    print(">>> Liczba zadań:", len(zadania))

    # --- KROK 0: sprawdź repo na VM i zbuduj obraz TYLKO RAZ ---
    log_global = os.path.join(lokalne_log_root, "00_global.log")

    # a) czy repo istnieje?
    cmd_check_repo = f"test -d {vm_repo_path} && echo OK_REPO || echo BRAK_REPO"
    ssh_cmd(uservm, ip, ssh_key, cmd_check_repo, log_path=log_global, check=True)

    # Jeśli repo nie istnieje, sklonuj je
    cmd_clone_repo = (
        f"if [ ! -d {vm_repo_path} ]; then "
        f"cd ~ && git clone https://github.com/MrTheLuke/projekt_balistyczny.git {vm_repo}; "
        f"fi"
    )
    ssh_cmd(uservm, ip, ssh_key, cmd_clone_repo, log_path=log_global, check=True)

    # b) przygotuj foldery na VM
    cmd_prepare_dirs = f"mkdir -p {vm_wyniki_dir} {vm_log_dir}"
    ssh_cmd(uservm, ip, ssh_key, cmd_prepare_dirs, log_path=log_global, check=True)

    # c) build obrazu tylko raz (jeśli nie istnieje)
    cmd_build_once = (
        f"cd {vm_repo_path} && "
        f"(docker image inspect balistyka:1 >/dev/null 2>&1 && echo OBRAZ_JUZ_JEST) || "
        f"(echo BUDUJE_OBRAZ && docker build -t balistyka:1 -f docker/Dockerfile .)"
    )
    ssh_cmd(uservm, ip, ssh_key, cmd_build_once, log_path=log_global, check=True)

    # --- pętla zadań ---
    status = {
        "rg": rg,
        "vm": vm,
        "ip": ip,
        "uservm": uservm,
        "czas_start": datetime.now().isoformat(),
        "force": force,
        "zadania": []
    }

    for z in zadania:
        zad_id = z.get("id", "bez_id")
        lokalny_folder = os.path.join(lokalne_root, zad_id)
        lokalny_wynik = os.path.join(lokalny_folder, "wynik.json")
        lokalny_log = os.path.join(lokalne_log_root, f"{zad_id}.log")

        # RESUME: jeśli wynik już jest i nie FORCE, pomiń
        if (not force) and os.path.isfile(lokalny_wynik):
            print(f">>> POMIJAM {zad_id} (wynik już istnieje). Ustaw FORCE=1 aby wymusić.")
            status["zadania"].append({
                "id": zad_id,
                "status": "SKIPPED",
                "czas_start": None,
                "czas_koniec": None
            })
            continue

        print("\n==============================")
        print("ZADANIE:", zad_id)
        print("==============================")

        t0 = datetime.now().isoformat()

        # 1) zapisz parametry lokalnie do tmp
        tmp_param_path = os.path.join("cloud", "wejscie_tmp", zad_id, "parametry.json")
        os.makedirs(os.path.dirname(tmp_param_path), exist_ok=True)
        parametry = {
            "id": zad_id,
            "opis": z.get("opis", ""),
            "kat_startowy_deg": z.get("kat_startowy_deg"),
            "predkosc_poczatkowa_mps": z.get("predkosc_poczatkowa_mps"),
            "czas_uruchomienia_lokalnie": datetime.now().isoformat()
        }
        write_json(parametry, tmp_param_path)

        # 2) wyślij parametry na VM (nadpisuje cloud/parametry.json)
        ok = True
        err_msg = None

        try:
            scp_to_vm(tmp_param_path, uservm, ip, ssh_key, vm_parametry_path, log_path=lokalny_log, check=True)

            # 3) uruchom kontener na VM i zapisz log na VM + w lokalnym logu (przez SSH output)
            vm_log_one = f"{vm_log_dir}/{zad_id}.log"

            remote_run = (
                f"cd {vm_repo_path} && "
                f"echo '=== START {zad_id} ===' | tee -a {vm_log_one} && "
                f"date | tee -a {vm_log_one} && "
                f"docker run --rm "
                f"-v $(pwd)/cloud:/wejscie "
                f"-v $(pwd)/cloud/wyniki:/wyniki "
                f"balistyka:1 2>&1 | tee -a {vm_log_one} && "
                f"echo '=== KONIEC {zad_id} ===' | tee -a {vm_log_one}"
            )
            ssh_cmd(uservm, ip, ssh_key, remote_run, log_path=lokalny_log, check=True)

            # 4) pobierz wynik
            scp_from_vm(uservm, ip, ssh_key, f"{vm_wyniki_dir}/wynik.json", lokalny_wynik, log_path=lokalny_log, check=True)

            # 5) pobierz log z VM (opcjonalnie, ale wygodne do oceny projektu)
            lokalny_log_vm = os.path.join(lokalny_folder, "log_vm.txt")
            scp_from_vm(uservm, ip, ssh_key, vm_log_one, lokalny_log_vm, log_path=lokalny_log, check=False)

        except Exception as e:
            ok = False
            err_msg = str(e)

        t1 = datetime.now().isoformat()

        status["zadania"].append({
            "id": zad_id,
            "status": "OK" if ok else "ERROR",
            "czas_start": t0,
            "czas_koniec": t1,
            "lokalny_wynik": lokalny_wynik if os.path.isfile(lokalny_wynik) else None,
            "lokalny_log": lokalny_log,
            "blad": err_msg
        })

        # zapis statusu po każdym zadaniu (na wypadek przerwania)
        write_json(status, status_path)

        if ok:
            print(">>> OK:", lokalny_wynik)
        else:
            print(">>> ERROR:", zad_id)
            print(">>> Szczegóły w logu:", lokalny_log)

    status["czas_koniec"] = datetime.now().isoformat()
    write_json(status, status_path)
    print("\n=== KONIEC KOLEJKI ===")
    print("Status:", status_path)


if __name__ == "__main__":
    main()