# 🏥 Student Health Monitoring System

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.0+-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3.0+-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

An intelligent, web-based clinic management solution designed to digitize student health records, integrate RFID identification, and automate parent communication.

---

## 📌 Project Overview
The **Student Health Monitoring System** is a Flask-powered application designed to streamline school clinic workflows. By replacing manual paperwork with digital records and RFID-based student tracking, the system ensures high data accuracy and real-time health analytics.

### 🎯 Key Objectives
* **Digitization:** Eliminate physical logbooks with a secure SQLite backend.
* **Efficiency:** Use **RFID Integration** for near-instant student identification.
* **Transparency:** Automated email notifications via **EmailJS** to keep parents informed.
* **Analytics:** Real-time dashboards to track health trends and common symptoms.

---

## 🔐 User Roles & Permissions

| Feature | 👩‍⚕️ Nurse (Admin) | 👨‍🎓 Student |
| :--- | :---: | :---: |
| View Personal Health Profile | ✅ | ✅ |
| View Visit History | ✅ (All) | ✅ (Personal) |
| CRUD Student Records | ✅ | ❌ |
| Record Clinic Visits | ✅ | ❌ |
| View Analytics & Trends | ✅ | ❌ |
| System Configuration | ✅ | ❌ |

---

## 🛠️ Core Functionalities

### 1. Smart Authentication
* Role-based access control (RBAC).
* Password hashing for enhanced security.
* Persistent session management.

### 2. Nurse Dashboard & Analytics
* **Live Metrics:** Total visits, daily counts, and visits per grade level.
* **Trend Tracking:** Visualization of the most common symptoms and medical conditions (allergies, etc.).
* **Recent Activity:** Quick view of the last 10 clinic entries.

### 3. RFID & Student Management
* **RFID Integration:** Instant data retrieval via UID scanning.
* **Batch Import:** Support for JSON-based student data uploads.
* **Automated Account Creation:** New students automatically receive login credentials upon registration.

### 4. Clinic Visit Recording & Automation
* Detailed logging of Vitals (Temperature), Chief Complaints, Diagnosis, and Prescriptions.
* **Automated Email Alerts:** Sends a comprehensive health report to parents immediately after a visit is encoded.

---

## 📂 Project Structure
```text
├── app.py              # Main Flask application logic
├── database.db         # SQLite Database file
├── schema.sql          # Database table definitions
├── static/             # CSS, JS, and Images
│   ├── css/
│   └── js/             # Includes RFID and EmailJS logic
├── templates/          # HTML Templates (Jinja2)
│   ├── auth/           # Login/Logout
│   ├── nurse/          # Dashboard, CRUD, Reports
│   └── student/        # Personal Profile, History
└── requirements.txt    # Python dependencies
