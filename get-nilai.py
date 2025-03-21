import requests
import json
import sys
import time
from datetime import datetime
import os
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

# Base URLs and endpoints
LOGIN_URL = "https://auth-api.pijarsekolah.id/student/login"
SCORE_URL = "https://api.pijarsekolah.id/exam/v2/score?page=1&size=50&mapel=&jenis_ujian=non-akm&sort_by=terbaru&tahun=2025"

# Files for logging
log_dir = "logs"
pdf_dir = "reports"
log_file = os.path.join(log_dir, "scores.log")

# Ensure directories exist
for directory in [log_dir, pdf_dir]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# Function to attempt login with NISN
def try_login(nisn):
    print(f"{Colors.CYAN}>> Attempting login for NISN: {nisn}{Colors.RESET}")
    
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
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36"
    }
    
    try:
        response = requests.post(LOGIN_URL, json=login_data, headers=headers)
        
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
            return None
    except Exception as e:
        print(f"{Colors.RED}>> Error during login request: {str(e)}{Colors.RESET}")
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
        response = requests.get(SCORE_URL, headers=headers)
        
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
            return None
    except Exception as e:
        print(f"{Colors.RED}>> Error during score request: {str(e)}{Colors.RESET}")
        return None

# Function to generate PDF report
def generate_pdf_report(score_data, nisn):
    print(f"{Colors.CYAN}>> Generating PDF report...{Colors.RESET}")
    
    # Extract student name and class information from the first score entry
    if len(score_data['data']) > 0:
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

# Main function
def main():
    print(f"{Colors.MAGENTA}{'='*60}{Colors.RESET}")
    print(f"{Colors.MAGENTA}          NISN SCORE EXTRACTOR & PDF GENERATOR          {Colors.RESET}")
    print(f"{Colors.MAGENTA}{'='*60}{Colors.RESET}")
    
    # Get NISN from user
    while True:
        nisn = input(f"{Colors.BLUE}>> Enter student NISN: {Colors.RESET}")
        if nisn.strip() and nisn.isdigit():
            break
        print(f"{Colors.RED}>> Invalid NISN. Please enter a valid numeric NISN.{Colors.RESET}")
    
    # Try login
    token = try_login(nisn)
    
    if token:
        # Get scores
        score_data = get_user_scores(token)
        
        if score_data and score_data.get('data'):
            # Generate PDF report
            pdf_file = generate_pdf_report(score_data, nisn)
            
            # Log success
            with open(log_file, 'a') as f:
                f.write(f"[{datetime.now()}] Successfully extracted scores for NISN {nisn} - PDF: {pdf_file}\n")
            
            print(f"{Colors.GREEN}>> Success! Score data has been extracted and saved to: {pdf_file}{Colors.RESET}")
            print(f"{Colors.BLUE}>> Found {len(score_data['data'])} exam scores.{Colors.RESET}")
        else:
            print(f"{Colors.RED}>> No score data found for NISN: {nisn}{Colors.RESET}")
    else:
        print(f"{Colors.RED}>> Could not login with NISN: {nisn}. Please check and try again.{Colors.RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"{Colors.YELLOW}>> Script interrupted by user. Exiting...{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.RED}>> An unexpected error occurred: {str(e)}{Colors.RESET}")
        sys.exit(1)
