set -e

# Użycie:
#   bash docker/uruchom.sh prosta
#   bash docker/uruchom.sh kolejka
#   bash docker/uruchom.sh build
#   bash docker/uruchom.sh clean
#
# Zmienne środowiskowe:
#   DOCKER_IMAGE=balistyka:1
#   MAX_PARALLEL=4

MODE="${1:-prosta}"
IMAGE="${DOCKER_IMAGE:-balistyka:1}"
MAXP="${MAX_PARALLEL:-4}"

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fix_docker_credsstore_wsl() {
  # Jeśli Docker w WSL próbuje użyć docker-credential-desktop.exe -> build/pull potrafi się wywalić.
  # Poprawiamy config JSON automatycznie (bez ręcznej konfiguracji).
  local CFG="$HOME/.docker/config.json"
  if [ -f "$CFG" ]; then
    if grep -q '"credsStore"[[:space:]]*:[[:space:]]*"desktop\.exe"' "$CFG"; then
      echo ">>> [FIX] Wykryto credsStore=desktop.exe w $CFG (problem w WSL). Usuwam wpis."
      cp "$CFG" "$CFG.bak" || true
      python3 - << 'PY'
import json, os
cfg = os.path.expanduser("~/.docker/config.json")
with open(cfg, "r", encoding="utf-8") as f:
    data = json.load(f)

# usuń globalny credsStore
data.pop("credsStore", None)

# usuń helper dla docker.io jeśli istnieje
ch = data.get("credHelpers")
if isinstance(ch, dict):
    ch.pop("docker.io", None)
    if not ch:
        data.pop("credHelpers", None)

with open(cfg, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
print("OK: zapisano poprawiony config:", cfg)
PY
    fi
  fi
}



wejscie_prepare() {
  # Jeśli użytkownik nie ma cloud/parametry.json, kopiujemy z example
  if [ ! -f "$REPO_DIR/cloud/parametry.json" ]; then
    if [ -f "$REPO_DIR/cloud/parametry.example.json" ]; then
      cp "$REPO_DIR/cloud/parametry.example.json" "$REPO_DIR/cloud/parametry.json"
      echo ">>> Skopiowano cloud/parametry.example.json -> cloud/parametry.json"
    else
      echo "ERROR: brak cloud/parametry.example.json"
      exit 1
    fi
  fi
}

build_image() {
  fix_docker_credsstore_wsl
  echo ">>> Build image: $IMAGE"
  docker build -t "$IMAGE" -f "$REPO_DIR/docker/Dockerfile" "$REPO_DIR"
}


run_prosta() {
  wejscie_prepare
  mkdir -p "$REPO_DIR/cloud/wyniki"

  # buduj jeśli obraz nie istnieje (bez wymuszania)
  if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
    build_image
  fi

  echo ">>> Run: prosta symulacja"
  docker run --rm \
    -v "$REPO_DIR/cloud:/wejscie" \
    -v "$REPO_DIR/cloud/wyniki:/wyniki" \
    "$IMAGE"

  echo ">>> Wynik (cloud/wyniki/wynik.json):"
  head -n 80 "$REPO_DIR/cloud/wyniki/wynik.json" || true

  echo ">>> Pliki w cloud/wyniki:"
  ls -la "$REPO_DIR/cloud/wyniki" || true
}

run_kolejka() {
  # buduj jeśli obraz nie istnieje
  if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
    build_image
  fi

  echo ">>> Run: kolejka + równoległość"
  echo ">>> MAX_PARALLEL=$MAXP, IMAGE=$IMAGE"

  # Generowanie zadań + uruchomienie kolejki + CSV
  python3 "$REPO_DIR/kolejka/generuj_zadania.py"
  MAX_PARALLEL="$MAXP" DOCKER_IMAGE="$IMAGE" python3 "$REPO_DIR/kolejka/uruchom_kolejke_docker.py"
  python3 "$REPO_DIR/kolejka/zrob_zestawienie_csv_kata.py"

  echo ">>> Wyniki kolejki:"
  echo "    cloud/wyniki_kolejka/wyniki_zbiorcze.json"
  echo "    cloud/wyniki_kolejka/zestawienie.csv"
  ls -la "$REPO_DIR/cloud/wyniki_kolejka" || true
}

clean_runtime() {
  echo ">>> Czyszczenie wyników runtime"
  rm -rf "$REPO_DIR/cloud/wyniki" \
         "$REPO_DIR/cloud/wyniki_kolejka" \
         "$REPO_DIR/cloud/wyniki_z_azure" 2>/dev/null || true
  echo ">>> OK"
}

case "$MODE" in
  prosta)
    run_prosta
    ;;
  kolejka)
    run_kolejka
    ;;
  build)
    build_image
    ;;
  clean)
    clean_runtime
    ;;
  *)
    echo "Nieznany tryb: $MODE"
    echo "Użycie: bash docker/uruchom.sh [prosta|kolejka|build|clean]"
    exit 1
    ;;
esac