#!/bin/bash

# URL que você está procurando
URL_PROCURADA="https://wonderful-sky-0d846c110-preview.centralus.4.azurestaticapps.net"

# Faça login na Azure CLI, se necessário
#az login

# Obtenha a lista de todos os Static Web Apps
STATIC_WEB_APPS=$(az staticwebapp list --query "[].{Name:name,ResourceGroup:resourceGroup}" -o tsv)

# Percorra cada Static Web App
while IFS=$'\t' read -r NAME RESOURCE_GROUP; do
    echo "Verificando Static Web App: $NAME em Resource Group: $RESOURCE_GROUP"
    
    # Obtenha a lista de domínios personalizados para o Static Web App
    HOSTNAMES=$(az staticwebapp hostname list --name "$NAME" --resource-group "$RESOURCE_GROUP" --query "[].hostname" -o tsv)
    
    # Verifique se a URL procurada está na lista de domínios
    if echo "$HOSTNAMES" | grep -q "$URL_PROCURADA"; then
        echo "URL $URL_PROCURADA encontrada no Static Web App: $NAME"
    fi
done <<< "$STATIC_WEB_APPS"