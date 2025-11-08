# backend/app.py (Final Version with Patient Portal and Image Reports)

import os # <-- Make sure 'os' is imported
import sqlite3
import uuid
from flask import (Flask, render_template, request, redirect, url_for,
                   send_from_directory, flash, session, abort) 
from werkzeug.security import generate_password_hash, check_password_hash
# We no longer need pathlib
# from pathlib import Path 

# --- Assuming backend_utils, report_generator, db_init are in the same directory ---
try:
    from backend_utils import preprocess_image, load_class_mapping, load_dr_model
    from report_generator import generate_pdf
    from db_init import init_db
except ImportError as e:
     print(f"Error importing local modules: {e}. Make sure files are in the 'backend' directory.")
     
# --- App Configuration: Points to your UI folder ---
app = Flask(__name__, template_folder='../Flask/templates', static_folder='../Flask/static')
app.secret_key = "visionai_final_submission_key_needs_to_be_stronger" # Change this!

# --- **START OF PATH FIX** ---
# --- Paths and Configuration ---
# Use standard 'os' module for all paths to ensure consistency
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads") # This is now a STRING
DB_PATH = os.path.join(BASE_DIR, "records.db") # This is now a STRING

# Create the uploads folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
# --- **END OF PATH FIX** ---

# --- Load AI Model ---
try:
    MODEL = load_dr_model()
    CLASS_MAPPING = load_class_mapping()
    print("✅ AI Model and class mappings loaded successfully.")
except Exception as e:
    print(f"❌ CRITICAL ERROR: Could not load the AI model. {e}")
    MODEL, CLASS_MAPPING = None, None 

# --- Database Helper ---
def get_db_connection():
    """Establishes connection to the SQLite database."""
    try:
        conn = sqlite3.connect(DB_PATH) # Use string path
        conn.row_factory = sqlite3.Row # Access columns by name
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

# --- Public Routes ---
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/services")
def services():
    return render_template("services.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

# --- Authentication Routes ---
@app.route("/doctor_login", methods=["GET", "POST"])
def doctor_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        conn = get_db_connection()
        if not conn:
            flash("Database error. Please try again later.", "danger")
            return render_template("doctorLog.html")

        user = conn.execute("SELECT * FROM users WHERE username = ? AND role = 'doctor'", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            session["full_name"] = user["full_name"] 
            flash(f"Welcome back, Dr. {user['full_name']}!", "success")
            return redirect(url_for("dashboard")) 
        else:
            flash("Invalid credentials or not a doctor account.", "danger")
    return render_template("doctorLog.html")

@app.route("/doctor_register", methods=["GET", "POST"])
def doctor_register():
    if request.method == "POST":
        required_fields = ["username", "password", "full_name", "contact_number", "hospital_name", "medical_id"]
        if not all(request.form.get(field) for field in required_fields):
            flash("Please fill out all required fields.", "warning")
            return render_template("doctorReg.html")

        hashed_password = generate_password_hash(request.form.get("password"))
        conn = get_db_connection()
        if not conn:
            flash("Database error. Please try again later.", "danger")
            return render_template("doctorReg.html")

        try:
            conn.execute("""
                INSERT INTO users (username, password, role, full_name, contact_number, hospital_name, medical_id)
                VALUES (?, ?, 'doctor', ?, ?, ?, ?)
            """, (
                request.form.get("username"), hashed_password,
                request.form.get("full_name"), request.form.get("contact_number"),
                request.form.get("hospital_name"), request.form.get("medical_id")
            ))
            conn.commit()
            flash("Doctor registration successful! Please log in.", "success")
            return redirect(url_for("doctor_login"))
        except sqlite3.IntegrityError:
            flash("That email address is already registered.", "danger")
        except sqlite3.Error as e:
             flash(f"Database error during registration: {e}", "danger")
        finally:
            if conn: conn.close()
    return render_template("doctorReg.html")

# --- Functional Patient Routes ---
@app.route("/patient_login", methods=["GET", "POST"])
def patient_login():
    if request.method == "POST":
        username_input = request.form.get("username")
        password_input = request.form.get("password")
        conn = get_db_connection()
        if not conn:
             flash("Database error. Please try again later.", "danger")
             return render_template("patientLog.html")

        user = conn.execute("SELECT * FROM users WHERE lower(username) = ? AND role = 'patient'",
                            (username_input.lower(),)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password_input):
            session["user_id"] = user["id"]
            session["username"] = user["username"] 
            session["role"] = user["role"]
            session["full_name"] = user["full_name"]
            flash(f"Welcome back, {user['full_name']}!", "success")
            return redirect(url_for("patient_dashboard"))
        else:
            flash("Invalid credentials or not a patient account.", "danger")
    return render_template("patientLog.html")

@app.route("/patient_register", methods=["GET", "POST"])
def patient_register():
    if request.method == "POST":
        required_fields = ["username", "password", "full_name", "contact_number", "address", "age", "gender"]
        if not all(request.form.get(field) for field in required_fields):
            flash("Please fill out all required fields.", "warning")
            return render_template("patientReg.html")

        hashed_password = generate_password_hash(request.form.get("password"))
        conn = get_db_connection()
        if not conn:
            flash("Database error. Please try again later.", "danger")
            return render_template("patientReg.html")
        try:
            conn.execute("""
                INSERT INTO users (username, password, role, full_name, contact_number, address, age, gender)
                VALUES (?, ?, 'patient', ?, ?, ?, ?, ?)
            """, (
                request.form.get("username"), hashed_password,
                request.form.get("full_name"), request.form.get("contact_number"),
                request.form.get("address"), request.form.get("age"),
                request.form.get("gender")
            ))
            conn.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("patient_login"))
        except sqlite3.IntegrityError:
            flash("That email address is already registered.", "danger")
        except sqlite3.Error as e:
            flash(f"Database error during registration: {e}", "danger")
        finally:
            if conn: conn.close()
    return render_template("patientReg.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))

# --- Doctor Portal (Login Required) ---
@app.route("/dashboard")
def dashboard():
    if session.get("role") != "doctor":
        flash("Please log in as a doctor to access the dashboard.", "warning")
        return redirect(url_for("doctor_login"))

    conn = get_db_connection()
    if not conn:
        flash("Database error. Cannot load dashboard.", "danger")
        return render_template("dashboard.html", patients=[], doctor=None)

    patients = conn.execute("SELECT * FROM patients WHERE doctor_id = ? ORDER BY created_at DESC", (session["user_id"],)).fetchall()
    doctor = conn.execute("SELECT full_name FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    conn.close()

    doctor_name = doctor['full_name'] if doctor else "Doctor"
    return render_template("dashboard.html", patients=patients, doctor={'full_name': doctor_name})

@app.route("/form")
def form():
    if session.get("role") != "doctor":
        return redirect(url_for("doctor_login"))

    doctor_name = session.get("full_name", "Doctor")
    return render_template("form.html", doctor={'full_name': doctor_name})

@app.route("/generate_report", methods=["POST"])
def generate_report():
    if session.get("role") != "doctor" or not MODEL:
        flash("Unauthorized or AI Model not available.", "danger")
        return redirect(url_for("doctor_login"))

    patient_info = {
        "name": request.form.get("patient_name"),
        "patient_id": request.form.get("patient_id"), # This MUST be patient's registered email
        "age": request.form.get("age"), "gender": request.form.get("gender"),
        "diabetes_duration": request.form.get("diabetes_duration"),
        "blood_pressure": request.form.get("blood_pressure"),
        "medications": request.form.get("medications"),
        "other_conditions": request.form.get("other_conditions"),
        "report_id": str(uuid.uuid4())
    }
    
    left_eye, right_eye = request.files.get("left_eye"), request.files.get("right_eye")

    if not all([patient_info["name"], patient_info["patient_id"], left_eye, right_eye]):
        flash("Please fill required fields (Name, Patient ID/Email) & upload both eye images.", "danger")
        return redirect(url_for("form"))

    # --- Use os.path.join for all path construction ---
    try:
        left_ext = os.path.splitext(left_eye.filename)[1]
        right_ext = os.path.splitext(right_eye.filename)[1]
        left_filename = f"{uuid.uuid4()}_left{left_ext}"
        right_filename = f"{uuid.uuid4()}_right{right_ext}"
        left_path = os.path.join(UPLOAD_FOLDER, left_filename)
        right_path = os.path.join(UPLOAD_FOLDER, right_filename)
        left_eye.save(left_path)
        right_eye.save(right_path)
    except Exception as e:
        flash(f"Error saving uploaded images: {e}", "danger")
        return redirect(url_for("form"))

    try:
        left_pred = MODEL.predict(preprocess_image(left_path)).argmax(axis=1)[0]
        right_pred = MODEL.predict(preprocess_image(right_path)).argmax(axis=1)[0]
    except Exception as e:
         flash(f"AI prediction failed: {e}. Ensure model & images are valid.", "danger")
         if os.path.exists(left_path): os.remove(left_path)
         if os.path.exists(right_path): os.remove(right_path)
         return redirect(url_for("form"))

    patient_info.update({
        "left_eye_path": left_path, # Pass absolute string path
        "right_eye_path": right_path,
        "left_result": CLASS_MAPPING.get(left_pred, "Unknown"),
        "right_result": CLASS_MAPPING.get(right_pred, "Unknown"),
        "combined_result": CLASS_MAPPING.get(max(left_pred, right_pred), "Unknown"),
    })

    conn = get_db_connection()
    if not conn:
        flash("Database error. Could not save report.", "danger")
        return redirect(url_for("form"))
    try:
        conn.execute("""
            INSERT INTO patients (doctor_id, name, patient_id, age, gender, diabetes_duration,
            blood_pressure, medications, other_conditions, left_eye_path, right_eye_path,
            left_result, right_result, combined_result, report_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session["user_id"], patient_info["name"], patient_info["patient_id"], patient_info["age"],
            patient_info["gender"], patient_info["diabetes_duration"], patient_info["blood_pressure"],
            patient_info["medications"], patient_info["other_conditions"],
            os.path.join("uploads", left_filename), # Store relative path in DB
            os.path.join("uploads", right_filename),
            patient_info["left_result"], patient_info["right_result"],
            patient_info["combined_result"], patient_info["report_id"]
        ))
        conn.commit()

        doctor = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
        
        # We will now check if the PDF generation succeeds
        try:
            pdf_report_path = os.path.join(UPLOAD_FOLDER, f"{patient_info['report_id']}.pdf")
            generate_pdf(patient_info, dict(doctor) if doctor else {}, pdf_report_path)
            
            # Only flash success if PDF generation ALSO succeeds
            flash("Report generated successfully!", "success")

        except Exception as e:
            # If PDF fails, print error and flash a specific, visible error
            print(f"❌ FAILED TO GENERATE PDF: {e}")
            flash(f"Report was saved to database, but PDF generation FAILED: {e}", "danger")
        
        return redirect(url_for("dashboard"))
    except sqlite3.IntegrityError:
        flash("A patient with this ID (email) already has a record.", "danger")
        return redirect(url_for("form"))
    except sqlite3.Error as e:
        flash(f"Database error saving report: {e}", "danger")
    finally:
        if conn: conn.close()
    return redirect(url_for("form"))

# --- Doctor: View/Download Specific Report ---
@app.route("/report/<report_id>")
def report(report_id):
    if "user_id" not in session:
        flash("Please log in to view reports.", "warning")
        return redirect(url_for("home"))

    conn = get_db_connection()
    if not conn: abort(500, description="Database connection failed")

    if session.get("role") == "doctor":
        report_data = conn.execute("SELECT * FROM patients WHERE report_id = ? AND doctor_id = ?",
                                   (report_id, session["user_id"])).fetchone()
    else:
         conn.close()
         abort(403) # Forbidden

    conn.close()

    if not report_data:
        flash("Report not found or permission denied.", "danger")
        return redirect(url_for("dashboard"))

    pdf_filename = f"{report_id}.pdf"
    
    # --- ** THIS IS THE FIX ** ---
    # Create the full, absolute path as a string
    pdf_path_str = os.path.join(UPLOAD_FOLDER, pdf_filename)
    
    # Use os.path.isfile() with the string path
    if os.path.isfile(pdf_path_str):
        action = request.args.get('action', 'view') 
        # Pass the string UPLOAD_FOLDER to send_from_directory
        return send_from_directory(UPLOAD_FOLDER, pdf_filename, as_attachment=(action == 'download'))
    else:
        # This is the error you are seeing
        flash(f"Report PDF file is missing from the server. [Path: {pdf_filename}]", "danger")
        print(f"❌ File check failed. Looking for: {pdf_path_str}") 
        return redirect(url_for("dashboard"))

# --- Patient Portal (Login Required) ---
@app.route("/patient_dashboard")
def patient_dashboard():
    if session.get("role") != "patient":
        return redirect(url_for("patient_login"))

    conn = get_db_connection()
    if not conn:
        flash("Database error.", "danger")
        return render_template("patient.html", reports=[], user=None)

    reports = conn.execute("SELECT * FROM patients WHERE patient_id = ? ORDER BY created_at DESC",
                           (session["username"],)).fetchall()
    user_details = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    conn.close()

    return render_template("patient.html", reports=reports, user=user_details)

# --- Patient Report Access ---
@app.route("/patient_report/<report_id>")
def patient_report(report_id):
    if session.get("role") != "patient":
        flash("Please log in as a patient.", "warning")
        return redirect(url_for("patient_login"))

    conn = get_db_connection()
    if not conn: abort(500, description="Database connection failed")

    report_data = conn.execute("SELECT * FROM patients WHERE report_id = ? AND patient_id = ?",
                               (report_id, session["username"])).fetchone()
    conn.close()

    if report_data:
        pdf_filename = f"{report_id}.pdf"
        
        # --- ** THIS IS THE FIX ** ---
        # Create the full, absolute path as a string
        pdf_path_str = os.path.join(UPLOAD_FOLDER, pdf_filename)
        
        # Use os.path.isfile() with the string path
        if os.path.isfile(pdf_path_str):
            action = request.args.get('action', 'view')
            # Pass the string UPLOAD_FOLDER to send_from_directory
            return send_from_directory(UPLOAD_FOLDER, pdf_filename, as_attachment=(action == 'download'))
        else:
            flash("Report PDF file is missing.", "danger")
            print(f"❌ File check failed (patient). Looking for: {pdf_path_str}")
            return redirect(url_for("patient_dashboard"))
    else:
        flash("Report not found or access denied.", "danger")
        return redirect(url_for("patient_dashboard"))
# --- ** END OF FIX ** ---

# --- Application Runner ---
if __name__ == "__main__":
    if not os.path.exists(DB_PATH): # Use os.path.exists
        print(f"Database not found at {DB_PATH}. Initializing...")
        try:
            init_db()
        except Exception as e:
            print(f"❌ Failed to initialize database: {e}")
    
    print("🚀 Starting VisionAI Flask server...")
    app.run(debug=True, port=5000)