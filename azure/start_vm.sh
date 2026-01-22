#!/bin/bash
set -e

RG="rg-balistyczny-student-norwayeast"
VM="vm-balistyczna"

echo ">>> START VM"
az vm start --resource-group "$RG" --name "$VM"

echo ">>> Pobieram IP"
IP=$(az vm show -d -g "$RG" -n "$VM" --query publicIps -o tsv)
echo ">>> VM IP: $IP"

echo "$IP" > azure/vm_ip.txt
