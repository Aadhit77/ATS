import os
import re
import fitz
import pymysql
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = 'resumes'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db = pymysql.connect(
    host='localhost',
    user='root',
    password='1234',
    database='ats_db',
    cursorclass=pymysql.cursors.DictCursor
)

def analyze_resume(resume_path):
    doc = fitz.open(resume_path)
    text = ""
    for page in doc:
        text += page.get_text()

    analysis = {
        "name": None,
        "bias_flags": [],
        "skills_detected": [],
        "fairness_score": 100
    }

    gendered_terms = ["he", "she", "his", "her", "male", "female"]
    for word in gendered_terms:
        if re.search(r'\b' + word + r'\b', text, re.IGNORECASE):
            analysis["bias_flags"].append(f"Found potentially biased word: {word}")
            analysis["fairness_score"] -= 5

    core_skills = ["python", "data analysis", "communication", "teamwork", "html", "css"]
    for skill in core_skills:
        if skill in text.lower():
            analysis["skills_detected"].append(skill)

    for line in text.strip().split('\n'):
        if line.strip() and re.match(r'^[A-Za-z\s]+$', line.strip()):
            analysis["name"] = line.strip()
            break

    return analysis

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def login_signup():
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        with db.cursor() as cursor:
            if form_type == 'signup':
                name = request.form.get('name')
                cursor.execute("SELECT * FROM user WHERE email = %s", (email,))
                if cursor.fetchone():
                    flash("User already exists!", "error")
                    return redirect(url_for('login_signup'))
                hashed_pw = generate_password_hash(password)
                cursor.execute("INSERT INTO user (name, email, password, role) VALUES (%s, %s, %s, %s)",
                               (name, email, hashed_pw, role))
                db.commit()
                flash("Signup successful! Please login.", "success")
                return redirect(url_for('login_signup'))

            elif form_type == 'login':
                cursor.execute("SELECT * FROM user WHERE email = %s", (email,))
                user = cursor.fetchone()
                if user and check_password_hash(user['password'], password) and user['role'] == role:
                    # Successful login, set the session user email
                    session['user_email'] = user['email']
                    return redirect(url_for('hr_dashboard') if role == 'hr' else url_for('applicant_dashboard'))
                else:
                    flash("Invalid credentials.", "error")
                    return redirect(url_for('login_signup'))

    return render_template('login_signup.html')


@app.route('/submit_application', methods=['POST'])
def submit_application():
    full_name = request.form['full_name']
    email_used_in_form = request.form['email']  # keep the form email
    job = request.form['job']
    location = request.form['location']
    experience = request.form['experience']
    resume = request.files['resume']

    # Logged in user email
    logged_in_user_email = session.get('user_email')

    if resume and allowed_file(resume.filename):
        filename = secure_filename(resume.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        resume.save(filepath)

        result = analyze_resume(filepath)
        detected_name = full_name
        detected_skills = ", ".join(result['skills_detected'])
        bias_flags = ", ".join(result['bias_flags'])

        with db.cursor() as cursor:
            cursor.execute("""
                INSERT INTO applicants 
                (name, email, job, location, experience, resume_filename, fairness_score, 
                 skills_detected, bias_flags, status, user_email)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'Pending', %s)
            """, (detected_name, email_used_in_form, job, location, experience, filename,
                  result['fairness_score'], detected_skills, bias_flags, logged_in_user_email))
            db.commit()

        flash("Application submitted successfully!", "success")
        return redirect(url_for('applicant_dashboard'))

    flash("Invalid resume format.", "error")
    return redirect(url_for('apply'))




def get_job_titles():
    with db.cursor() as cursor:
        cursor.execute("SELECT title FROM jobs")
        jobs = cursor.fetchall()
        return [job['title'] for job in jobs]


@app.route('/apply', methods=['GET', 'POST'])
def apply():
    job_titles = get_job_titles()  # Get job titles from the database
    return render_template('apply.html', job_titles=job_titles)


@app.route('/dashboard')
def dashboard():
    user_email = session.get('user_email')

    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM applicants WHERE email = %s ORDER BY id DESC", (user_email,))
        applicants = cursor.fetchall()

    return render_template('dashboard.html', applicants=applicants)

@app.route('/listing')
def listing():
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM jobs ORDER BY job_id DESC")
        jobs = cursor.fetchall()
    return render_template('listing.html', jobs=jobs)

@app.route('/applicant/dashboard')
def applicant_dashboard():
    user_email = session.get('user_email')
    if not user_email:
        flash("Please login first.", "warning")
        return redirect(url_for('login_signup'))

    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM applicants WHERE user_email = %s ORDER BY id DESC", (user_email,))
        applicants = cursor.fetchall()

    return render_template('dashboard.html', applicants=applicants)


@app.route('/hr/dashboard')
def hr_dashboard():
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM applicants ORDER BY id DESC")
        applicants = cursor.fetchall()
    return render_template('hr_dashboard.html', applicants=applicants)

@app.route('/update_status', methods=['POST'])
def update_status():
    applicant_id = request.form['applicant_id']
    new_status = request.form['status']

    try:
        with db.cursor() as cursor:
            sql = "UPDATE applicants SET status = %s WHERE id = %s"
            cursor.execute(sql, (new_status, applicant_id))
        db.commit()
        flash("Applicant status updated successfully!", "success")
    except Exception as e:
        print("Error updating applicant status:", e)
        flash("Failed to update status.", "danger")

    return redirect(url_for('hr_dashboard'))


@app.route('/view_applicants')
def view_applicants():
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM applicants ORDER BY id DESC")
        applicants = cursor.fetchall()
    return render_template('view_applicants.html', applicants=applicants)

@app.route('/post_job', methods=['GET', 'POST'])
def post_job():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        requirements = request.form['requirements']
        with db.cursor() as cursor:
            cursor.execute("INSERT INTO jobs (title, description, requirements) VALUES (%s, %s, %s)",
                           (title, description, requirements))
            db.commit()
        flash(f"Job '{title}' posted!", "success")
        return redirect(url_for('post_job'))
    return render_template('post_job.html')

@app.route('/resumes/<filename>')
def download_resume(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/logout')
def logout():
    session.pop('user_email', None)  # Remove user email from session
    flash("Logged out successfully.", "success")
    return redirect(url_for('login_signup'))


if __name__ == '__main__':
    app.run(debug=True)
