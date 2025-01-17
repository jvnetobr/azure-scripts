#!/bin/bash

# Solicitar o nome do grupo de recursos
read -p "Digite o nome do grupo de recursos: " RESOURCE_GROUP

# Obter a lista de contas de armazenamento no grupo de recursos
echo "Recuperando contas de armazenamento no grupo de recursos '$RESOURCE_GROUP'..."
STORAGE_ACCOUNTS=$(az storage account list --resource-group "$RESOURCE_GROUP" --query "[].name" -o tsv)

if [ -z "$STORAGE_ACCOUNTS" ]; then
    echo "Nenhuma conta de armazenamento encontrada no grupo de recursos '$RESOURCE_GROUP'."
    exit 1
fi

# Criar/limpar arquivo de saída
OUTPUT_FILE="filtered_containers"
> "$OUTPUT_FILE"

# Listar contêineres de blob para cada conta de armazenamento
echo -e "\nContêineres de Blob encontrados no grupo de recursos '$RESOURCE_GROUP':"
for ACCOUNT in $STORAGE_ACCOUNTS; do
    echo -e "\nConta de Armazenamento: $ACCOUNT"
    
    # Obter a chave de acesso da conta de armazenamento
    STORAGE_KEY=$(az storage account keys list --account-name "$ACCOUNT" --resource-group "$RESOURCE_GROUP" --query "[0].value" -o tsv)
    
    # Listar os contêineres de blob
    CONTAINERS=$(az storage container list --account-name "$ACCOUNT" --account-key "$STORAGE_KEY" --query "[].name" -o tsv)
    
    if [ -z "$CONTAINERS" ]; then
        echo "  Nenhum contêiner de Blob encontrado."
    else
        echo "  Contêineres encontrados:"
        echo "$CONTAINERS" | awk '{print "  - " $0}'
        
        # Adicionar os contêineres ao arquivo de saída
        echo "$CONTAINERS" >> "$OUTPUT_FILE"
    fi
done

echo -e "\nArquivo gerado: $OUTPUT_FILE"