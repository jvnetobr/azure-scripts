import json
import requests
from msal import ConfidentialClientApplication

# Informações do Tenant e Service Principal
tenant_id = input("Digite o Tenant ID: ")
client_id = input("Digite o Client ID: ")
client_secret = input("Digite o Client Secret: ")
subscription_id = input("Digite o Subscription ID: ")

# URLs da API
GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0"
AZURE_MANAGEMENT_API_ENDPOINT = "https://management.azure.com"
AZURE_SCOPE = "https://management.azure.com/.default"
GRAPH_SCOPE = "https://graph.microsoft.com/.default"

# Autenticação usando MSAL
app = ConfidentialClientApplication(
    client_id,
    authority=f"https://login.microsoftonline.com/{tenant_id}",
    client_credential=client_secret,
)

# Solicitar token de acesso para a Microsoft Graph API
graph_token_response = app.acquire_token_for_client(scopes=[GRAPH_SCOPE])

if "access_token" not in graph_token_response:
    print("Falha ao obter token de acesso para Microsoft Graph!")
    print(graph_token_response.get("error_description"))
    exit(1)

graph_access_token = graph_token_response["access_token"]

# Solicitar token de acesso para a API de Gerenciamento da Azure
azure_token_response = app.acquire_token_for_client(scopes=[AZURE_SCOPE])

if "access_token" not in azure_token_response:
    print("Falha ao obter token de acesso para Azure Management API!")
    print(azure_token_response.get("error_description"))
    exit(1)

azure_access_token = azure_token_response["access_token"]

# Função para chamar a API Microsoft Graph
def call_graph_api(endpoint):
    headers = {"Authorization": f"Bearer {graph_access_token}"}
    response = requests.get(f"{GRAPH_API_ENDPOINT}{endpoint}", headers=headers)
    return response.json()

# Função para chamar a API de Gerenciamento de Recursos do Azure
def call_azure_management_api(endpoint):
    headers = {"Authorization": f"Bearer {azure_access_token}"}
    response = requests.get(f"{AZURE_MANAGEMENT_API_ENDPOINT}{endpoint}", headers=headers)
    return response.json()

# 1. Listar todos os usuários no Azure AD
print("Recuperando usuários...")
users_data = call_graph_api("/users")
users = users_data.get("value", [])

# 2. Listar todos os grupos no Azure AD
print("Recuperando grupos...")
groups_data = call_graph_api("/groups")
groups = groups_data.get("value", [])

# 3. Listar as permissões de RBAC para a subscription
print("Recuperando permissões de RBAC...")
role_assignments_data = call_azure_management_api(f"/subscriptions/{subscription_id}/providers/Microsoft.Authorization/roleAssignments?api-version=2020-08-01")
role_assignments = role_assignments_data.get("value", [])

# 4. Exibir as permissões para cada usuário e grupo
output_data = []

for role_assignment in role_assignments:
    principal_id = role_assignment["properties"]["principalId"]
    role_definition_id = role_assignment["properties"]["roleDefinitionId"]
    scope = role_assignment["properties"]["scope"]

    # Buscar o nome do usuário ou grupo
    principal_name = None
    for user in users:
        if user["id"] == principal_id:
            principal_name = user["displayName"]
            break

    if not principal_name:
        for group in groups:
            if group["id"] == principal_id:
                principal_name = group["displayName"]
                break

    if not principal_name:
        principal_name = "Desconhecido"

    # Exibir permissões para o usuário ou grupo
    output_data.append({
        "Principal": principal_name,
        "Principal ID": principal_id,
        "Role Definition ID": role_definition_id,
        "Scope": scope
    })

# Escrever a saída em um arquivo JSON
output_file = "permissoes_usuarios_grupos.json"
with open(output_file, 'w') as f:
    json.dump(output_data, f, indent=4)

print(f"Permissões salvas no arquivo {output_file}.")