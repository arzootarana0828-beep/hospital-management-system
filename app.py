from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")


def get_connection():
    connection = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    return connection

@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT *
            FROM users
            WHERE username = %s
            AND password = %s
        """

        cursor.execute(query, (username, password))

        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if user:
            session["user"] = user["username"]
            return redirect(url_for("dashboard"))

        return "Invalid username or password"

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect(url_for("login"))

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM patients")
    patients = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM doctors")
    doctors = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM appointments")
    appointments = cursor.fetchone()["total"]

    cursor.close()
    connection.close()

    return render_template(
        "dashboard.html",
        patients=patients,
        doctors=doctors,
        appointments=appointments
    )

@app.route("/patients")
def patients():

    if "user" not in session:
        return redirect(url_for("login"))

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    search = request.args.get("search", "").strip()

    if search:

        query = """
            SELECT *
            FROM patients
            WHERE patient_name LIKE %s
               OR phone LIKE %s
               OR disease LIKE %s
        """

        value = "%" + search + "%"

        cursor.execute(query, (value, value, value))

    else:

        cursor.execute("SELECT * FROM patients")

    patients = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "patients.html",
        patients=patients,
        search=search
    )

@app.route("/add_patient", methods=["GET", "POST"])
def add_patient():

    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        patient_name = request.form["patient_name"]
        age = request.form["age"]
        gender = request.form["gender"]
        phone = request.form["phone"]
        disease = request.form["disease"]

        connection = get_connection()
        cursor = connection.cursor()

        query = """
            INSERT INTO patients
            (patient_name, age, gender, phone, disease)
            VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(
            query,
            (patient_name, age, gender, phone, disease)
        )

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for("patients"))

    return render_template("add_patient.html")
@app.route("/edit_patient/<int:patient_id>", methods=["GET", "POST"])
def edit_patient(patient_id):

    if "user" not in session:
        return redirect(url_for("login"))

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":

        patient_name = request.form["patient_name"]
        age = request.form["age"]
        gender = request.form["gender"]
        phone = request.form["phone"]
        disease = request.form["disease"]

        query = """
            UPDATE patients
            SET patient_name = %s,
                age = %s,
                gender = %s,
                phone = %s,
                disease = %s
            WHERE patient_id = %s
        """

        cursor.execute(
            query,
            (patient_name, age, gender, phone, disease, patient_id)
        )

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for("patients"))

    cursor.execute(
        "SELECT * FROM patients WHERE patient_id = %s",
        (patient_id,)
    )

    patient = cursor.fetchone()

    cursor.close()
    connection.close()

    if not patient:
        return "Patient not found"

    return render_template(
        "edit_patient.html",
        patient=patient
    )

@app.route("/delete_patient/<int:patient_id>")
def delete_patient(patient_id):

    if "user" not in session:
        return redirect(url_for("login"))

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM patients WHERE patient_id = %s",
        (patient_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for("patients"))

@app.route("/doctors")
def doctors():

    if "user" not in session:
        return redirect(url_for("login"))

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    search = request.args.get("search", "").strip()

    if search:

        query = """
            SELECT *
            FROM doctors
            WHERE doctor_name LIKE %s
               OR specialization LIKE %s
               OR phone LIKE %s
        """

        value = "%" + search + "%"

        cursor.execute(query, (value, value, value))

    else:

        cursor.execute("SELECT * FROM doctors")

    doctors = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "doctors.html",
        doctors=doctors,
        search=search
    )

@app.route("/add_doctor", methods=["GET", "POST"])
def add_doctor():

    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        doctor_name = request.form["doctor_name"]
        specialization = request.form["specialization"]
        phone = request.form["phone"]
        email = request.form["email"]

        connection = get_connection()
        cursor = connection.cursor()

        query = """
            INSERT INTO doctors
            (doctor_name, specialization, phone, email)
            VALUES (%s, %s, %s, %s)
        """

        cursor.execute(
            query,
            (doctor_name, specialization, phone, email)
        )

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for("doctors"))

    return render_template("add_doctor.html")

@app.route("/edit_doctor/<int:doctor_id>", methods=["GET", "POST"])
def edit_doctor(doctor_id):

    if "user" not in session:
        return redirect(url_for("login"))

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":

        doctor_name = request.form["doctor_name"]
        specialization = request.form["specialization"]
        phone = request.form["phone"]
        email = request.form["email"]

        query = """
            UPDATE doctors
            SET doctor_name = %s,
                specialization = %s,
                phone = %s,
                email = %s
            WHERE doctor_id = %s
        """

        cursor.execute(
            query,
            (
                doctor_name,
                specialization,
                phone,
                email,
                doctor_id
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for("doctors"))

    cursor.execute(
        "SELECT * FROM doctors WHERE doctor_id = %s",
        (doctor_id,)
    )

    doctor = cursor.fetchone()

    cursor.close()
    connection.close()

    if not doctor:
        return "Doctor not found"

    return render_template(
        "edit_doctor.html",
        doctor=doctor
    )

@app.route("/delete_doctor/<int:doctor_id>")
def delete_doctor(doctor_id):

    if "user" not in session:
        return redirect(url_for("login"))

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM doctors WHERE doctor_id = %s",
        (doctor_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for("doctors"))

@app.route("/appointments")
def appointments():

    if "user" not in session:
        return redirect(url_for("login"))

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    search = request.args.get("search", "").strip()

    query = """
        SELECT
            a.appointment_id,
            p.patient_name,
            d.doctor_name,
            a.appointment_date,
            a.appointment_time,
            a.reason
        FROM appointments a
        JOIN patients p
            ON a.patient_id = p.patient_id
        JOIN doctors d
            ON a.doctor_id = d.doctor_id
    """

    if search:

        query += """
            WHERE p.patient_name LIKE %s
               OR d.doctor_name LIKE %s
               OR a.reason LIKE %s
        """

        value = "%" + search + "%"

        cursor.execute(
            query,
            (value, value, value)
        )

    else:

        cursor.execute(query)

    appointments = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "appointments.html",
        appointments=appointments,
        search=search
    )

@app.route("/add_appointment", methods=["GET", "POST"])
def add_appointment():

    if "user" not in session:
        return redirect(url_for("login"))

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":

        patient_id = request.form["patient_id"]
        doctor_id = request.form["doctor_id"]
        appointment_date = request.form["appointment_date"]
        appointment_time = request.form["appointment_time"]
        reason = request.form["reason"]

        query = """
            INSERT INTO appointments
            (patient_id, doctor_id, appointment_date, appointment_time, reason)
            VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(
            query,
            (
                patient_id,
                doctor_id,
                appointment_date,
                appointment_time,
                reason
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for("appointments"))

    cursor.execute("SELECT * FROM patients")
    patients = cursor.fetchall()

    cursor.execute("SELECT * FROM doctors")
    doctors = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "add_appointment.html",
        patients=patients,
        doctors=doctors
    )

@app.route("/edit_appointment/<int:appointment_id>", methods=["GET", "POST"])
def edit_appointment(appointment_id):

    if "user" not in session:
        return redirect(url_for("login"))

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":

        patient_id = request.form["patient_id"]
        doctor_id = request.form["doctor_id"]
        appointment_date = request.form["appointment_date"]
        appointment_time = request.form["appointment_time"]
        reason = request.form["reason"]

        query = """
            UPDATE appointments
            SET patient_id = %s,
                doctor_id = %s,
                appointment_date = %s,
                appointment_time = %s,
                reason = %s
            WHERE appointment_id = %s
        """

        cursor.execute(
            query,
            (
                patient_id,
                doctor_id,
                appointment_date,
                appointment_time,
                reason,
                appointment_id
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for("appointments"))

    cursor.execute(
        "SELECT * FROM appointments WHERE appointment_id = %s",
        (appointment_id,)
    )

    appointment = cursor.fetchone()

    if not appointment:

        cursor.close()
        connection.close()

        return "Appointment not found"

    cursor.execute("SELECT * FROM patients")
    patients = cursor.fetchall()

    cursor.execute("SELECT * FROM doctors")
    doctors = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "edit_appointment.html",
        appointment=appointment,
        patients=patients,
        doctors=doctors
    )

@app.route("/delete_appointment/<int:appointment_id>")
def delete_appointment(appointment_id):

    if "user" not in session:
        return redirect(url_for("login"))

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM appointments WHERE appointment_id = %s",
        (appointment_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for("appointments"))


@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)