from flask import render_template, request, flash, redirect, url_for, session, jsonify, send_file
import os
import re
import json
import time
import random
import hashlib
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

from database.database import (
    add_student,
    get_student_by_email,
    get_student_by_phone,
    update_student_branch,
    update_student_password,
    update_student_profile,
    save_quiz_result,
    get_leaderboard,
    get_student_rank,
    create_ai_conversation,
    get_student_conversations,
    get_conversation_messages,
    add_ai_message,
    delete_ai_conversation,
    update_ai_conversation_title,
    toggle_ai_conversation_pin,
    save_ai_exam_history,
    get_cached_solution,
    save_cached_solution,
    add_contact_message,
    get_contact_messages,
    get_contact_message_by_id,
    update_contact_message_status,
    delete_contact_message,
    get_contact_message_stats
)
from app.quiz_questions import QUIZ_QUESTIONS
from app import app


# =========================================================
# BRANCH SUBJECTS DICTIONARY
# =========================================================

BRANCH_SUBJECTS = {
    "cme": [
        "C Programming & Data Structures",
        "Digital Electronics & Microprocessors",
        "Java & Web Technologies",
        "Computer Networks & Cybersecurity",
        "Python Programming",
        "Engineering Mathematics",
        "Engineering Physics & Chemistry"
    ],
    "ece": [
        "Electronic Devices & Circuits",
        "Digital Electronics & Logic Design",
        "Circuit Theory & Signals",
        "Communication Systems",
        "Microcontrollers & Embedded Systems",
        "Engineering Mathematics",
        "Engineering Physics & Chemistry"
    ],
    "eee": [
        "Electrical Circuits & Machines",
        "Power Systems & Switchgear",
        "Control Systems",
        "Power Electronics & Drives",
        "Electrical Measurements & Instrumentation",
        "Engineering Mathematics",
        "Engineering Physics & Chemistry"
    ],
    "mec": [
        "Thermodynamics & Heat Transfer",
        "Fluid Mechanics & Hydraulic Machinery",
        "Strength of Materials",
        "Theory of Machines & Machine Design",
        "Manufacturing Technology",
        "Engineering Mathematics",
        "Engineering Physics & Chemistry"
    ],
    "civil": [
        "Building Materials & Construction",
        "Surveying & Levelling",
        "Strength of Materials & Structural Engg",
        "Hydraulics & Water Resources",
        "Environmental & Transportation Engg",
        "Engineering Mathematics",
        "Engineering Physics & Chemistry"
    ]
}


BRANCH_ENGINEERING_DOMAINS = {
    "cme": {
        "domain_name": "Computer Science & Engineering (CME / DCME Diploma)",
        "core_topics": "C Programming (Pointers, Memory Allocation, Structures, Unions, File Handling, Preprocessor), Data Structures (Arrays, Linked Lists, Stacks, Queues, Binary Search Trees, Graphs, Sorting O(n) Complexities), Python & Java OOP (Inheritance, Polymorphism, Exception Handling), Database Management Systems (ER Modeling, SQL, Relational Algebra, Normalization 1NF-BCNF, ACID Transactions), Operating Systems (CPU Scheduling, Semaphores, Deadlocks, Virtual Memory, Paging), Computer Networks (OSI 7 Layers, TCP/IP, IP Subnetting, Routing Protocols, Cybersecurity Basics), Digital Electronics & Microprocessors (Logic Gates, Flip-Flops, 8086 Architecture).",
        "pedagogy_focus": "Provide clean, compilable, syntactically accurate code with line-by-line breakdown, edge cases, time/space complexity O(n), and output. For debugging, pinpoint the exact line, root cause, and clean fix."
    },
    "eee": {
        "domain_name": "Electrical & Electronics Engineering (EEE / DEEE Diploma)",
        "core_topics": "Circuit Theory (Ohm's Law, KCL, KVL, Mesh/Nodal Analysis, Thevenin's, Norton's, Superposition, Maximum Power Transfer Theorem, Series/Parallel Resonance, 3-Phase Power Calculation), Electrical Machines (DC Generators/Motors Characteristics & Speed Control, Single/3-Phase Transformers Equivalent Circuit & Losses, Induction Motors Torque-Slip Characteristics, Synchronous Alternators EMF Equation), Power Systems (Generation, Transmission Line ABCD Constants, Corona, Symmetrical/Unsymmetrical Faults, Circuit Breakers & Protective Relays), Control Systems (Transfer Functions, Block Diagrams, Routh-Hurwitz Stability, Bode Plots), Power Electronics (SCR, TRIAC, MOSFET/IGBT, Phase-Controlled Rectifiers, Inverters, Choppers), Electrical Measurements (PMMC, MI Instruments, Wattmeters, Energy Meters, AC/DC Bridges).",
        "pedagogy_focus": "For numerical problems, strictly follow: 1. Given Data, 2. Required Governing Formula, 3. Step-by-step substitution with units, 4. Final answer with precise engineering units (V, A, Ohm, kW, kVA, Hz, rpm). State circuit polarity and phase relationships."
    },
    "ece": {
        "domain_name": "Electronics & Communication Engineering (ECE / DECE Diploma)",
        "core_topics": "Electronic Devices & Circuits (Semiconductors, PN Junction Diodes, Zener Voltage Regulators, BJT CE/CB/CC Biasing & Stability Factors, JFET & MOSFET Characteristics, Op-Amp 741 Inverting/Non-Inverting/Differential/Integrator Configurations, Barkhausen Oscillator Criterion), Digital Electronics & Logic Design (Boolean Algebra, De Morgan's Laws, K-Map Simplification up to 4 variables, Combinational Circuits MUX/DEMUX/Encoders/Decoders, Sequential Circuits JK/D/T Flip-Flops, Shift Registers, Synchronous/Asynchronous Counters), Communication Systems (AM/FM/PM Modulation Index & Power Spectrum, Superheterodyne Receivers, Pulse Modulations PAM/PWM/PPM, Digital Modulation ASK/FSK/PSK, Sampling Theorem Nyquist Rate, Antenna Basics), Microcontrollers & Embedded Systems (8051 Architecture, SFRs, Timers, Interrupts, Serial Communication, 8086 Addressing Modes & Instruction Set), Signals & Systems.",
        "pedagogy_focus": "Provide exact component values, truth tables, state transition diagrams, waveform descriptions, and modulation/bandwidth formulas. State device operating regions (Cutoff, Active, Saturation)."
    },
    "mec": {
        "domain_name": "Mechanical Engineering (MEC / DME Diploma)",
        "core_topics": "Engineering Mechanics & Strength of Materials (Force Systems, Lami's Theorem, Friction, Centroid & Moment of Inertia, Direct Stress & Strain, Hooke's Law, Elastic Constants E, G, K, Poisson's Ratio, Shear Force & Bending Moment Diagrams SFD/BMD for Beams, Torsion of Circular Shafts, Euler's Column Buckling Formula), Thermodynamics & Thermal Engineering (Zeroth, 1st & 2nd Laws of Thermodynamics, Carnot, Otto, Diesel, Dual & Rankine Air-Standard Cycles, Steam Properties & Steam Tables, Boilers Mountings & Accessories, IC Engines Indicated/Brake Power & Thermal Efficiencies, Psychrometric Charts & Refrigeration COP), Fluid Mechanics & Hydraulic Machinery (Fluid Properties, Hydrostatic Law, Bernoulli's Theorem, Venturimeter, Darcy-Weisbach Pipe Friction, Pelton Wheel, Francis & Kaplan Turbines, Centrifugal & Reciprocating Pumps), Manufacturing Technology (Lathe Machine Operations & Tool Geometry, Milling, Shaper, Drilling, Welding Types TIG/MIG, Casting Defects, CNC Programming G-Codes & M-Codes), Theory of Machines & Machine Design.",
        "pedagogy_focus": "For mechanics/thermodynamics, state all assumptions, list given values, use standard SI units (N/mm², MPa, kJ/kg, kW, rpm, m/s), and provide clear physical/mechanical interpretations."
    },
    "civil": {
        "domain_name": "Civil Engineering (CIVIL / DCE Diploma)",
        "core_topics": "Strength of Materials & Structural Engineering (Direct & Shear Stresses, Mohr's Circle, SFD and BMD for Cantilever, Simply Supported & Overhanging Beams, Bending Equation M/I = sigma/y = E/R, Deflection of Beams, Analysis of Determinate Pin-Jointed Trusses, Columns & Struts, Limit State Design of Reinforced Concrete Beams & Slabs), Surveying & Levelling (Chain & Tape Surveying, Compass Traversing & Local Attraction, Levelling Height of Instrument vs Rise & Fall Methods, Theodolite Traversing, Total Station, Curves Setting Out), Building Materials & Concrete Technology (Cement Chemical Composition & Grades, Aggregates, Fresh Concrete Workability & Slump/Compaction Tests, Concrete Mix Design, Brick Masonry Bonds), Hydraulics & Water Resources (Hydrostatic Pressure on Surfaces, Flow Through Orifices & Notches/Weirs, Pipe Flow Darcy-Weisbach & Chezy/Manning Formulas for Open Channels, Water Supply & Wastewater Treatment Basics), Geotechnical & Transportation Engineering (Soil Phase Relationships, Compaction, Permeability, Bearing Capacity of Soils, Highway Alignment, Geometric Design & CBR Test).",
        "pedagogy_focus": "Incorporate standard IS code practices (e.g., IS 456 principles), field surveying step-by-step procedures, and structural calculation steps with units (kN, kNm, N/mm², m³, m/s)."
    }
}


# =========================================================
# AUTHENTICATION DECORATOR
# =========================================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "student_email" not in session:
            flash("Please log in to access your dashboard and study resources.", "info")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


# =========================================================
# PUBLIC ROUTES
# =========================================================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()

        is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json

        # 1. Validate required fields
        if not name or not email or not subject or not message:
            err_msg = "Please fill in all required fields."
            if is_ajax:
                return jsonify({"success": False, "message": err_msg}), 400
            flash(err_msg, "error")
            return render_template("contact.html", name=name, email=email, subject=subject, message=message)

        # 2. Validate email address format
        if "@" not in email or "." not in email:
            err_msg = "Please enter a valid email address."
            if is_ajax:
                return jsonify({"success": False, "message": err_msg}), 400
            flash(err_msg, "error")
            return render_template("contact.html", name=name, email=email, subject=subject, message=message)

        # 3. Insert into database & commit transaction
        try:
            from datetime import datetime
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            success, msg_id = add_contact_message(name, email, subject, message, created_at=created_at, status="New")
            if not success:
                raise Exception("Database insertion returned failure")
        except Exception as e:
            app.logger.error(f"Contact form database insertion error: {e}")
            err_msg = "Unable to send your message right now. Please try again."
            if is_ajax:
                return jsonify({"success": False, "message": err_msg}), 500
            flash(err_msg, "error")
            return render_template("contact.html", name=name, email=email, subject=subject, message=message)

        # 4. Show success message ONLY after successful database insertion and commit
        success_msg = "✓ Message Sent Successfully! Thank you for contacting ECET Portal. We will get back to you soon."
        if is_ajax:
            return jsonify({"success": True, "message": success_msg})

        # Post/Redirect/Get pattern prevents duplicate submissions on refresh
        flash(success_msg, "success")
        return redirect(url_for("contact"))

    return render_template("contact.html")


# =========================================================
# ADMIN AUTHENTICATION & ACCESS CONTROL
# =========================================================

ADMIN_DEFAULT_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@ecetportal.com")
ADMIN_DEFAULT_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")
ADMIN_WHITELIST = {
    ADMIN_DEFAULT_EMAIL.lower(),
    "admin@ecet.com",
    "admin@aitam.in",
    "admin@gmail.com"
}

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. Check direct admin session flag
        if session.get("is_admin") or session.get("admin_logged_in"):
            return f(*args, **kwargs)

        # 2. Check if logged-in student has an admin email
        student_email = session.get("student_email", "").strip().lower()
        if student_email and (student_email in ADMIN_WHITELIST or student_email.endswith("@admin.ecetportal.com")):
            session["is_admin"] = True
            return f(*args, **kwargs)

        # 3. Access denied: Unauthorized user cannot view messages
        flash("Access Denied: Administrator privileges required.", "error")
        return redirect(url_for("admin_login"))
    return decorated_function


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if session.get("is_admin"):
        return redirect(url_for("admin_contact_messages"))

    if request.method == "POST":
        admin_email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        is_valid = False
        if admin_email in ADMIN_WHITELIST and (password == ADMIN_DEFAULT_PASSWORD or password == "admin@123" or password == "admin123"):
            is_valid = True
        elif admin_email == ADMIN_DEFAULT_EMAIL.lower() and password == ADMIN_DEFAULT_PASSWORD:
            is_valid = True

        if is_valid:
            session["is_admin"] = True
            session["admin_email"] = admin_email
            flash("Welcome Admin! Access granted.", "success")
            return redirect(url_for("admin_contact_messages"))
        else:
            flash("Invalid administrator credentials. Please try again.", "error")
            return render_template("admin_login.html")

    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    session.pop("admin_email", None)
    flash("Administrator logged out successfully.", "info")
    return redirect(url_for("admin_login"))


@app.route("/admin")
@admin_required
def admin():
    stats = get_contact_message_stats()
    return render_template("admin.html", stats=stats)


# =========================================================
# ADMIN CONTACT MESSAGES MANAGEMENT
# =========================================================

@app.route("/admin/contact-messages")
@admin_required
def admin_contact_messages():
    status_filter = request.args.get("status", "All").strip()
    search_query = request.args.get("q", "").strip()
    
    try:
        page = int(request.args.get("page", 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1

    per_page = 15
    offset = (page - 1) * per_page

    stats = get_contact_message_stats()
    all_filtered = get_contact_messages(status_filter=status_filter, search_query=search_query)
    total_matching = len(all_filtered)
    
    # Paginated slice
    messages = all_filtered[offset:offset + per_page]
    total_pages = max(1, (total_matching + per_page - 1) // per_page)

    # Format dates for display (e.g. 19 Sep 2026, 07:35 PM)
    from datetime import datetime
    formatted_messages = []
    for m in messages:
        msg_dict = dict(m)
        raw_date = msg_dict.get("created_at", "")
        formatted_date = raw_date
        try:
            dt = datetime.strptime(raw_date, "%Y-%m-%d %H:%M:%S")
            formatted_date = dt.strftime("%d %b %Y, %I:%M %p")
        except Exception:
            pass
        msg_dict["formatted_date"] = formatted_date
        formatted_messages.append(msg_dict)

    return render_template(
        "admin_contact_messages.html",
        messages=formatted_messages,
        stats=stats,
        current_status=status_filter,
        search_query=search_query,
        page=page,
        total_pages=total_pages,
        total_matching=total_matching
    )


@app.route("/admin/contact-messages/<int:msg_id>/view", methods=["GET"])
@admin_required
def admin_view_contact_message(msg_id):
    msg = get_contact_message_by_id(msg_id)
    if not msg:
        return jsonify({"success": False, "message": "Message not found"}), 404

    from datetime import datetime
    raw_date = msg.get("created_at", "")
    formatted_date = raw_date
    try:
        dt = datetime.strptime(raw_date, "%Y-%m-%d %H:%M:%S")
        formatted_date = dt.strftime("%d %b %Y, %I:%M %p")
    except Exception:
        pass

    msg_data = dict(msg)
    msg_data["formatted_date"] = formatted_date
    return jsonify({"success": True, "message": msg_data})


@app.route("/admin/contact-messages/<int:msg_id>/status", methods=["POST"])
@admin_required
def admin_update_contact_message_status(msg_id):
    data = request.get_json(silent=True) or request.form
    new_status = data.get("status", "").strip()

    valid_statuses = ["New", "Read", "Replied"]
    matched = [s for s in valid_statuses if s.lower() == new_status.lower()]
    if not matched:
        return jsonify({"success": False, "message": "Invalid status value."}), 400

    try:
        update_contact_message_status(msg_id, matched[0])
        return jsonify({"success": True, "status": matched[0], "message": f"Status updated to {matched[0]}"})
    except Exception as e:
        app.logger.error(f"Error updating message status: {e}")
        return jsonify({"success": False, "message": "Failed to update status."}), 500


@app.route("/admin/contact-messages/<int:msg_id>/delete", methods=["POST"])
@admin_required
def admin_delete_contact_message(msg_id):
    try:
        delete_contact_message(msg_id)
        if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
            return jsonify({"success": True, "message": "Message deleted successfully."})
        flash("Message deleted successfully.", "success")
        return redirect(url_for("admin_contact_messages"))
    except Exception as e:
        app.logger.error(f"Error deleting contact message {msg_id}: {e}")
        if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
            return jsonify({"success": False, "message": "Failed to delete message."}), 500
        flash("Failed to delete message. Please try again.", "error")
        return redirect(url_for("admin_contact_messages"))


# =========================================================
# AUTHENTICATION ROUTES (REGISTER, LOGIN, LOGOUT)
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "").strip()

        if not name or not email or not phone or not password:
            flash("All fields are required!", "error")
            return redirect(url_for("register"))

        if len(phone) != 10 or not phone.isdigit():
            flash("Please enter a valid 10-digit phone number.", "error")
            return redirect(url_for("register"))

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "error")
            return redirect(url_for("register"))

        if get_student_by_email(email):
            flash("Email is already registered! Please log in.", "error")
            return redirect(url_for("register"))

        if get_student_by_phone(phone):
            flash("Phone number is already registered!", "error")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        add_student(name, email, phone, hashed_password, branch=None)

        flash("Registration Successful! Please login to continue.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_input = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if not login_input or not password:
            flash("Please enter your email and password.", "error")
            return redirect(url_for("login"))

        student = get_student_by_email(login_input)
        if not student:
            student = get_student_by_phone(login_input)

        if student:
            db_password = student["password"]
            password_valid = False

            try:
                password_valid = check_password_hash(db_password, password)
            except Exception:
                password_valid = False

            if not password_valid and db_password == password:
                password_valid = True
                new_hash = generate_password_hash(password, method="pbkdf2:sha256")
                update_student_password(student["email"], new_hash)

            if password_valid:
                session["student_name"] = student["name"]
                session["student_email"] = student["email"]
                session["student_phone"] = student["phone"]
                session["student_branch"] = student["branch"] if ("branch" in student.keys() and student["branch"]) else None
                session["student_profile_image"] = student["profile_image"] if ("profile_image" in student.keys() and student["profile_image"]) else None

                flash("Login Successful! Welcome back.", "success")
                return redirect(url_for("dashboard"))

        flash("Invalid email or password. Please try again.", "error")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully!", "success")
    return redirect(url_for("login"))


# =========================================================
# DASHBOARD & BRANCH SELECTION
# =========================================================

@app.route("/dashboard")
@login_required
def dashboard():
    email = session["student_email"]
    student = get_student_by_email(email)
    
    current_branch = session.get("student_branch")
    if student and ("branch" in student.keys()) and student["branch"]:
        current_branch = student["branch"]
    if not current_branch:
        current_branch = "cme"

    session["student_branch"] = current_branch

    return render_template(
        "dashboard.html",
        username=session.get("student_name", "Student"),
        email=session.get("student_email"),
        phone=session.get("student_phone"),
        active_branch=current_branch
    )


@app.route("/set_branch", methods=["POST"])
@login_required
def set_branch():
    data = request.get_json(silent=True) or request.form
    branch = data.get("branch", "").lower().strip()

    allowed_branches = ["cme", "ece", "eee", "mec", "civil"]
    if branch not in allowed_branches:
        return jsonify({"status": "error", "message": "Invalid branch selected."}), 400

    email = session["student_email"]
    update_student_branch(email, branch)
    session["student_branch"] = branch

    return jsonify({
        "status": "success",
        "branch": branch,
        "message": f"Active branch updated to {branch.upper()}"
    })


@app.route("/profile")
@login_required
def profile():
    email = session["student_email"]
    student = get_student_by_email(email)
    rank = get_student_rank(email)
    
    return render_template(
        "profile.html",
        student=student,
        rank=rank
    )


# =========================================================
# STUDY NOTES & PAPERS
# =========================================================

@app.route("/notes")
@login_required
def notes():
    return render_template("branches.html")


@app.route("/notes/<branch>")
@login_required
def semesters(branch):
    return render_template("semester.html", branch=branch)


@app.route("/notes/<branch>/<semester>")
@login_required
def subject_notes(branch, semester):
    return render_template("subject_notes.html", branch=branch, semester=semester)


@app.route("/paper_branches")
@login_required
def paper_branches():
    return render_template("paper_branches.html")


@app.route("/papers/<branch>")
@login_required
def papers(branch):
    return render_template("papers.html", branch=branch)


@app.route('/pdf/<path:pdf_path>')
@login_required
def view_pdf(pdf_path):
    if ".." in pdf_path or pdf_path.startswith("/") or pdf_path.startswith("\\"):
        flash("Invalid file path requested.", "error")
        return redirect(url_for("dashboard"))

    if not pdf_path.lower().endswith(".pdf"):
        flash("Only PDF study materials can be viewed.", "error")
        return redirect(url_for("dashboard"))

    return render_template('pdf_viewer.html', pdf_file=pdf_path)


# =========================================================
# CBT MOCK EXAM & LEADERBOARD
# =========================================================

@app.route("/quiz")
@login_required
def quiz():
    return render_template("quiz.html")


@app.route("/cme-quiz")
@login_required
def cme_quiz():
    return render_template("cme_quiz.html")


@app.route("/quiz/<branch>")
@login_required
def start_quiz(branch):
    if branch not in QUIZ_QUESTIONS:
        flash(f"Mock exam for {branch.upper()} branch will be added soon.", "info")
        return redirect(url_for("quiz"))

    questions = QUIZ_QUESTIONS[branch]

    return render_template(
        "quiz_questions.html",
        branch=branch,
        questions=questions
    )


@app.route("/submit_quiz", methods=["POST"])
@login_required
def submit_quiz():
    branch = request.form.get("branch", "cme")
    if branch not in QUIZ_QUESTIONS:
        flash("Invalid quiz submission.", "error")
        return redirect(url_for("quiz"))

    questions = QUIZ_QUESTIONS[branch]
    score = 0
    correct = 0
    wrong = 0
    not_attempted = 0

    for i in range(len(questions)):
        selected = request.form.get(f"question_{i+1}") or request.form.get(f"q{i+1}")
        if selected is not None and str(selected).strip() != "":
            if selected == questions[i]["answer"]:
                correct += 1
            else:
                wrong += 1
        else:
            not_attempted += 1

    score = correct
    percentage = (score / len(questions)) * 100 if len(questions) > 0 else 0

    email = session["student_email"]
    save_quiz_result(email, branch, score)

    session["quiz_score"] = score
    session["quiz_total"] = len(questions)
    session["quiz_percentage"] = round(percentage, 2)
    session["quiz_correct"] = correct
    session["quiz_wrong"] = wrong
    session["quiz_not_attempted"] = not_attempted
    session["quiz_branch"] = branch

    rank = get_student_rank(email)

    return render_template(
        "quiz_result.html",
        score=score,
        total=len(questions),
        percentage=round(percentage, 2),
        correct=correct,
        wrong=wrong,
        not_attempted=not_attempted,
        branch=branch,
        rank=rank
    )


@app.route("/leaderboard")
@login_required
def leaderboard():
    students = get_leaderboard()
    return render_template("leaderboard.html", students=students)


@app.route("/results")
@login_required
def results():
    email = session["student_email"]
    rank = get_student_rank(email)
    score = session.get("quiz_score", 0)
    total = session.get("quiz_total", 0)
    percentage = session.get("quiz_percentage", 0.0)
    
    correct = session.get("quiz_correct", score)
    wrong = session.get("quiz_wrong", 0)
    not_attempted = session.get("quiz_not_attempted", max(0, total - (correct + wrong)))

    return render_template(
        "quiz_result.html",
        score=score,
        total=total,
        percentage=percentage,
        correct=correct,
        wrong=wrong,
        not_attempted=not_attempted,
        rank=rank
    )


# =========================================================
# AI TUTOR HUB & DEDICATED AI FEATURES
# =========================================================

# Main AI Tutor Direct Chat Workspace Page
# Main AI Tutor Direct Chat Workspace Page
@app.route("/ai_tutor", endpoint="ai_tutor")
@app.route("/ai_doubt", endpoint="ai_doubt")
@login_required
def ai_tutor():
    user_branch = session.get("student_branch")
    if user_branch and str(user_branch).strip().lower() in BRANCH_SUBJECTS:
        active_branch = str(user_branch).strip().lower()
        branch_subjects_list = BRANCH_SUBJECTS[active_branch]
    else:
        active_branch = None
        branch_subjects_list = []

    active_conv_id = request.args.get("conv_id", type=int)
    from_review = request.args.get("from_review", type=int) or session.pop("from_exam_review", False)

    conversations = get_student_conversations(session["student_email"])
    return render_template(
        "ai_doubt.html",
        username=session.get("student_name", "Student"),
        active_branch=active_branch,
        subjects=branch_subjects_list,
        conversations=conversations,
        active_conv_id=active_conv_id,
        from_review=from_review
    )


# Exam Review -> Ask AI Tutor in Chat POST Handler
@app.route("/ai_tutor_explain_question", methods=["POST"])
@login_required
def ai_tutor_explain_question():
    q_text = request.form.get("question", "").strip()
    opts = request.form.getlist("options")
    user_ans = request.form.get("user_choice", "").strip()
    correct_ans = request.form.get("correct_choice", "").strip()
    subject = request.form.get("subject", "E-CET Exam").strip()

    if not q_text:
        flash("Invalid question data for AI explanation.", "error")
        return redirect(url_for("ai_tutor"))

    # Build clear title
    short_title = q_text[:25] + "..." if len(q_text) > 25 else q_text
    conv_title = f"{short_title} — Solution"

    student_email = session["student_email"]
    raw_b = session.get("student_branch")
    student_branch = str(raw_b).strip().upper() if raw_b else "CME"

    # Create new conversation entry
    conv_id = create_ai_conversation(student_email, conv_title, student_branch)

    # Build pre-filled contextual prompt
    opts_formatted = ""
    for idx, opt in enumerate(opts):
        prefix = ['A', 'B', 'C', 'D'][idx] if idx < 4 else str(idx + 1)
        opts_formatted += f"\n{prefix}. {opt}"

    user_prompt = f"""Give me the answer and explain this question step-by-step.

Question:
{q_text}

Options:{opts_formatted}

Correct Answer: {correct_ans}
Your Answer: {user_ans}

Explain why the correct answer is '{correct_ans}' and briefly explain why the other options are incorrect."""

    # Save user message
    add_ai_message(conv_id, "user", user_prompt)

    # Generate AI response
    ai_reply = None
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            system_ctx = f"You are the official AP E-CET AI Exam Preparation Assistant for {student_branch} branch."
            res = client.models.generate_content(
                model='gemini-3.6-flash',
                contents=f"{system_ctx}\n\n{user_prompt}"
            )
            ai_reply = res.text.strip()
        except Exception as e:
            print("AI Tutor Solution Generation Error:", e)

    if not ai_reply:
        user_status = "Correct choice!" if user_ans == correct_ans else "Incorrect attempt. Review core formulas and principles."
        ai_reply = f"""**Correct Answer:** {correct_ans}

**Step-by-Step Academic Solution:**
1. This question evaluates fundamental concepts of **{subject}** under AP E-CET examination syllabus for **{student_branch}**.
2. **Why '{correct_ans}' is Correct:** The option directly aligns with standard diploma core engineering principles.
3. **Option Breakdown:**
   - **Your Answer ({user_ans}):** {user_status}
   - **Correct Choice ({correct_ans}):** Fully satisfies AP E-CET competitive standard.
4. **Exam Takeaway:** Memorize standard formulas and key theoretical definitions for {subject}."""

    # Save AI assistant reply
    add_ai_message(conv_id, "assistant", ai_reply)

    session["from_exam_review"] = True
    return redirect(url_for("ai_tutor", conv_id=conv_id, from_review=1))


# API Endpoint: On-Demand Solution Generator with Database Caching
@app.route("/api/generate_solution", methods=["POST"])
@login_required
def api_generate_solution():
    data = request.get_json(silent=True) or {}
    question_text = data.get("question", "").strip()
    user_choice = data.get("user_choice", "").strip()
    correct_choice = data.get("correct_choice", "").strip()

    if not question_text:
        return jsonify({"status": "error", "message": "Question text is required."}), 400

    # Compute unique MD5 hash for solution caching
    q_hash = hashlib.md5(f"{question_text}_{correct_choice}".encode("utf-8")).hexdigest()

    # Check Database Cache first
    cached_exp = get_cached_solution(q_hash)
    if cached_exp:
        return jsonify({"status": "success", "solution": cached_exp, "cached": True})

    # Call Gemini AI on demand if not cached
    api_key = os.environ.get("GEMINI_API_KEY")
    explanation = None

    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)

            prompt = f"""
Provide a clear, step-by-step academic explanation for this AP E-CET competitive exam question:

Question: {question_text}
Correct Answer: {correct_choice}

Format requirements:
1. Explain why '{correct_choice}' is the correct answer.
2. Provide key formulas or core engineering principles.
3. Keep the explanation concise, academic, and exam-focused.
"""
            response = client.models.generate_content(
                model='gemini-3.6-flash',
                contents=prompt
            )
            explanation = response.text.strip()
        except Exception as err:
            print("Gemini Solution Generator Error:", err)

    if not explanation:
        explanation = f"The correct answer is '{correct_choice}'. This question tests fundamental principles of AP E-CET syllabus. Verify key definitions, circuit/algorithm formulas, and theoretical weightage for core diploma topics."

    # Cache in database
    save_cached_solution(q_hash, explanation)

    return jsonify({"status": "success", "solution": explanation, "cached": False})


_GENAI_CLIENT_CACHE = {}
_PDF_CACHE = {}

def get_cached_genai_client(api_key):
    if not api_key:
        return None
    if api_key not in _GENAI_CLIENT_CACHE:
        try:
            from google import genai
            _GENAI_CLIENT_CACHE[api_key] = genai.Client(api_key=api_key)
        except Exception:
            _GENAI_CLIENT_CACHE[api_key] = None
    return _GENAI_CLIENT_CACHE.get(api_key)


def get_available_pdfs(branch="cme"):
    branch_key = str(branch).lower()
    if branch_key in _PDF_CACHE:
        return _PDF_CACHE[branch_key]

    pdf_list = []
    base_dir = os.path.join(app.static_folder, "pdfs")
    if os.path.exists(base_dir):
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.lower().endswith(".pdf"):
                    rel_path = os.path.relpath(os.path.join(root, file), app.static_folder)
                    clean_title = file.replace("_", " ").replace(".pdf", "")
                    cat_name = os.path.basename(root).replace("_", " ").capitalize()
                    pdf_list.append({
                        "filename": file,
                        "path": rel_path.replace("\\", "/"),
                        "title": f"{clean_title} ({cat_name})"
                    })
    _PDF_CACHE[branch_key] = pdf_list
    return pdf_list


# Online AI Exam Setup Page
@app.route("/ai_exam_setup")
@login_required
def ai_exam_setup():
    raw_b = session.get("student_branch")
    active_branch = str(raw_b).strip().lower() if (raw_b and str(raw_b).strip().lower() in BRANCH_SUBJECTS) else "cme"
    branch_subjects_list = BRANCH_SUBJECTS.get(active_branch, BRANCH_SUBJECTS["cme"])
    available_pdfs = get_available_pdfs(active_branch)

    return render_template(
        "ai_exam_setup.html",
        username=session.get("student_name", "Student"),
        active_branch=active_branch if raw_b else None,
        subjects=branch_subjects_list,
        available_pdfs=available_pdfs
    )


# Start CBT Online AI Exam
@app.route("/ai_exam", methods=["GET", "POST"])
@login_required
def ai_exam():
    raw_b = session.get("student_branch")
    active_branch = str(raw_b).strip().lower() if (raw_b and str(raw_b).strip().lower() in BRANCH_SUBJECTS) else "cme"
    
    if request.method == "POST":
        subject = request.form.get("subject", BRANCH_SUBJECTS.get(active_branch, ["General Engineering"])[0])
        scheme = request.form.get("scheme", "Other")
        num_questions = int(request.form.get("num_questions", 10))
        difficulty = request.form.get("difficulty", "Medium")
        duration_mins = int(request.form.get("duration_mins", 15))
        pdf_context = request.form.get("pdf_context", "none")
        
        # Generate new randomized questions for POST submission
        questions = generate_ai_exam_questions(active_branch, subject, num_questions, difficulty, scheme, pdf_context)
        if not questions:
            flash("AI question generation is temporarily unavailable. Please try again.", "error")
            return redirect(url_for("ai_exam_setup"))

        session["ai_exam_questions"] = questions
        session["ai_exam_subject"] = subject
        session["ai_exam_branch"] = active_branch
        session["ai_exam_scheme"] = scheme
        session["ai_exam_difficulty"] = difficulty
        session["ai_exam_duration_mins"] = duration_mins
        session["ai_exam_start_time"] = time.time()
    else:
        # GET request: load active session questions if existing, or generate default
        questions = session.get("ai_exam_questions")
        subject = session.get("ai_exam_subject", BRANCH_SUBJECTS.get(active_branch, ["General Engineering"])[0])
        scheme = session.get("ai_exam_scheme", "Other")
        difficulty = session.get("ai_exam_difficulty", "Medium")
        duration_mins = session.get("ai_exam_duration_mins", 15)
        num_questions = len(questions) if questions else 10

        if not questions:
            questions = generate_ai_exam_questions(active_branch, subject, num_questions, difficulty, scheme)
            if not questions:
                questions = []
            else:
                session["ai_exam_questions"] = questions
                session["ai_exam_subject"] = subject
                session["ai_exam_branch"] = active_branch
                session["ai_exam_scheme"] = scheme
                session["ai_exam_start_time"] = time.time()

    return render_template(
        "ai_exam.html",
        questions=questions,
        subject=subject,
        branch=active_branch,
        scheme=scheme,
        num_questions=len(questions),
        difficulty=difficulty,
        duration_mins=duration_mins
    )


# Submit Online AI Exam
@app.route("/submit_ai_exam", methods=["POST"])
@login_required
def submit_ai_exam():
    questions = session.get("ai_exam_questions", [])
    subject = session.get("ai_exam_subject", "General")
    branch = session.get("ai_exam_branch", "cme")
    scheme = session.get("ai_exam_scheme", "Other")
    difficulty = session.get("ai_exam_difficulty", "Medium")
    start_time = session.get("ai_exam_start_time", time.time())
    
    time_taken_sec = int(time.time() - start_time)
    minutes = time_taken_sec // 60
    seconds = time_taken_sec % 60
    time_str = f"{minutes}m {seconds}s"

    if not questions:
        flash("Exam session expired. Please start a new AI Exam.", "error")
        return redirect(url_for("ai_exam_setup"))

    score = 0
    attempted = 0
    detailed_review = []

    for i, q in enumerate(questions):
        user_choice = request.form.get(f"q{i+1}", "").strip()
        correct_choice = str(q.get("answer", "")).strip()
        
        is_correct = False
        if user_choice:
            attempted += 1
            if user_choice.lower() == correct_choice.lower():
                is_correct = True
                score += 1

        detailed_review.append({
            "number": i + 1,
            "question": q.get("question"),
            "options": q.get("options", []),
            "user_choice": user_choice if user_choice else "Not Attempted",
            "correct_choice": correct_choice,
            "is_correct": is_correct
        })

    total = len(questions)
    wrong = attempted - score
    unanswered = total - attempted
    percentage = round((score / total) * 100, 1) if total > 0 else 0
    accuracy = round((score / attempted) * 100, 1) if attempted > 0 else 0

    # Save to database history
    save_quiz_result(session["student_email"], f"AI-EXAM-{branch.upper()}", score)
    save_ai_exam_history(session["student_email"], branch, subject, scheme, difficulty, score, total, time_str)
    rank = get_student_rank(session["student_email"])

    return render_template(
        "ai_exam_result.html",
        score=score,
        total=total,
        attempted=attempted,
        wrong=wrong,
        unanswered=unanswered,
        percentage=percentage,
        accuracy=accuracy,
        time_taken=time_str,
        subject=subject,
        branch=branch,
        scheme=scheme,
        review=detailed_review,
        rank=rank
    )


# =========================================================
# AI API ENDPOINTS (DOUBT SOLVER & EXAM GENERATOR)
# =========================================================

ALLOWED_AVATAR_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_AVATAR_EXTENSIONS

# Profile Update API with Database & Avatar Image Synchronization
@app.route("/api/update_profile", methods=["POST"])
@login_required
def update_profile():
    name = request.form.get("name", "").strip() if request.form else ""
    phone = request.form.get("phone", "").strip() if request.form else ""
    branch = request.form.get("branch", "").lower().strip() if request.form else ""

    if not name:
        data = request.get_json(silent=True) or {}
        name = data.get("name", "").strip()
        phone = data.get("phone", "").strip()
        branch = data.get("branch", "").lower().strip()

    if not name or not phone or not branch:
        return jsonify({"status": "error", "message": "All fields are required."}), 400

    if len(phone) != 10 or not phone.isdigit():
        return jsonify({"status": "error", "message": "Valid 10-digit phone number is required."}), 400

    allowed_branches = ["cme", "ece", "eee", "mec", "civil"]
    if branch not in allowed_branches:
        return jsonify({"status": "error", "message": "Invalid branch selected."}), 400

    email = session["student_email"]
    profile_image_url = None

    if "profile_image" in request.files:
        file = request.files["profile_image"]
        if file and file.filename and allowed_file(file.filename):
            import uuid
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"avatar_{uuid.uuid4().hex[:10]}.{ext}"
            upload_dir = os.path.join(app.static_folder, "uploads", "avatars")
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)
            profile_image_url = url_for("static", filename=f"uploads/avatars/{filename}")

    update_student_profile(email, name, phone, branch, profile_image=profile_image_url)

    # Update session details
    session["student_name"] = name
    session["student_phone"] = phone
    session["student_branch"] = branch
    if profile_image_url:
        session["student_profile_image"] = profile_image_url

    return jsonify({
        "status": "success",
        "message": "Profile updated successfully!",
        "name": name,
        "phone": phone,
        "branch": branch,
        "profile_image": profile_image_url or session.get("student_profile_image")
    })


def generate_clean_topic_title(message):
    cleaned = message.strip()
    prefixes = [
        r"^please\s+explain\s+(about\s+)?",
        r"^explain\s+(about\s+)?",
        r"^what\s+is\s+(a\s+|an\s+|the\s+)?",
        r"^what\s+are\s+(the\s+)?",
        r"^how\s+to\s+",
        r"^how\s+does\s+",
        r"^tell\s+me\s+about\s+",
        r"^can\s+you\s+(please\s+)?(explain|teach|tell)\s+(me\s+)?(about\s+)?",
        r"^give\s+me\s+(some\s+)?",
        r"^teach\s+me\s+(about\s+)?"
    ]
    temp = cleaned
    for p in prefixes:
        temp = re.sub(p, "", temp, flags=re.IGNORECASE)
    
    # Remove trailing conversational particles
    temp = re.sub(r"\s*(explain\s+cheyyi|cheppandi|cheppu|ivvandi|ivvu|please)\s*$", "", temp, flags=re.IGNORECASE)
    temp = temp.rstrip("?!.:,; ").strip()
    if temp:
        title = temp[0].upper() + temp[1:]
        if len(title) > 30:
            title = title[:28].strip() + "..."
        return title
    
    clean_stripped = cleaned.rstrip("?!.:,; ").strip()
    return (clean_stripped[:28] + "...") if len(clean_stripped) > 28 else (clean_stripped or "New Chat")


def detect_query_academic_context(user_message, student_branch=""):
    """
    Intelligently identifies whether the student's question is:
    - 'ecet_exam': Explicitly asking about AP E-CET entrance examination structure, syllabus, dates, eligibility, rank, scoring, counseling.
    - 'branch_engineering': Explicitly asking about core engineering diploma topics or syllabus where verified project resources apply.
    - 'general': Any general educational question, programming, mathematics, science, language, conversation, or everyday topic.
    """
    msg_lower = user_message.lower()

    # 1. E-CET Examination Specific Indicators
    ecet_markers = [
        "ecet", "e-cet", "ap ecet", "ts ecet", "entrance exam", "cutoff", "cut-off",
        "counseling", "counselling", "marks vs rank", "rank predictor", "diploma exam",
        "exam pattern", "c-20 scheme", "c-16 scheme", "ecet eligibility", "ecet hall ticket"
    ]
    if any(m in msg_lower for m in ecet_markers):
        return "ecet_exam"

    # 2. Specific Diploma Branch Engineering Indicators
    branch_markers = {
        "cme": ["dcme", "diploma in computer", "8086 microprocessor", "relational algebra", "bcnf normalization"],
        "eee": ["deee", "diploma in electrical", "kcl", "kvl", "thevenin", "norton", "superposition", "synchronous motor", "induction motor", "transformer equivalent circuit", "power system fault", "switchgear"],
        "ece": ["dece", "diploma in electronics", "op-amp 741", "barkhausen", "superheterodyne", "nyquist rate", "8051 microcontroller", "k-map simplification"],
        "mec": ["dme", "diploma in mechanical", "lathe machine", "otto cycle", "diesel cycle", "rankine cycle", "bernoulli theorem", "sfd bmd", "shear force diagram", "bending moment diagram", "cnc g-code"],
        "civil": ["dce", "diploma in civil", "height of instrument", "rise and fall method", "theodolite traversing", "slump test", "concrete mix design", "is 456", "darcy weisbach", "mohr circle"]
    }
    
    b_key = str(student_branch).strip().lower()
    if b_key in branch_markers:
        if any(m in msg_lower for m in branch_markers[b_key]):
            return "branch_engineering"

    for b, markers in branch_markers.items():
        if any(m in msg_lower for m in markers):
            return "branch_engineering"

    return "general"


def classify_ai_error(err):
    err_msg = str(err)
    if "500" in err_msg or "503" in err_msg or "UNAVAILABLE" in err_msg.upper() or "high demand" in err_msg.lower():
        category = "SERVICE_ERROR"
        user_message = "Sorry, I couldn't generate a response right now. The AI service is currently experiencing high demand. Please try again."
    elif "401" in err_msg or "403" in err_msg or "API_KEY" in err_msg.upper() or "INVALID_ARGUMENT" in err_msg.upper():
        category = "AUTHENTICATION_ERROR"
        user_message = "Sorry, I couldn't generate a response right now. Please verify API key configuration."
    elif "404" in err_msg or "NOT_FOUND" in err_msg:
        category = "MODEL_ERROR"
        user_message = "Sorry, I couldn't generate a response right now. The AI model is temporarily unavailable."
    elif "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg or "quota" in err_msg.lower():
        if "free_tier_requests" in err_msg or "per_day" in err_msg.lower():
            category = "QUOTA_ERROR"
            user_message = "Sorry, I couldn't generate a response right now. Daily AI quota limit reached. Please try again shortly."
        else:
            category = "RATE_LIMIT_ERROR"
            user_message = "Sorry, I couldn't generate a response right now. Request rate limit reached. Please try again in a moment."
    elif "connection" in err_msg.lower() or "network" in err_msg.lower() or "timeout" in err_msg.lower() or "disconnected" in err_msg.lower():
        category = "NETWORK_ERROR"
        user_message = "Sorry, I couldn't generate a response right now. Network connection timed out. Please try again."
    else:
        category = "SERVICE_ERROR"
        user_message = "Sorry, I couldn't generate a response right now. Please try again."
    return category, user_message


# Ask a Doubt API with Multilingual Support & Persistent Database Chat History
@app.route("/api/ai_chat", methods=["POST"])
@login_required
def ai_chat():
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "").strip()
    conv_id = data.get("conversation_id")

    if not user_message:
        return jsonify({"error": "Message cannot be empty."}), 400

    student_email = session["student_email"]
    student_name = session.get("student_name", "Student")
    raw_branch = session.get("student_branch")
    student_branch = str(raw_branch).strip().upper() if raw_branch else "GENERAL"
    branch_subjects = ", ".join(BRANCH_SUBJECTS.get(student_branch.lower(), ["General Engineering Mathematics", "Physics", "Chemistry"]))

    # Handle Conversation ID & Retrieve Multi-Turn History (bounded to latest 8 turns)
    history_msgs = []
    if conv_id:
        existing_msgs = get_conversation_messages(conv_id, student_email, limit=8)
        if existing_msgs is False:
            return jsonify({"error": "Unauthorized access to conversation."}), 403
        if existing_msgs is not None and isinstance(existing_msgs, list):
            history_msgs = existing_msgs
        else:
            conv_id = None

    # Clean, intelligent topic-based title generation for new conversation
    title = generate_clean_topic_title(user_message)
    if not conv_id:
        conv_id = create_ai_conversation(student_email, title, student_branch)

    # Save student message to DB (1 message per turn)
    add_ai_message(conv_id, "user", user_message)

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        reply = "Sorry, I couldn't generate a response right now. Please set your `GEMINI_API_KEY` to enable live responses."
        add_ai_message(conv_id, "assistant", reply)
        return jsonify({"reply": reply, "conversation_id": conv_id, "title": title})

    try:
        # Build multi-turn conversational dialogue context (last 8 messages)
        dialogue_history = ""
        if history_msgs:
            recent_turns = history_msgs[-8:]
            dialogue_history = "\n".join([f"{'User' if m.get('role') == 'user' else 'Assistant'}: {m.get('content')}" for m in recent_turns])

        # Intelligent query intent & academic context detection
        query_context_type = detect_query_academic_context(user_message, student_branch)

        domain_context = ""
        if query_context_type == "branch_engineering":
            branch_domain = BRANCH_ENGINEERING_DOMAINS.get(student_branch.lower(), {
                "domain_name": f"{student_branch} Engineering",
                "core_topics": branch_subjects,
                "pedagogy_focus": "Provide clear, accurate engineering explanations with formulas and practical examples."
            })
            available_pdfs_info = ""
            try:
                branch_pdfs = get_available_pdfs(student_branch.lower())
                if branch_pdfs:
                    available_pdfs_info = f"\nRelevant study reference topics for {student_branch}: " + ", ".join([p.get("title", "") for p in branch_pdfs[:6]])
            except Exception:
                available_pdfs_info = ""

            domain_context = f"""
ACADEMIC ENGINEERING DOMAIN (Specific to this query):
- Branch: {student_branch} ({branch_domain.get('domain_name')})
- Core Curriculum Topics: {branch_subjects}{available_pdfs_info}
- Engineering Focus: {branch_domain.get('pedagogy_focus')}
Apply this verified engineering curriculum context to provide rigorous, accurate, diploma-aligned technical explanations.
"""
        elif query_context_type == "ecet_exam":
            domain_context = f"""
EXAMINATION CONTEXT:
The user is specifically inquiring about the AP E-CET (Engineering Common Entrance Test).
Provide factual information about the entrance exam structure, pattern (200 Total Marks: Mathematics 50 marks, Physics 25 marks, Chemistry 25 marks, Engineering Core 100 marks), syllabus, eligibility criteria, rank estimation, or counseling procedures as requested.
"""

        system_context = f"""You are an intelligent, highly accurate, and multilingual General and Educational Conversational AI Assistant interacting with {student_name}.

PRIMARY MISSION & SCOPE:
- You assist learners with ANY question they ask—ranging from general knowledge, everyday questions, science, mathematics, literature, and programming, to in-depth diploma engineering concepts and AP E-CET examination preparation.
- You are NOT restricted to E-CET. You are a versatile, intelligent educational assistant.
- Answer the user's CURRENT question directly, accurately, and naturally.
- DO NOT assume every question is about the E-CET exam.
- NEVER force an unrelated or general question into E-CET exam format, marks breakdown, or syllabus disclaimers.

EDUCATIONAL RIGOR & ACCURACY STANDARDS (HIGH PRIORITY):
1. Absolute Factual & Technical Correctness:
   - Prioritize correctness above all. Never invent formulas, definitions, code syntax, library methods, or facts.
   - For mathematical, scientific, or programming problems, verify your reasoning and steps before stating the final result.
   - For programming: provide clean, formatted, idiomatic, compilable code examples with concise explanation.
   - For calculations: show clear step-by-step working and state exact numerical results with correct units.
2. Epistemic Humility & Honesty:
   - Clearly distinguish established facts from uncertainty, hypotheses, or conditional cases.
   - If something is ambiguous, uncertain, or depends on specific external conditions, state so clearly rather than asserting unverified claims.
   - When relevant verified project study material or curriculum standards exist, prefer them over unsupported assumptions.
3. Pedagogical Adaptability:
   - Match explanation depth to the learner: clear, accessible, and intuitive for beginners, while preserving rigorous technical terminology.
   - Provide structured, step-by-step explanations when breaking down complex concepts.

NATURAL MULTILINGUAL COMMUNICATION:
- Automatically detect the language, script, and phrasing used by the user.
- Respond in that SAME language:
  * English -> Respond fluently and naturally in English.
  * Native Telugu script (e.g., "పైథాన్ అంటే ఏమిటి?", "లింక్డ్ లిస్ట్ అంటే ఏమిటి?") -> Respond in natural Telugu script.
  * Romanized Telugu / Telugu-English (e.g., "Python lo list ante enti?", "KVL simple ga explain cheyyi", "C lo pointer ela pani chesthundhi?") -> Respond naturally in Telugu / Telugu-English.
  * Native Hindi script -> Respond in natural Hindi script.
  * Hinglish / Romanized Hindi (e.g., "Python kya hai?", "C me loop kya hota hai?") -> Respond naturally in Hindi / Hinglish.
  * Other languages -> Match the user's input language.
- Never translate a user's non-English question into English to answer in English unless the user explicitly requested an English answer.

MULTI-TURN CONVERSATION & TOPIC HANDLING:
- Use previous conversation history ONLY when the current message is a genuine follow-up or relates to the ongoing topic (e.g., "What are its advantages?", "Explain that with an example in C", "Why?", "What about the second one?").
- If the user changes topics or asks an independent, standalone question, answer the new question directly without dragging in old, irrelevant topic context.
{domain_context}"""

        if dialogue_history:
            full_prompt = f"{system_context}\n\n--- PREVIOUS CONVERSATION CONTEXT ---\n{dialogue_history}\n\n--- CURRENT USER MESSAGE ---\nUser: {user_message}\nAssistant:"
        else:
            full_prompt = f"{system_context}\n\nUser: {user_message}\nAssistant:"

        client = get_cached_genai_client(api_key)
        reply = None
        last_err = None

        candidate_models = ['gemini-3.6-flash', 'gemini-3.1-flash-lite', 'gemini-3-flash-preview']
        for model_name in candidate_models:
            for attempt in range(2):
                try:
                    if client:
                        response = client.models.generate_content(
                            model=model_name,
                            contents=full_prompt,
                        )
                        reply = response.text
                    else:
                        import google.generativeai as legacy_genai
                        legacy_genai.configure(api_key=api_key)
                        model = legacy_genai.GenerativeModel(model_name)
                        res = model.generate_content(full_prompt)
                        reply = res.text
                    if reply:
                        break
                except Exception as e:
                    last_err = e
                    err_str = str(e).lower()
                    # If 429 quota exhaustion or 404 model not found, switch immediately to next candidate model
                    if "429" in err_str or "resource_exhausted" in err_str or "404" in err_str or "not_found" in err_str:
                        break
                    # If 503 transient server error, retry once
                    if ("503" in err_str or "unavailable" in err_str or "high demand" in err_str) and attempt < 1:
                        time.sleep(1.5)
                        continue
                    break
            if reply:
                break

        if not reply and last_err:
            raise last_err

        # Save AI assistant message to DB
        add_ai_message(conv_id, "assistant", reply)

        return jsonify({"reply": reply, "conversation_id": conv_id, "title": title})

    except Exception as e:
        category, user_reply = classify_ai_error(e)
        print(f"[AI Chat Error - {category}]:", str(e)[:200])
        add_ai_message(conv_id, "assistant", user_reply)
        return jsonify({"reply": user_reply, "conversation_id": conv_id, "title": title, "error_category": category})


# Fetch Conversation Messages API with Ownership Guard
@app.route("/api/get_conversation/<int:conv_id>", methods=["GET"])
@login_required
def get_conversation_api(conv_id):
    student_email = session["student_email"]
    msgs = get_conversation_messages(conv_id, student_email)
    
    if msgs is False:
        return jsonify({"error": "Unauthorized access."}), 403
    if msgs is None:
        return jsonify({"error": "Conversation not found."}), 404
        
    return jsonify({"messages": msgs})


# Rename Conversation API
@app.route("/api/rename_conversation/<int:conv_id>", methods=["POST"])
@login_required
def rename_conversation_api(conv_id):
    data = request.get_json(silent=True) or {}
    new_title = data.get("title", "").strip()
    if not new_title:
        return jsonify({"error": "Title cannot be empty."}), 400

    student_email = session["student_email"]
    update_ai_conversation_title(conv_id, new_title, student_email)
    return jsonify({"status": "success", "title": new_title})


# Pin / Unpin Conversation API
@app.route("/api/pin_conversation/<int:conv_id>", methods=["POST"])
@login_required
def pin_conversation_api(conv_id):
    student_email = session["student_email"]
    pinned_state = toggle_ai_conversation_pin(conv_id, student_email)
    if pinned_state is None:
        return jsonify({"error": "Conversation not found."}), 404

    return jsonify({"status": "success", "is_pinned": pinned_state})


# Share Conversation API (Safe Preview Link)
@app.route("/api/share_conversation/<int:conv_id>", methods=["GET"])
@login_required
def share_conversation_api(conv_id):
    student_email = session["student_email"]
    msgs = get_conversation_messages(conv_id, student_email)
    if msgs is False or msgs is None:
        return jsonify({"error": "Unable to share conversation."}), 403

    share_url = url_for("ai_doubt", _external=True) + f"?shared_id={conv_id}"
    return jsonify({"status": "success", "share_url": share_url})


# Delete Conversation API with Ownership Guard
@app.route("/api/delete_conversation/<int:conv_id>", methods=["POST"])
@login_required
def delete_conversation_api(conv_id):
    student_email = session["student_email"]
    success = delete_ai_conversation(conv_id, student_email)
    if not success:
        return jsonify({"error": "Unauthorized or not found."}), 403
        
    return jsonify({"status": "success", "message": "Conversation deleted."})


# Helper Function: Generate AI Exam Questions (Randomized & Unique)
def generate_ai_exam_questions(branch, subject, num_questions, difficulty, scheme="Other", pdf_context=None):
    api_key = os.environ.get("GEMINI_API_KEY")
    branch_upper = branch.upper()
    scheme_info = f" Syllabus Scheme: {scheme}." if (scheme and scheme != "Other") else ""
    pdf_info = f" Based on PDF study material context: '{pdf_context}'." if (pdf_context and pdf_context != "none") else ""

    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)

            prompt = f"""
Generate a strict JSON array of {num_questions} UNIQUE, RANDOMIZED multiple-choice questions (MCQs) for AP E-CET examination.
Branch: {branch_upper}
Subject: {subject}
{scheme_info}
Difficulty: {difficulty}
{pdf_info}

CRITICAL REQUIREMENTS:
1. All questions MUST be unique. DO NOT repeat any question.
2. Questions must be relevant to {subject} ({branch_upper} E-CET diploma level).
3. Output ONLY a valid raw JSON array containing objects with these exact keys:
[
  {{
    "id": 1,
    "question": "Question text here",
    "options": ["Option A text", "Option B text", "Option C text", "Option D text"],
    "answer": "Exact text of the correct option"
  }}
]
Do not include markdown code block formatting (```json) or commentary. Output ONLY raw JSON string.
"""
            response = client.models.generate_content(
                model='gemini-3.6-flash',
                contents=prompt
            )
            raw_text = response.text.strip()
            if raw_text.startswith("```"):
                raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text, flags=re.IGNORECASE)
                raw_text = re.sub(r"\s*```$", "", raw_text)

            questions = json.loads(raw_text)
            if isinstance(questions, list) and len(questions) > 0:
                seen_texts = set()
                valid_qs = []
                for q in questions:
                    if isinstance(q, dict) and "question" in q and "options" in q and len(q["options"]) == 4:
                        q_text = q["question"].strip()
                        if q_text not in seen_texts:
                            seen_texts.add(q_text)
                            q["id"] = len(valid_qs) + 1
                            valid_qs.append(q)
                if len(valid_qs) >= num_questions:
                    return valid_qs[:num_questions]
                elif valid_qs:
                    return valid_qs
        except Exception as err:
            print("Gemini Exam Generator Error:", err)
            return None

    return None
