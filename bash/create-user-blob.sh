#!/bin/bash

# Solicitar informações do usuário
read -p "Digite o nome do grupo de recursos: " RESOURCE_GROUP
read -p "Digite o nome da conta de armazenamento: " STORAGE_ACCOUNT
read -p "Digite o nome do usuário SFTP: " USERNAME
read -p "Digite o caminho para o arquivo contendo a lista de contêineres: " CONTAINERS_FILE

# Verificar se o arquivo existe
if [ ! -f "$CONTAINERS_FILE" ]; then
    echo "Arquivo $CONTAINERS_FILE não encontrado. Por favor, forneça um arquivo válido."
    exit 1
fi

# Ler a lista de contêineres do arquivo e construir a lista de permissões
PERMISSION_SCOPE=""
while IFS= read -r container; do
    PERMISSION_SCOPE+="--permission-scope permissions=rcwdl service=blob resource-name=$container "
done < "$CONTAINERS_FILE"

# Criar ou atualizar o usuário local SFTP com todas as permissões em uma única execução
echo "Criando ou atualizando o usuário local SFTP: $USERNAME..."
az storage account local-user create \
    --resource-group "$RESOURCE_GROUP" \
    --account-name "$STORAGE_ACCOUNT" \
    --user-name "$USERNAME" \
    --has-ssh-password true \
    $PERMISSION_SCOPE \
    --output json || { echo "Erro ao criar o usuário SFTP. Verifique os parâmetros."; exit 1; }

# Recuperar e exibir os dados do usuário criado
USER_DETAILS=$(az storage account local-user show \
    --resource-group "$RESOURCE_GROUP" \
    --account-name "$STORAGE_ACCOUNT" \
    --user-name "$USERNAME" \
    --output json)

# Exibir os detalhes do usuário
echo -e "\nUsuário local criado com sucesso!"
echo "Nome do Usuário: $USERNAME"
echo "Detalhes do Usuário:"
echo "$USER_DETAILS" | jq