import sqlite3
import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

DB_NAME = "clinic.db"

def seed_data():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 1. Sample Data Pools
    sections = ['STEM-A', 'STEM-B', 'ICT-A', 'ABM-A', 'HUMSS-B', 'GAS-A']
    complaints = ['Fever', 'Headache', 'Stomach ache', 'Dizziness', 'Cough and Cold', 'Sprain', 'Nausea']
    diagnoses = ['Flu symptoms', 'Migraine', 'Dysmenorrhea', 'High blood pressure', 'Common cold', 'Minor injury', 'Food poisoning']
    medicines = ['Paracetamol', 'Ibuprofen', 'Antacid', 'Cetirizine', 'Biogesic', 'None']

    print("Generating 30 students...")
    student_ids = []
    
    # 2. Create 30 Students
    for i in range(1, 31):
        full_name = f"Student Name {i}"
        std_num = f"2026-{1000 + i}"
        rfid = f"UID{random.randint(100000, 999999)}"
        
        try:
            cursor.execute("""
                INSERT INTO students (rfid_uid, student_number, full_name, grade, section, parent_name, parent_email)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (rfid, std_num, full_name, random.choice(['11', '12','7','8','9','10']), random.choice(sections), 
                  f"Parent of {full_name}", "parent@example.com"))
            
            s_id = cursor.lastrowid
            student_ids.append(s_id)
            
            # Create User Account for the student
            cursor.execute("INSERT OR IGNORE INTO users (username, password, role, linked_student_id) VALUES (?, ?, ?, ?)",
                           (full_name, generate_password_hash(std_num), 'student', s_id))
        except sqlite3.IntegrityError:
            continue # Skip if already exists

    print("Generating 200 visit records...")
    # 3. Create 200 Random Visits
    for _ in range(200):
        s_id = random.choice(student_ids)
        temp = round(random.uniform(36.2, 39.5), 1)
        comp = random.choice(complaints)
        diag = random.choice(diagnoses)
        med = random.choice(medicines)
        
        # Random date within the last 30 days
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        visit_date = (datetime.now() - timedelta(days=days_ago, hours=hours_ago)).strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO clinic_visits (student_id, nurse_id, temperature, complaint, diagnosis, medicine, time_in)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (s_id, 2, temp, comp, diag, med, visit_date)) # nurse_id 2 is Bonnie Bennett

    conn.commit()
    conn.close()
    print(f"Successfully added 200 visits to {DB_NAME}!")

if __name__ == "__main__":
    seed_data()