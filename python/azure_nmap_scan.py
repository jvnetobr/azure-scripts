import subprocess
import json
import os

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

def list_vms_in_resource_group(resource_group):
    print(f"\nFetching VMs for Resource Group: {resource_group}...")
    command = [
        "az", "vm", "list", 
        "--resource-group", resource_group, 
        "--show-details", 
        "--query", "[].{Name:name,PublicIP:publicIps}", 
        "--output", "json"
    ]
    output = run_command(command)
    if output:
        return json.loads(output)
    return []

def run_nmap_on_ip(ip, output_file):
    try:
        print(f"\nRunning nmap on IP: {ip}...")
        command = ["sudo", "nmap", "-sS", "-Pn", ip]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        
        with open(output_file, "a") as file:
            file.write(f"Scan results for IP: {ip}\n")
            file.write(result.stdout + "\n")
        
        print(f"Scan results saved to {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error running nmap on IP {ip}: {e}")

def main():
    output_dir = "azure_nmap_scans"
    os.makedirs(output_dir, exist_ok=True)
    
    resource_groups = list_resource_groups()
    if not resource_groups:
        print("No Resource Groups found.")
        return
    
    for rg in resource_groups:
        print(f"\nProcessing Resource Group: {rg}")
        vms = list_vms_in_resource_group(rg)
        if not vms:
            print(f"No VMs found in Resource Group: {rg}")
            continue
        
        output_file = os.path.join(output_dir, f"{rg}_nmap_results.txt")
        for vm in vms:
            vm_name = vm.get("Name")
            public_ip = vm.get("PublicIP")
            if public_ip:
                print(f"VM: {vm_name}, Public IP: {public_ip}")
                run_nmap_on_ip(public_ip, output_file)
            else:
                print(f"VM: {vm_name} does not have a public IP.")
    
    print("\nAll scans completed. Results are saved in the 'azure_nmap_scans' directory.")

if __name__ == "__main__":
    main()