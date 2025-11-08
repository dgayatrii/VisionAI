# #db_init.py
# import sqlite3
# import os

# DB_PATH = os.path.join(os.path.dirname(__file__), "records.db")

# def init_db():
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()

#     # Users: doctors / patients
#     c.execute("""
#     CREATE TABLE IF NOT EXISTS users (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         username TEXT UNIQUE NOT NULL,
#         password TEXT NOT NULL,
#         role TEXT NOT NULL
#     )
#     """)

#     # Patient prediction records
#     c.execute("""
#     CREATE TABLE IF NOT EXISTS patients (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         patient_name TEXT,
#         patient_id TEXT,
#         left_eye_path TEXT,
#         right_eye_path TEXT,
#         left_result TEXT,
#         right_result TEXT,
#         combined_result TEXT,
#         report_id TEXT,
#         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#     )
#     """)

#     conn.commit()
#     conn.close()
#     print("Initialized DB at:", DB_PATH)

# if __name__ == "__main__":
#     init_db()


# backend/db_init.py
# backend/db_init.py
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "records.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Create a comprehensive 'users' table for both doctors and patients
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        full_name TEXT,
        contact_number TEXT,
        address TEXT,
        age INTEGER,
        gender TEXT,
        hospital_name TEXT,
        medical_id TEXT
    )
    """)

    # Create a detailed 'patients' table linked to the doctor who created it
    c.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doctor_id INTEGER,
        name TEXT NOT NULL,
        patient_id TEXT UNIQUE,
        age INTEGER,
        gender TEXT,
        diabetes_duration TEXT,
        blood_sugar_level TEXT,
        blood_pressure TEXT,
        medications TEXT,
        other_conditions TEXT,
        doctor_notes TEXT,
        left_eye_path TEXT,
        right_eye_path TEXT,
        left_result TEXT,
        right_result TEXT,
        combined_result TEXT,
        report_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (doctor_id) REFERENCES users (id)
    )
    """)

    conn.commit()
    conn.close()
    print("✅ Initialized Upgraded DB at:", DB_PATH)

if __name__ == "__main__":
    init_db()