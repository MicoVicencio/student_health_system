import pandas as pd
import random
from faker import Faker

# Initialize Faker with Philippine locale
fake = Faker('en_PH')

def generate_excel_dummy_data(count=500):
    # Updated filename to reflect the count dynamically
    filename = f"dummy_students_{count}.xlsx"
    
    data = []
    sections = ['STEM-A', 'STEM-B', 'HUMSS-A', 'ABM-A', 'GAS-A', 'ICT-A', 'HE-A']
    medical_issues = ['Asthma', 'Diabetes', 'Hypertension', 'None', 'None', 'None']
    allergy_list = ['Peanuts', 'Dust', 'Shrimp', 'None', 'None', 'None']

    print(f"Generating {count} records... please wait.")

    for i in range(1, count + 1):
        # Unique identifiers
        rfid = f"RFID-{random.randint(10000000, 99999999)}"
        student_no = f"2026-{1000 + i}"
        
        # Realistic naming
        last_name = fake.last_name()
        student_name = f"{fake.first_name()} {last_name}"
        parent_name = f"{fake.first_name_male() if random.random() > 0.5 else fake.first_name_female()} {last_name}"
        
        # PH Mobile format
        contact_no = f"09{random.randint(10, 99)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"

        # Create row matching your SQL table schema
        row = {
            "rfid_uid": rfid,
            "student_number": student_no,
            "full_name": student_name,
            "address": fake.address().replace('\n', ', '),
            "age": random.randint(16, 19),
            "grade": random.choice(["11", "12"]),
            "section": random.choice(sections),
            "allergies": random.choice(allergy_list),
            "medical_condition": random.choice(medical_issues),
            "parent_name": parent_name,
            "parent_contact_number": contact_no,
            "parent_email": fake.email()
        }
        data.append(row)

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Save to Excel
    df.to_excel(filename, index=False, engine='openpyxl')
    print(f"Successfully generated '{filename}'")

if __name__ == "__main__":
    # CHANGE THIS NUMBER: This is what determines the final count.
    generate_excel_dummy_data(500)