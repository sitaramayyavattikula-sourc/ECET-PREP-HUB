import os
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

# If DATABASE_URL exists, PostgreSQL will be used.
# Otherwise, SQLite will be used locally.

DATABASE_URL = os.environ.get("DATABASE_URL")

DATABASE_NAME = "database/ecet.db"


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():

    # -------------------------
    # PostgreSQL - Render
    # -------------------------
    if DATABASE_URL:

        connection = psycopg2.connect(
            DATABASE_URL
        )

        return connection

    # -------------------------
    # SQLite - Local computer
    # -------------------------
    connection = sqlite3.connect(
        DATABASE_NAME
    )

    connection.row_factory = sqlite3.Row

    return connection


# =========================================================
# CREATE TABLES
# =========================================================

def create_tables():

    connection = get_connection()

    cursor = connection.cursor()

    # =====================================================
    # PostgreSQL
    # =====================================================

    if DATABASE_URL:

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS students(
            id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            name TEXT,
            email TEXT,
            phone TEXT,
            password TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_results(
            id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            student_email TEXT,
            branch TEXT,
            score INTEGER
        )
        """)

    # =====================================================
    # SQLite
    # =====================================================

    else:

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS students(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT,
            password TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_results(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_email TEXT,
            branch TEXT,
            score INTEGER
        )
        """)

    connection.commit()

    cursor.close()
    connection.close()

    print("Database tables created successfully!")


# =========================================================
# ADD STUDENT
# =========================================================

def add_student(name, email, phone, password):

    connection = get_connection()

    cursor = connection.cursor()

    if DATABASE_URL:

        cursor.execute(
            """
            INSERT INTO students
            (name, email, phone, password)
            VALUES (%s, %s, %s, %s)
            """,
            (name, email, phone, password)
        )

    else:

        cursor.execute(
            """
            INSERT INTO students
            (name, email, phone, password)
            VALUES (?, ?, ?, ?)
            """,
            (name, email, phone, password)
        )

    connection.commit()

    cursor.close()
    connection.close()


# =========================================================
# GET STUDENT BY EMAIL
# =========================================================

def get_student_by_email(email):

    connection = get_connection()

    if DATABASE_URL:

        cursor = connection.cursor(
            cursor_factory=RealDictCursor
        )

        cursor.execute(
            """
            SELECT *
            FROM students
            WHERE LOWER(email) =LOWER(%s)
            """,
            (email,)
        )

    else:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM students
            WHERE email = ?
            """,
            (email,)
        )

    student = cursor.fetchone()

    cursor.close()
    connection.close()

    return student


# =========================================================
# GET STUDENT BY PHONE
# =========================================================

def get_student_by_phone(phone):

    connection = get_connection()

    if DATABASE_URL:

        cursor = connection.cursor(
            cursor_factory=RealDictCursor
        )

        cursor.execute(
            """
            SELECT *
            FROM students
            WHERE phone = %s
            """,
            (phone,)
        )

    else:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM students
            WHERE phone = ?
            """,
            (phone,)
        )

    student = cursor.fetchone()

    cursor.close()
    connection.close()

    return student


# =========================================================
# SAVE QUIZ RESULT
# =========================================================

def save_quiz_result(email, branch, score):

    connection = get_connection()

    cursor = connection.cursor()

    if DATABASE_URL:

        cursor.execute(
            """
            INSERT INTO quiz_results
            (student_email, branch, score)
            VALUES (%s, %s, %s)
            """,
            (email, branch, score)
        )

    else:

        cursor.execute(
            """
            INSERT INTO quiz_results
            (student_email, branch, score)
            VALUES (?, ?, ?)
            """,
            (email, branch, score)
        )

    connection.commit()

    cursor.close()
    connection.close()


# =========================================================
# GET LEADERBOARD
# =========================================================

def get_leaderboard():

    connection = get_connection()

    if DATABASE_URL:

        cursor = connection.cursor(
            cursor_factory=RealDictCursor
        )

    else:

        cursor = connection.cursor()

    cursor.execute(
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
    )

    students = cursor.fetchall()

    if not DATABASE_URL:
        students = [
            dict(row)
            for row in students
        ]

    print(students)

    cursor.close()
    connection.close()

    return students


# =========================================================
# GET STUDENT RANK
# =========================================================

def get_student_rank(email):

    connection = get_connection()

    if DATABASE_URL:

        cursor = connection.cursor(
            cursor_factory=RealDictCursor
        )

    else:

        cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            student_email,
            MAX(score) AS best_score
        FROM quiz_results
        GROUP BY student_email
        ORDER BY best_score DESC
        """
    )

    students = cursor.fetchall()

    cursor.close()
    connection.close()

    rank = 1

    for student in students:

        if student["student_email"] == email:
            return rank

        rank += 1

    return None