# ✅ app.py (Final Combined Version)

from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'


# -------------------------
# ROUTES
# -------------------------

@app.route('/')
def home():
    """Render the homepage"""
    return render_template('index.html')


@app.route('/services')
def services():
    """Services page (currently uses same template)"""
    return render_template('services.html')


@app.route('/doctor')
def doctor():
    """Doctor page (currently uses same template)"""
    return render_template('doctorReg.html')

@app.route('/doctor_login')
def doctor_login():
    """Doctor page (currently uses same template)"""
    return render_template('doctorLog.html')

@app.route('/dashboard')
def dashboard():
    """Doctor page (currently uses same template)"""
    return render_template('dashboard.html')

@app.route('/form')
def form():
    """Doctor page (currently uses same template)"""
    return render_template('form.html')


@app.route('/patient')
def patient():
    """Patient page (currently uses same template)"""
    return render_template('patient.html')

@app.route('/patient_login')
def patient_login():
    """Patient page (currently uses same template)"""
    return render_template('patientLog.html')

@app.route('/patient_register')
def patient_register():
    """Patient page (currently uses same template)"""
    return render_template('patientReg.html')


@app.route('/contact')
def contact():
    """Contact page (currently uses same template)"""
    return render_template('contact.html')


@app.route('/generate-report', methods=['GET', 'POST'])
def generate_report():
    """Handle report generation requests"""
    if request.method == 'POST':
        # TODO: Add actual report generation logic here
        return jsonify({'status': 'success', 'message': 'Report generation feature coming soon'})
    
    # For GET requests, render index or a separate template if desired
    return render_template('index.html')


# -------------------------
# MAIN ENTRY POINT
# -------------------------

if __name__ == '__main__':
    # Run Flask app on all interfaces (useful for testing on local network)
    app.run(debug=True, host='0.0.0.0', port=5000)
