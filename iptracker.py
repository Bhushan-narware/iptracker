import requests
import os
import sys
import time
import json
import socket
import ipaddress
from colorama import init, Fore, Back, Style

# Initialize colorama for cross-platform colors
init(autoreset=True)

# --- API CONFIGURATION ---
VIEWDNS_API_KEY = os.getenv('VIEWDNS_API_KEY', '5e2b62da60904c6ac5cf0981319dbbf75107ea94')  # Fallback to your provided key

def logo():
    os.system('clear' if os.name == 'posix' else 'cls')
    print(Fore.YELLOW + Style.BRIGHT)
    print(Fore.RED + "      _" + Fore.YELLOW + " ____    _")
    print("     " + Fore.RED + "(_)" + Fore.YELLOW + "  _ \  | |_ _ __ __ _  ___ ___ _ __")
    print("     | | |_) | | __| '__/ _` |/ __/ _ \ '__|")
    print("     | |  __/  | |_| | | (_| | (_|  __/ |")
    print("     |_|_|      \__|_|  \__,_|\___\___|_|")
    print("\n   " + Fore.WHITE + "}" + Fore.RED + "----------------------------------------" + Fore.WHITE + "{")
    print("}" + Fore.RED + "-------------- " + Fore.GREEN + "Cyber-Guardian Tracer" + Fore.RED + " ----------" + Fore.WHITE + "{")
    print("   " + Fore.RED + "----------------------------------------" + Fore.WHITE + "{")
    print(Fore.RED + "\nDisclaimer: Use this tool responsibly for ethical purposes only.")
    print(Style.RESET_ALL)

def validate_and_resolve(target):
    """Validate IP or resolve domain to IP."""
    try:
        ipaddress.ip_address(target)
        return target
    except ValueError:
        try:
            return socket.gethostbyname(target)
        except socket.gaierror:
            
            return None

def fetch_ip_data(ip):
    """Fetch IP data with fallback to secondary API."""
    # Primary: ip-api.com
    primary_url = f"http://ip-api.com/json/{ip}"
    try:
        response = requests.get(primary_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get('status') == 'success':
            return data
    except requests.exceptions.RequestException:
        pass  # Fall back
    
    # Fallback: ipinfo.io (requires free token; replace with yours if needed)
    fallback_url = f"https://ipinfo.io/{ip}/json"
    try:
        response = requests.get(fallback_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if 'ip' in data:
            # Normalize to match primary format
            return {
                'query': data['ip'],
                'city': data.get('city', 'N/A'),
                'region': data.get('region', 'N/A'),
                'country': data.get('country', 'N/A'),
                'zip': data.get('postal', 'N/A'),
                'lat': data.get('loc', '').split(',')[0] if data.get('loc') else 'N/A',
                'lon': data.get('loc', '').split(',')[1] if data.get('loc') else 'N/A',
                'timezone': data.get('timezone', 'N/A'),
                'isp': data.get('org', 'N/A'),  # Org as ISP
                'status': 'success'
            }
    except requests.exceptions.RequestException:
        pass
    
    return None

def fetch_viewdns_domains(ip):
    """Fetch associated domains from ViewDNS."""
    if not VIEWDNS_API_KEY:
        return []
    url = f"https://api.viewdns.info/reverseip/?host={ip}&apikey={VIEWDNS_API_KEY}&output=json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get('response', {}).get('domains'):
            return [d['name'] for d in data['response']['domains'][:5]]
        elif data.get('error'):
            print(Fore.RED + f"[-] ViewDNS Error: {data['error']}")
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"[-] ViewDNS Connection Error: {e}")
    return []

def get_ip_info(target=""):
    """Enhanced IP tracking with expanded data."""
    resolved_ip = validate_and_resolve(target)
    if not resolved_ip:
        print(Fore.RED + "[-] Invalid IP or domain.")
        return
    
    print(Fore.BLUE + "[*] Fetching IP data...")
    time.sleep(1)  # Rate limit
    
    ip_data = fetch_ip_data(resolved_ip)
    if not ip_data:
        print(Fore.RED + f"[-] Failed to fetch data for {resolved_ip}.")
        return
    
    # Display expanded info
    print(Fore.GREEN + f"\n[+] IP Address : {Fore.WHITE}{resolved_ip}")
    print(Fore.GREEN + f"[+] Location   : {Fore.WHITE}{ip_data.get('city', 'N/A')}, {ip_data.get('region', 'N/A')}, {ip_data.get('country', 'N/A')}")
    print(Fore.GREEN + f"[+] Zip Code   : {Fore.WHITE}{ip_data.get('zip', 'N/A')}")
    print(Fore.GREEN + f"[+] Coordinates: {Fore.WHITE}{ip_data.get('lat', 'N/A')}, {ip_data.get('lon', 'N/A')}")
    print(Fore.GREEN + f"[+] Timezone   : {Fore.WHITE}{ip_data.get('timezone', 'N/A')}")
    print(Fore.GREEN + f"[+] ISP/Org    : {Fore.WHITE}{ip_data.get('isp', 'N/A')}")
    
    # ViewDNS domains
    domains = fetch_viewdns_domains(resolved_ip)
    if domains:
        print(Fore.GREEN + f"[+] Domains    : {Fore.WHITE}{', '.join(domains)}")
    else:
        print(Fore.YELLOW + "[+] Domains    : None found")
    
    # Export option
    export = input(Fore.YELLOW + "\nExport to JSON? (y/n): ").strip().lower()
    if export == 'y':
        result = {'ip': resolved_ip, 'data': ip_data, 'domains': domains}
        with open('ip_track.json', 'w') as f:
            json.dump(result, f, indent=4)
        print(Fore.BLUE + "[*] Exported to ip_track.json")
    
    input(Fore.YELLOW + "\nPress Enter to return...")

def menu():
    while True:
        logo()
        print(Fore.GREEN + "   [ 1 ] Track Target IP/Domain")
        print(Fore.GREEN + "   [ 2 ] Track Your IP")
        print(Fore.GREEN + "   [ x ] Exit\n")
        
        choice = input(Fore.WHITE + '  Cyber-Guardian >> ').strip().lower()
        
        if choice in ['x', 'exit']:
            print(Fore.GREEN + "Exiting...")
            sys.exit()
        elif choice == '1':
            target = input(Fore.GREEN + "\nEnter Target IP/Domain: ").strip()
            get_ip_info(target)
        elif choice == '2':
            get_ip_info()
        else:
            print(Fore.RED + "Invalid choice.")

if __name__ == "__main__":
    menu()