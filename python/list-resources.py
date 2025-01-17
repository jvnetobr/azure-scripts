from azure.identity import ClientSecretCredential
from azure.mgmt.resource import ResourceManagementClient
from tabulate import tabulate

# Credenciais do Service Principal
tenant_id = input("Digite o Tenant ID: ")
client_id = input("Digite o Client ID: ")
client_secret = input("Digite o Client Secret: ")
subscription_id = input("Digite o Subscription ID: ")

# Autenticação com o Service Principal
credentials = ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)

# Criação do cliente de gerenciamento de recursos
resource_client = ResourceManagementClient(credentials, subscription_id)

# Nome do arquivo de saída
output_file = input("Digite o nome do arquivo de saída: ")

# Lista de recursos para a tabela
resource_table = []

# Loop para pegar as informações dos recursos
for resource in resource_client.resources.list():
    # Extraindo o resource_group do ID do recurso
    resource_id_parts = resource.id.split('/')
    resource_group = resource_id_parts[4]  # O resource_group é a 5ª parte do ID

    # Adicionando informações do recurso à tabela
    resource_table.append([resource.name, resource.type, resource.location, resource_group])

# Criando cabeçalhos da tabela
headers = ["Nome do Recurso", "Tipo", "Localização", "Grupo de Recursos"]

# Formatando a tabela
table = tabulate(resource_table, headers, tablefmt="grid")

# Salvando a tabela em um arquivo de saída
with open(output_file, 'w') as f:
    f.write(table)

print(f"Tabela de recursos salva em: {output_file}")