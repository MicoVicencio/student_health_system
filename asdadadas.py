import sqlite3
import random
from datetime import datetime, timedelta
# Import remains in case you want to toggle it back later
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
    
    # New unique names for this batch
    student_names = [
        "Leo Sterling", "Ava Montgomery", "Silas Thorne", "Elara Vance", "Felix Wright",
        "Student Name 6", "Student Name 7", "Student Name 8", "Student Name 9", "Student Name 10",
        "Student Name 11", "Student Name 12", "Student Name 13", "Student Name 14", "Student Name 15",
        "Student Name 16", "Student Name 17", "Student Name 18", "Student Name 19", "Student Name 20",
        "Student Name 21", "Student Name 22", "Student Name 23", "Student Name 24", "Student Name 25",
        "Student Name 26", "Student Name 27", "Student Name 28", "Student Name 29", "Student Name 30"
    ]

    print("Generating 30 students... (Instant mode enabled)")
    student_ids = []
    
    # 2. Create 30 Students
    for i, full_name in enumerate(student_names, start=1):
        std_num = f"2026-{3000 + i}" 
        rfid = f"UID{random.randint(100000, 999999)}"
        
        try:
            cursor.execute("""
                INSERT INTO students (rfid_uid, student_number, full_name, grade, section, parent_name, parent_email)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (rfid, std_num, full_name, random.choice(['11', '12','7','8','9','10']), random.choice(sections), 
                  f"Parent of {full_name}", "parent@example.com"))
            
            s_id = cursor.lastrowid
            
            if not s_id:
                cursor.execute("SELECT id FROM students WHERE student_number = ?", (std_num,))
                result = cursor.fetchone()
                if result:
                    s_id = result[0]
                
            if s_id:
                student_ids.append(s_id)
                
                # TEMPORARY: Using plain text password to prevent KeyboardInterrupt/Freeze
                # Change this back to generate_password_hash(std_num) for production
                password_placeholder = f"hashed_{std_num}"
                
                cursor.execute("INSERT OR IGNORE INTO users (username, password, role, linked_student_id) VALUES (?, ?, ?, ?)",
                               (full_name, password_placeholder, 'student', s_id))

        except sqlite3.IntegrityError:
            continue

    print("Generating 200 visit records...")
    # 3. Create 200 Random Visits
    if student_ids:
        for _ in range(200):
            s_id = random.choice(student_ids)
            temp = round(random.uniform(36.2, 39.5), 1)
            comp = random.choice(complaints)
            diag = random.choice(diagnoses)
            med = random.choice(medicines)
            
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            visit_date = (datetime.now() - timedelta(days=days_ago, hours=hours_ago)).strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("""
                INSERT INTO clinic_visits (student_id, nurse_id, temperature, complaint, diagnosis, medicine, time_in)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (s_id, 2, temp, comp, diag, med, visit_date))

        conn.commit()
        print(f"Successfully populated {DB_NAME} with 30 students and 200 visits!")
    else:
        print("No students were processed. Check if student_number range 3000+ already exists.")
        
    conn.close()

if __name__ == "__main__":
    seed_data()