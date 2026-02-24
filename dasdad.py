import sqlite3

DB_NAME = "clinic.db"

def show_all_accounts():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("\n" + "="*120)
    # Added "PASSWORD TO TYPE" column which pulls the student_number
    print(f"{'ID':<4} | {'USERNAME (Full Name)':<25} | {'PASSWORD TO TYPE':<18} | {'ROLE':<8} | {'HASHED PASSWORD IN DB'}")
    print("-" * 120)

    # JOIN students table so we can see the plain student_number (which is the password)
    query = """
        SELECT u.id, u.username, u.role, u.password as hashed_pass, s.student_number
        FROM users u
        LEFT JOIN students s ON u.linked_student_id = s.id
    """
    
    try:
        cursor.execute(query)
        rows = cursor.fetchall()

        if not rows:
            print("The users table is currently empty.")
        else:
            for row in rows:
                # If it's a nurse, student_number will be NULL, so we handle that
                plain_pass = row['student_number'] if row['student_number'] else "Check Nurse Table"
                
                # We show the first 30 characters of the hash to keep the table readable
                print(f"{row['id']:<4} | {row['username']:<25} | {plain_pass:<18} | {row['role']:<8} | {row['hashed_pass'][:40]}...")
            
        print("="*120)
        print("\nDEBUG INFO:")
        print("1. If 'USERNAME' has weird spaces, login will fail.")
        print("2. If 'PASSWORD TO TYPE' has a '.0' at the end, the student must type the '.0'.")
        print("3. The 'HASHED PASSWORD' is what check_password_hash() looks at.")

    except sqlite3.Error as e:
        print(f"Database Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    show_all_accounts()