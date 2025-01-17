import subprocess
import json

def run_command(command):
    try:
        print(f"Running command: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        return None

def list_resource_groups():
    print("\nFetching Resource Groups...")
    command = ["az", "group", "list", "--query", "[].name", "--output", "json"]
    output = run_command(command)
    if output:
        return json.loads(output)
    return []

def list_network_security_groups(resource_group):
    print(f"\nFetching NSGs for Resource Group: {resource_group}...")
    command = [
        "az", "network", "nsg", "list", 
        "--resource-group", resource_group, 
        "--query", "[].name", 
        "--output", "json"
    ]
    output = run_command(command)
    if output:
        return json.loads(output)
    return []

def fetch_nsg_rules(resource_group, nsg_name, output_file):
    print(f"\nFetching rules for NSG: {nsg_name} in Resource Group: {resource_group}...")
    command = [
        "az", "network", "nsg", "rule", "list", 
        "--resource-group", resource_group, 
        "--nsg-name", nsg_name, 
        "--output", "table"
    ]
    output = run_command(command)
    if output:
        with open(output_file, "w") as file:
            file.write(output)
        print(f"Rules for NSG {nsg_name} saved to {output_file}")
    else:
        print(f"Failed to fetch rules for NSG {nsg_name} in Resource Group {resource_group}")

def main():
    resource_groups = list_resource_groups()
    if not resource_groups:
        print("No Resource Groups found.")
        return
    
    for rg in resource_groups:
        nsgs = list_network_security_groups(rg)
        if not nsgs:
            print(f"No NSGs found in Resource Group: {rg}")
            continue

        for nsg in nsgs:
            output_file = f"{rg}_{nsg}_rules.txt"
            fetch_nsg_rules(rg, nsg, output_file)

if __name__ == "__main__":
    main()