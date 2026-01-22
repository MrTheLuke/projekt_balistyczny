#!/bin/bash
set -e

RG="rg-balistyczny-student-norwayeast"
VM="vm-balistyczna"

echo ">>> STOP VM (deallocate)"
az vm deallocate --resource-group "$RG" --name "$VM"
