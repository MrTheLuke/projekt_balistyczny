#!/bin/bash
set -e

RG="rg-balistyczny-student-norwayeast"
VM="vm-balistyczna"
USERVM="azureuser"
SSH_KEY="$HOME/.ssh/azure_vm_key"

MAX_PARALLEL=${MAX_PARALLEL:-2}
STOP_AFTER=${STOP_AFTER:-1}   # 1 = zatrzymaj VM po obliczeniach

echo ">>> START VM"
az vm start --resource-group "$RG" --name "$VM"

echo ">>> Pobieram IP"
IP=$(az vm show -d -g "$RG" -n "$VM" --query publicIps -o tsv)
echo ">>> IP VM: $IP"

echo ">>> Czekam na SSH..."
until ssh -i "$SSH_KEY" -o ConnectTimeout=5 -o StrictHostKeyChecking=no "$USERVM@$IP" "echo SSH_OK" >/dev/null 2>&1
do
  sleep 5
done
echo ">>> SSH gotowe"

echo ">>> Aktualizacja repo na VM"
ssh -i "$SSH_KEY" "$USERVM@$IP" "cd ~/projekt_balistyczny && git pull"

echo ">>> Uruchamiam kolejkę (MAX_PARALLEL=$MAX_PARALLEL)"
MAX_PARALLEL="$MAX_PARALLEL" python3 kolejka/uruchom_kolejke_vm.py

if [ "$STOP_AFTER" = "1" ]; then
  echo ">>> STOP VM"
  az vm deallocate --resource-group "$RG" --name "$VM"
else
  echo ">>> VM pozostaje uruchomiona"
fi

echo "=== GOTOWE ==="
