# backend/regenerate_one_report.py
import sqlite3, os, sys
from report_generator import generate_pdf

if len(sys.argv) < 2:
    print("Usage: python regenerate_one_report.py <report_id>")
    sys.exit(1)

report_id = sys.argv[1]
DB = "records.db"
UPLOAD_DIR = os.path.join("uploads")  # relative to backend folder

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
cur = conn.cursor()
row = cur.execute("SELECT * FROM patients WHERE report_id = ?", (report_id,)).fetchone()
if not row:
    print("No record found with report_id:", report_id)
    conn.close()
    sys.exit(1)

# Convert sqlite3.Row -> dict for safe .get() usage and clearer code
rowd = dict(row)

# Resolve image paths stored in DB (they might be "uploads/xxx.png" or just filenames)
def resolve_path(p):
    if not p:
        return None
    # if it's already an absolute path, return it
    if os.path.isabs(p):
        return p
    # possible stored forms: "uploads/xxx.png" or "xxx.png"
    cand1 = os.path.join(p)
    cand2 = os.path.join("uploads", os.path.basename(p))
    cand3 = os.path.join(os.getcwd(), p)
    cand4 = os.path.join(os.getcwd(), "uploads", os.path.basename(p))
    for c in (cand1, cand2, cand3, cand4):
        if os.path.exists(c):
            return os.path.abspath(c)
    return None

left = resolve_path(rowd.get("left_eye_path") or "")
right = resolve_path(rowd.get("right_eye_path") or "")

print("Resolved left image:", left)
print("Resolved right image:", right)

if not left or not right:
    print("One or both eye image files are missing on disk; cannot regenerate.")
    # For debugging, print DB-stored values:
    print("DB left_eye_path:", rowd.get("left_eye_path"))
    print("DB right_eye_path:", rowd.get("right_eye_path"))
    conn.close()
    sys.exit(1)

# Build patient_info dict expected by generate_pdf
patient_info = {
    "name": rowd.get("name", ""),
    "patient_id": rowd.get("patient_id", ""),
    "age": rowd.get("age", ""),
    "gender": rowd.get("gender", ""),
    "diabetes_duration": rowd.get("diabetes_duration", ""),
    "blood_pressure": rowd.get("blood_pressure", "") or rowd.get("blood_sugar_level", ""),
    "medications": rowd.get("medications", ""),
    "other_conditions": rowd.get("other_conditions", ""),
    "report_id": report_id,
    "left_eye_path": left,
    "right_eye_path": right,
    "left_result": rowd.get("left_result", ""),
    "right_result": rowd.get("right_result", ""),
    "combined_result": rowd.get("combined_result", "")
}

os.makedirs(UPLOAD_DIR, exist_ok=True)
pdf_filename = f"{report_id}.pdf"
pdf_path = os.path.join(UPLOAD_DIR, pdf_filename)

try:
    print("Generating PDF to:", pdf_path)
    generate_pdf(patient_info, {}, pdf_path)
    if not os.path.exists(pdf_path):
        print("Failed: generate_pdf did not create the PDF at:", pdf_path)
        conn.close()
        sys.exit(1)
    # Update DB report_filename if needed
    existing_fname = rowd.get("report_filename")
    if not existing_fname or existing_fname != pdf_filename:
        cur.execute("UPDATE patients SET report_filename = ? WHERE id = ?", (pdf_filename, rowd["id"]))
        conn.commit()
        print("DB updated report_filename ->", pdf_filename)
    print("Success: PDF created and DB updated ->", pdf_filename)
except Exception as e:
    print("Exception during PDF generation:", e)
finally:
    conn.close()
