import requests
import json
import os

# Config
CLOUDFLARE_API_TOKEN = os.getenv('CLOUDFLARE_API_TOKEN')
ZONE_ID = os.getenv('ZONE_ID')
IP_CACHE_FILE = 'last_ip.txt'

def get_public_ip():
    """Fetch the current public IP address"""
    response = requests.get('https://api.ipify.org?format=json')
    response.raise_for_status()
    return response.json()['ip']

def get_dns_records():
    """Fetch all A records from Cloudflare for the given zone"""
    url = f'https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records?type=A'
    headers = {
        'Authorization': f'Bearer {CLOUDFLARE_API_TOKEN}',
        'Content-Type': 'application/json',
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['result']

def update_dns_record(record_id, domain_name, ip_address):
    """Update the DNS record with the new IP address"""
    url = f'https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records/{record_id}'
    headers = {
        'Authorization': f'Bearer {CLOUDFLARE_API_TOKEN}',
        'Content-Type': 'application/json',
    }
    data = {
        'type': 'A',
        'name': domain_name,
        'content': ip_address
    }
    response = requests.put(url, headers=headers, data=json.dumps(data))
    response.raise_for_status()
    return response.json()

def check_and_update_ip():
    try:
        new_ip = get_public_ip()
        # Read the last known IP from the cache file
        if os.path.exists(IP_CACHE_FILE):
            with open(IP_CACHE_FILE, 'r') as file:
                current_ip = file.read().strip()
        else:
            current_ip = None

        if new_ip != current_ip:
            print(f'IP change detected: {new_ip}')
            all_updates_successful = True
            records = get_dns_records()
            for record in records:
                if record['content'] == current_ip:
                    update_response = update_dns_record(record['id'], record['name'], new_ip)
                    if update_response['success']:
                        print(f'Updated Cloudflare record for {record["name"]} to {new_ip}')
                    else:
                        all_updates_successful = False
                        print(f'Failed to update Cloudflare for {record["name"]}:', update_response['errors'])
            
            if all_updates_successful:
                # Save the new IP to the cache file
                with open(IP_CACHE_FILE, 'w') as file:
                    file.write(new_ip)
        else:
            print('No IP change detected')
    except requests.RequestException as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    check_and_update_ip()
