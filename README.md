🏥 Student Health Monitoring System
📌 Project Description
The Student Health Monitoring System is a web-based application developed using Python (Flask) and SQLite designed to manage and monitor student health records within a school clinic environment.
The system enables school nurses to efficiently record, track, and analyze student clinic visits while allowing students to securely view their personal health records. It integrates RFID-based student identification for faster data retrieval and supports automated email notifications to parents after clinic visits.
This system aims to improve clinic workflow efficiency, ensure accurate medical record keeping, and enhance communication between the school clinic and parents.
🎯 System Objectives
Digitize student health records
Reduce manual paperwork in school clinics
Enable fast student identification using RFID
Provide real-time clinic visit tracking
Send automated health reports to parents
Generate health statistics for monitoring trends
🔐 User Roles
The system has two primary user roles:
👩‍⚕️ Nurse
Full access to student records
Can record clinic visits
Can view analytics and reports
Can manage student accounts
👨‍🎓 Student
Can view personal profile
Can see recent clinic visit history
🛠️ Core Functionalities
1️⃣ Authentication System
Secure login with username and password
Role-based access control (Nurse / Student)
Session management
Password hashing for security
2️⃣ Nurse Dashboard Features
📊 Health Statistics & Analytics
Total number of students
Total clinic visits
Visits for the current day
Visits per grade level
Most common symptoms
Students with allergies or medical conditions
Recent visit trends (last 10 entries)
This helps nurses monitor overall student health patterns.
3️⃣ Student Management (CRUD Operations)
Nurses can:
➕ Add new students
✏️ Edit student information
❌ Delete student records
📥 Import students via JSON upload
🔎 Search students by:
RFID UID
Student Number
When a new student is added:
A user account is automatically created
Password is securely hashed before storage
4️⃣ RFID Integration
Students can be identified using RFID card scanning
Each RFID UID is stored as a unique identifier
Enables fast student data retrieval during clinic visits
5️⃣ Clinic Visit Recording
Nurses can record:
Temperature
Chief complaint
Diagnosis
Prescribed medicine
Date and time of visit
Nurse who encoded the record
All visits are stored in the database and linked to the student.
6️⃣ Visit History Management
Nurse View:
Access to full visit history of all students
Detailed view including parent contact information
Student View:
Can see their personal visit history
Displays recent visit records (last 10 entries)
7️⃣ Automated Email Notification
After recording a clinic visit, the system automatically sends a health report email to the student’s parent.
The email includes:
Student Name
Student Number
Date and Time of Visit
Temperature
Complaint
Diagnosis
Prescribed Medicine
Nurse Name
This improves parent communication and transparency.
8️⃣ Secure Logout
Users can log out safely
Session is cleared
Redirected back to login page
🗄️ Technologies Used
Python
Flask Framework
SQLite Database
HTML / CSS
JavaScript
EmailJS (for email notifications)
RFID Reader Integration
📈 System Benefits
Faster clinic processing time
Organized digital health records
Reduced data loss risk
Improved parent communication
Better health monitoring and reporting
Scalable for school-wide implementation