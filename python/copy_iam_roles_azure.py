import subprocess
import json

def run_az_cli(cmd):
    """Executa comando no Azure CLI e retorna a saída JSON."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Erro ao executar: {' '.join(cmd)}")
        print(result.stderr)
        exit(1)
    return json.loads(result.stdout)

def get_user_object_id(user_email):
    """Obtém o objectId do usuário pelo e-mail."""
    cmd = ["az", "ad", "user", "show", "--id", user_email, "--query", "id", "-o", "tsv"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 or not result.stdout.strip():
        print(f"Usuário '{user_email}' não encontrado.")
        exit(1)
    return result.stdout.strip()

def list_role_assignments(user_id):
    """Lista todas as roles atribuídas diretamente ao usuário."""
    cmd = ["az", "role", "assignment", "list", "--assignee", user_id, "-o", "json"]
    return run_az_cli(cmd)

def assign_role(user_id, role_id, scope):
    """Atribui uma role ao usuário no escopo especificado."""
    cmd = [
        "az", "role", "assignment", "create",
        "--assignee", user_id,
        "--role", role_id,
        "--scope", scope
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"[OK] Role atribuída: {role_id} | Escopo: {scope}")
    else:
        if "RoleAssignmentExists" in result.stderr:
            print(f"[AVISO] Role já atribuída: {role_id} | Escopo: {scope}")
        else:
            print(f"[ERRO] Falha ao atribuir role: {role_id} | Escopo: {scope}")
            print(result.stderr)

def main():
    print("Script para copiar roles IAM de um usuário Azure para outro\n")

    user_origem = input("Digite o e-mail do usuário de ORIGEM: ").strip()
    user_destino = input("Digite o e-mail do usuário de DESTINO: ").strip()

    print("\nObtendo objectId dos usuários...")
    origem_id = get_user_object_id(user_origem)
    destino_id = get_user_object_id(user_destino)

    print(f"\nListando roles do usuário de origem ({user_origem})...")
    roles = list_role_assignments(origem_id)

    if not roles:
        print("Usuário de origem não possui roles atribuídas diretamente.")
        return

    print(f"\nTotal de roles encontradas: {len(roles)}")
    for role in roles:
        role_id = role.get("roleDefinitionId")
        scope = role.get("scope")
        print(f"Atribuindo role ao usuário de destino: {role_id} | Escopo: {scope}")
        assign_role(destino_id, role_id, scope)

    print("\nConcluído!")

if __name__ == "__main__":
    main()