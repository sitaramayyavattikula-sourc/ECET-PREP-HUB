import sqlite3


DATABASE_NAME = "database/ecet.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def create_tables():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    phone TEXT,
    password TEXT
)
    """)
        # Quiz Results table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quiz_results(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_email TEXT,
        branch TEXT,
        score INTEGER
    )
    """)

    connection.commit()
    connection.close()
    print("Students table created successfully!")
# Insert student data
# Insert student data
def add_student(name, email, phone, password):

    connection = get_connection()

    connection.execute(
        "INSERT INTO students(name,email,phone,password) VALUES(?,?,?,?)",
        (name, email, phone, password)
    )

    connection.commit()
    connection.close()




    
def get_student_by_email(email):

    connection = get_connection()

    student = connection.execute(
        "SELECT * FROM students WHERE email = ?",
        (email,)
    ).fetchone()

    connection.close()

    return student
def get_student_by_phone(phone):

    connection = get_connection()

    student = connection.execute(
        "SELECT * FROM students WHERE phone = ?",
        (phone,)
    ).fetchone()

    connection.close()

    return student
# ===========================
# Save Quiz Result
# ===========================
def save_quiz_result(email, branch, score):

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO quiz_results
        (student_email, branch, score)
        VALUES(?,?,?)
        """,
        (email, branch, score)
    )

    connection.commit()
    connection.close()
    # ===========================
# Get Leaderboard
# ===========================
def get_leaderboard():

    connection = get_connection()

    students = connection.execute(
        """
        SELECT
            students.name AS name,
            MAX(quiz_results.score) AS best_score
        FROM quiz_results
        INNER JOIN students
        ON students.email = quiz_results.student_email
        GROUP BY students.name
        ORDER BY best_score DESC
        """
    ).fetchall()

    print([dict(row) for row in students])

    connection.close()

    return students
def get_student_rank(email):

    connection = get_connection()

    students = connection.execute(
        """
        SELECT student_email,
               MAX(score) AS best_score
        FROM quiz_results
        GROUP BY student_email
        ORDER BY best_score DESC
        """
    ).fetchall()

    connection.close()

    rank = 1

    for student in students:
        if student["student_email"] == email:
            return rank

        rank += 1

    return None