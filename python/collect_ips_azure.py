import subprocess
import json
import pandas as pd

def listar_grupos_azure():
    print("🔎 Listando grupos de recursos...")
    resultado = subprocess.run(["az", "group", "list", "--output", "json"], capture_output=True, text=True)
    return json.loads(resultado.stdout)

def listar_ips_azure(grupo):
    comando = [
        "az", "network", "public-ip", "list",
        "--resource-group", grupo,
        "--output", "json"
    ]
    resultado = subprocess.run(comando, capture_output=True, text=True)
    try:
        return json.loads(resultado.stdout)
    except json.JSONDecodeError:
        print(f"⚠️ Erro ao coletar IPs do grupo: {grupo}")
        return []

def listar_webapps(grupo):
    comando = [
        "az", "webapp", "list",
        "--resource-group", grupo,
        "--output", "json"
    ]
    resultado = subprocess.run(comando, capture_output=True, text=True)
    try:
        return json.loads(resultado.stdout)
    except json.JSONDecodeError:
        print(f"⚠️ Erro ao coletar Web Apps do grupo: {grupo}")
        return []

def listar_static_webapps():
    comando = [
        "az", "staticwebapp", "list",
        "--output", "json"
    ]
    resultado = subprocess.run(comando, capture_output=True, text=True)
    try:
        return json.loads(resultado.stdout)
    except json.JSONDecodeError:
        print("⚠️ Erro ao coletar Static Web Apps.")
        return []

def listar_postgresql_servers(grupo):
    comando = [
        "az", "postgres", "flexible-server", "list",
        "--resource-group", grupo,
        "--output", "json"
    ]
    resultado = subprocess.run(comando, capture_output=True, text=True)
    try:
        return json.loads(resultado.stdout)
    except json.JSONDecodeError:
        print(f"⚠️ Erro ao coletar PostgreSQL Servers do grupo: {grupo}")
        return []

def coletar_ips_azure():
    dados = []
    grupos = listar_grupos_azure()
    for grupo in grupos:
        nome_grupo = grupo["name"]
        print(f"🔄 Coletando IPs do grupo: {nome_grupo}")
        
        # Coletar Public IPs
        ips = listar_ips_azure(nome_grupo)
        for ip in ips:
            ip_address = ip.get("ipAddress")
            nome_ip = ip.get("name")
            fqdn = ip.get("dnsSettings", {}).get("fqdn", "")
            if ip_address or fqdn:
                dados.append({
                    "cloud": "Azure",
                    "projeto_ou_grupo": nome_grupo,
                    "nome_recurso": nome_ip,
                    "ip": ip_address if ip_address else "",
                    "dominio_customizado": fqdn if fqdn else ""
                })
        
        # Coletar App Services
        webapps = listar_webapps(nome_grupo)
        for app in webapps:
            nome_app = app.get("name")
            hostnames = app.get("defaultHostName", "")
            if hostnames:
                dados.append({
                    "cloud": "Azure",
                    "projeto_ou_grupo": nome_grupo,
                    "nome_recurso": nome_app,
                    "ip": "",
                    "dominio_customizado": hostnames
                })
        
        # Coletar PostgreSQL Gerenciado
        postgres_servers = listar_postgresql_servers(nome_grupo)
        for server in postgres_servers:
            nome_server = server.get("name")
            fqdn = server.get("fullyQualifiedDomainName", "")
            if fqdn:
                dados.append({
                    "cloud": "Azure",
                    "projeto_ou_grupo": nome_grupo,
                    "nome_recurso": nome_server,
                    "ip": "",
                    "dominio_customizado": fqdn
                })
    
    # Coletar Static Web Apps
    static_webapps = listar_static_webapps()
    for static_app in static_webapps:
        nome_static_app = static_app.get("name")
        fqdn = static_app.get("defaultHostname", "")
        if fqdn:
            dados.append({
                "cloud": "Azure",
                "projeto_ou_grupo": "Static Web Apps",
                "nome_recurso": nome_static_app,
                "ip": "",
                "dominio_customizado": fqdn
            })
    
    return dados

def main():
    dados = coletar_ips_azure()
    df = pd.DataFrame(dados)
    df.to_csv("ips_azure_completo.csv", index=False)
    print("✅ Arquivo 'ips_azure_completo.csv' gerado com sucesso.")

if __name__ == "__main__":
    main()