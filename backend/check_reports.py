import sqlite3, os
DB = "records.db"
UPLOAD_DIR = "uploads"


def main():
    print("DB:", DB)
    print("Uploads:", os.path.abspath(UPLOAD_DIR))
    files = set(os.listdir(UPLOAD_DIR)) if os.path.exists(UPLOAD_DIR) else set()
    print("Number of files in uploads:", len(files))
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT id, name, patient_id, report_id, report_filename, created_at FROM patients ORDER BY created_at DESC")
    rows = cur.fetchall()
    missing = []
    for r in rows:
        rid = r["report_id"]
        fname = r["report_filename"] if "report_filename" in r.keys() else None
        expected = fname if fname else f"{rid}.pdf"
        exists = expected in files
        status = "OK" if exists else "MISSING"
        print(f"id={r['id']:>3} name={r['name']:<20} report_id={rid} report_filename={fname} -> {status}")
        if not exists:
            missing.append((r["id"], r["name"], rid, expected))
    print()
    print("Total rows:", len(rows))
    print("Missing files count:", len(missing))
    if missing:
        print("\nMissing rows (id, name, report_id, expected_filename):")
        for x in missing:
            print(" ", x)
    conn.close()

if __name__ == '__main__':
    main()
