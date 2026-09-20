import os
import sqlite3

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    psycopg2 = None
    RealDictCursor = None


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

# If DATABASE_URL exists, PostgreSQL will be used.
# Otherwise, SQLite will be used locally.

DATABASE_URL = os.environ.get("DATABASE_URL")

DATABASE_NAME = os.environ.get("SQLITE_DB_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "ecet.db"))


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

    if DATABASE_URL:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS students(
            id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            name TEXT,
            email TEXT,
            phone TEXT,
            password TEXT,
            branch TEXT DEFAULT 'cme',
            profile_image TEXT
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

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_conversations(
            id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            student_email TEXT NOT NULL,
            title TEXT NOT NULL,
            branch TEXT NOT NULL,
            is_pinned INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_messages(
            id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            conversation_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_exam_history(
            id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            student_email TEXT NOT NULL,
            branch TEXT NOT NULL,
            subject TEXT NOT NULL,
            scheme TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            time_taken TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS contact_messages(
            id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            status TEXT NOT NULL DEFAULT 'New'
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_exam_solutions(
            id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            question_hash TEXT UNIQUE NOT NULL,
            explanation TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # PostgreSQL column check & migration
        try:
            cursor.execute("ALTER TABLE students ADD COLUMN IF NOT EXISTS branch TEXT DEFAULT 'cme'")
            cursor.execute("ALTER TABLE students ADD COLUMN IF NOT EXISTS profile_image TEXT")
            cursor.execute("ALTER TABLE ai_conversations ADD COLUMN IF NOT EXISTS is_pinned INTEGER DEFAULT 0")
        except Exception as e:
            print("PostgreSQL migration note:", e)

    else:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS students(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT,
            password TEXT,
            branch TEXT DEFAULT 'cme'
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

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_conversations(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_email TEXT NOT NULL,
            title TEXT NOT NULL,
            branch TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_messages(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_exam_history(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_email TEXT NOT NULL,
            branch TEXT NOT NULL,
            subject TEXT NOT NULL,
            scheme TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            time_taken TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS contact_messages(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at DATETIME NOT NULL,
            status TEXT NOT NULL DEFAULT 'New'
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_exam_solutions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_hash TEXT UNIQUE NOT NULL,
            explanation TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # SQLite column check & migration
        try:
            cursor.execute("PRAGMA table_info(students)")
            columns = [row[1] for row in cursor.fetchall()]
            if "branch" not in columns:
                cursor.execute("ALTER TABLE students ADD COLUMN branch TEXT DEFAULT 'cme'")
            if "profile_image" not in columns:
                cursor.execute("ALTER TABLE students ADD COLUMN profile_image TEXT")

            cursor.execute("PRAGMA table_info(ai_conversations)")
            conv_cols = [row[1] for row in cursor.fetchall()]
            if conv_cols and "is_pinned" not in conv_cols:
                cursor.execute("ALTER TABLE ai_conversations ADD COLUMN is_pinned INTEGER DEFAULT 0")
        except Exception as e:
            print("SQLite migration note:", e)

    connection.commit()
    cursor.close()
    connection.close()

    print("Database tables created successfully!")


# =========================================================
# ADD STUDENT
# =========================================================

def add_student(name, email, phone, password, branch="cme"):

    connection = get_connection()
    cursor = connection.cursor()

    if DATABASE_URL:
        cursor.execute(
            """
            INSERT INTO students
            (name, email, phone, password, branch)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (name, email, phone, password, branch)
        )
    else:
        cursor.execute(
            """
            INSERT INTO students
            (name, email, phone, password, branch)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, email, phone, password, branch)
        )

    connection.commit()
    cursor.close()
    connection.close()


# =========================================================
# UPDATE STUDENT BRANCH
# =========================================================

def update_student_branch(email, branch):

    connection = get_connection()
    cursor = connection.cursor()

    if DATABASE_URL:
        cursor.execute(
            """
            UPDATE students
            SET branch = %s
            WHERE LOWER(email) = LOWER(%s)
            """,
            (branch, email)
        )
    else:
        cursor.execute(
            """
            UPDATE students
            SET branch = ?
            WHERE LOWER(email) = LOWER(?)
            """,
            (branch, email)
        )

    connection.commit()
    cursor.close()
    connection.close()


# =========================================================
# UPDATE STUDENT PASSWORD (For upgrading legacy plain passwords)
# =========================================================

def update_student_password(email, hashed_password):

    connection = get_connection()
    cursor = connection.cursor()

    if DATABASE_URL:
        cursor.execute(
            """
            UPDATE students
            SET password = %s
            WHERE LOWER(email) = LOWER(%s)
            """,
            (hashed_password, email)
        )
    else:
        cursor.execute(
            """
            UPDATE students
            SET password = ?
            WHERE LOWER(email) = LOWER(?)
            """,
            (hashed_password, email)
        )

    connection.commit()
    cursor.close()
    connection.close()


# =========================================================
# UPDATE STUDENT PROFILE
# =========================================================

def update_student_profile(email, name, phone, branch, profile_image=None):

    connection = get_connection()
    cursor = connection.cursor()

    if profile_image is not None:
        if DATABASE_URL:
            cursor.execute(
                """
                UPDATE students
                SET name = %s, phone = %s, branch = %s, profile_image = %s
                WHERE LOWER(email) = LOWER(%s)
                """,
                (name, phone, branch, profile_image, email)
            )
        else:
            cursor.execute(
                """
                UPDATE students
                SET name = ?, phone = ?, branch = ?, profile_image = ?
                WHERE LOWER(email) = LOWER(?)
                """,
                (name, phone, branch, profile_image, email)
            )
    else:
        if DATABASE_URL:
            cursor.execute(
                """
                UPDATE students
                SET name = %s, phone = %s, branch = %s
                WHERE LOWER(email) = LOWER(%s)
                """,
                (name, phone, branch, email)
            )
        else:
            cursor.execute(
                """
                UPDATE students
                SET name = ?, phone = ?, branch = ?
                WHERE LOWER(email) = LOWER(?)
                """,
                (name, phone, branch, email)
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

# =========================================================
# PERSISTENT AI CONVERSATIONS & MESSAGES HELPERS
# =========================================================

def create_ai_conversation(student_email, title, branch):
    connection = get_connection()
    cursor = connection.cursor()
    
    if DATABASE_URL:
        cursor.execute(
            "INSERT INTO ai_conversations (student_email, title, branch) VALUES (%s, %s, %s) RETURNING id",
            (student_email, title, branch)
        )
        conv_id = cursor.fetchone()[0]
    else:
        cursor.execute(
            "INSERT INTO ai_conversations (student_email, title, branch) VALUES (?, ?, ?)",
            (student_email, title, branch)
        )
        conv_id = cursor.lastrowid
        
    connection.commit()
    cursor.close()
    connection.close()
    return conv_id


def get_student_conversations(student_email):
    connection = get_connection()
    if DATABASE_URL:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM ai_conversations WHERE student_email = %s ORDER BY is_pinned DESC, updated_at DESC", (student_email,))
    else:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM ai_conversations WHERE student_email = ? ORDER BY is_pinned DESC, updated_at DESC", (student_email,))

    rows = cursor.fetchall()
    if not DATABASE_URL:
        rows = [dict(r) for r in rows]
        
    cursor.close()
    connection.close()
    return rows


def get_conversation_messages(conversation_id, student_email, limit=None):
    connection = get_connection()
    if DATABASE_URL:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT student_email FROM ai_conversations WHERE id = %s", (conversation_id,))
    else:
        cursor = connection.cursor()
        cursor.execute("SELECT student_email FROM ai_conversations WHERE id = ?", (conversation_id,))

    row = cursor.fetchone()
    if not row:
        cursor.close()
        connection.close()
        return None  # Not found

    owner_email = row["student_email"] if isinstance(row, dict) else row[0]
    if owner_email != student_email:
        cursor.close()
        connection.close()
        return False  # Unauthorized access

    if limit and isinstance(limit, int) and limit > 0:
        if DATABASE_URL:
            cursor.execute("""
                SELECT role, content, created_at FROM (
                    SELECT id, role, content, created_at FROM ai_messages WHERE conversation_id = %s ORDER BY id DESC LIMIT %s
                ) sub ORDER BY id ASC
            """, (conversation_id, limit))
        else:
            cursor.execute("""
                SELECT role, content, created_at FROM (
                    SELECT id, role, content, created_at FROM ai_messages WHERE conversation_id = ? ORDER BY id DESC LIMIT ?
                ) ORDER BY id ASC
            """, (conversation_id, limit))
    else:
        if DATABASE_URL:
            cursor.execute("SELECT role, content, created_at FROM ai_messages WHERE conversation_id = %s ORDER BY id ASC", (conversation_id,))
        else:
            cursor.execute("SELECT role, content, created_at FROM ai_messages WHERE conversation_id = ? ORDER BY id ASC", (conversation_id,))
        
    msgs = cursor.fetchall()
    if not DATABASE_URL:
        msgs = [dict(m) for m in msgs]

    cursor.close()
    connection.close()
    return msgs


def add_ai_message(conversation_id, role, content):
    connection = get_connection()
    cursor = connection.cursor()
    
    if DATABASE_URL:
        cursor.execute("INSERT INTO ai_messages (conversation_id, role, content) VALUES (%s, %s, %s)", (conversation_id, role, content))
        cursor.execute("UPDATE ai_conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = %s", (conversation_id,))
    else:
        cursor.execute("INSERT INTO ai_messages (conversation_id, role, content) VALUES (?, ?, ?)", (conversation_id, role, content))
        cursor.execute("UPDATE ai_conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (conversation_id,))
        
    connection.commit()
    cursor.close()
    connection.close()


def delete_ai_conversation(conversation_id, student_email):
    connection = get_connection()
    cursor = connection.cursor()
    
    if DATABASE_URL:
        cursor.execute("SELECT student_email FROM ai_conversations WHERE id = %s", (conversation_id,))
    else:
        cursor.execute("SELECT student_email FROM ai_conversations WHERE id = ?", (conversation_id,))
        
    row = cursor.fetchone()
    if not row:
        cursor.close()
        connection.close()
        return False

    owner = row["student_email"] if isinstance(row, dict) else row[0]
    if owner != student_email:
        cursor.close()
        connection.close()
        return False

    if DATABASE_URL:
        cursor.execute("DELETE FROM ai_messages WHERE conversation_id = %s", (conversation_id,))
        cursor.execute("DELETE FROM ai_conversations WHERE id = %s", (conversation_id,))
    else:
        cursor.execute("DELETE FROM ai_messages WHERE conversation_id = ?", (conversation_id,))
        cursor.execute("DELETE FROM ai_conversations WHERE id = ?", (conversation_id,))

    connection.commit()
    cursor.close()
    connection.close()
    return True


def update_ai_conversation_title(conv_id, title, student_email):
    connection = get_connection()
    cursor = connection.cursor()
    if DATABASE_URL:
        cursor.execute(
            "UPDATE ai_conversations SET title = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s AND student_email = %s",
            (title, conv_id, student_email)
        )
    else:
        cursor.execute(
            "UPDATE ai_conversations SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND student_email = ?",
            (title, conv_id, student_email)
        )
    connection.commit()
    cursor.close()
    connection.close()


def toggle_ai_conversation_pin(conv_id, student_email):
    connection = get_connection()
    cursor = connection.cursor()
    if DATABASE_URL:
        cursor.execute("SELECT is_pinned FROM ai_conversations WHERE id = %s AND student_email = %s", (conv_id, student_email))
    else:
        cursor.execute("SELECT is_pinned FROM ai_conversations WHERE id = ? AND student_email = ?", (conv_id, student_email))
        
    row = cursor.fetchone()
    if not row:
        cursor.close()
        connection.close()
        return None

    current_pinned = row[0] if not DATABASE_URL else row["is_pinned"]
    new_pinned = 0 if current_pinned else 1

    if DATABASE_URL:
        cursor.execute("UPDATE ai_conversations SET is_pinned = %s WHERE id = %s AND student_email = %s", (new_pinned, conv_id, student_email))
    else:
        cursor.execute("UPDATE ai_conversations SET is_pinned = ? WHERE id = ? AND student_email = ?", (new_pinned, conv_id, student_email))

    connection.commit()
    cursor.close()
    connection.close()
    return new_pinned


def save_ai_exam_history(student_email, branch, subject, scheme, difficulty, score, total, time_taken):
    connection = get_connection()
    cursor = connection.cursor()
    if DATABASE_URL:
        cursor.execute(
            "INSERT INTO ai_exam_history (student_email, branch, subject, scheme, difficulty, score, total, time_taken) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (student_email, branch, subject, scheme, difficulty, score, total, time_taken)
        )
    else:
        cursor.execute(
            "INSERT INTO ai_exam_history (student_email, branch, subject, scheme, difficulty, score, total, time_taken) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (student_email, branch, subject, scheme, difficulty, score, total, time_taken)
        )
    connection.commit()
    cursor.close()
    connection.close()


def get_cached_solution(question_hash):
    connection = get_connection()
    cursor = connection.cursor()
    if DATABASE_URL:
        cursor.execute("SELECT explanation FROM ai_exam_solutions WHERE question_hash = %s", (question_hash,))
    else:
        cursor.execute("SELECT explanation FROM ai_exam_solutions WHERE question_hash = ?", (question_hash,))
    row = cursor.fetchone()
    cursor.close()
    connection.close()
    if row:
        return row[0] if not DATABASE_URL else row["explanation"]
    return None


def save_cached_solution(question_hash, explanation):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        if DATABASE_URL:
            cursor.execute(
                "INSERT INTO ai_exam_solutions (question_hash, explanation) VALUES (%s, %s) ON CONFLICT (question_hash) DO UPDATE SET explanation = EXCLUDED.explanation",
                (question_hash, explanation)
            )
        else:
            cursor.execute(
                "INSERT OR REPLACE INTO ai_exam_solutions (question_hash, explanation) VALUES (?, ?)",
                (question_hash, explanation)
            )
        connection.commit()
    except Exception as e:
        print("Error saving cached solution:", e)
    finally:
        cursor.close()
        connection.close()



# =========================================================
# CONTACT MESSAGES HELPER FUNCTIONS
# =========================================================

def add_contact_message(name, email, subject, message, created_at=None, status="New"):
    """
    Inserts a validated contact message into the contact_messages table.
    Uses parameterized SQL queries to protect against SQL injection.
    Commits transaction and returns (True, new_id).
    On failure, rolls back transaction and raises exception.
    """
    from datetime import datetime
    if not created_at:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    name = str(name).strip()
    email = str(email).strip()
    subject = str(subject).strip()
    message = str(message).strip()

    connection = get_connection()
    cursor = connection.cursor()
    try:
        if DATABASE_URL:
            cursor.execute(
                """
                INSERT INTO contact_messages (name, email, subject, message, created_at, status)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (name, email, subject, message, created_at, status)
            )
            new_id = cursor.fetchone()[0]
        else:
            cursor.execute(
                """
                INSERT INTO contact_messages (name, email, subject, message, created_at, status)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (name, email, subject, message, created_at, status)
            )
            new_id = cursor.lastrowid

        connection.commit()
        return True, new_id
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        cursor.close()
        connection.close()


def get_contact_messages(status_filter=None, search_query=None, limit=None, offset=None):
    """
    Retrieves contact messages sorted by newest first (created_at DESC, id DESC).
    Supports status filtering and search by name, email, or subject.
    """
    connection = get_connection()
    params = []
    where_clauses = []

    if status_filter and status_filter.strip() and status_filter.lower() != "all":
        if DATABASE_URL:
            where_clauses.append("LOWER(status) = LOWER(%s)")
        else:
            where_clauses.append("LOWER(status) = LOWER(?)")
        params.append(status_filter.strip())

    if search_query and search_query.strip():
        search_pattern = f"%{search_query.strip()}%"
        if DATABASE_URL:
            where_clauses.append("(name ILIKE %s OR email ILIKE %s OR subject ILIKE %s)")
            params.extend([search_pattern, search_pattern, search_pattern])
        else:
            where_clauses.append("(name LIKE ? OR email LIKE ? OR subject LIKE ?)")
            params.extend([search_pattern, search_pattern, search_pattern])

    where_sql = ""
    if where_clauses:
        where_sql = "WHERE " + " AND ".join(where_clauses)

    order_sql = "ORDER BY created_at DESC, id DESC"

    pagination_sql = ""
    if limit is not None:
        pagination_sql = f"LIMIT {int(limit)}"
        if offset is not None:
            pagination_sql += f" OFFSET {int(offset)}"

    query = f"SELECT id, name, email, subject, message, created_at, status FROM contact_messages {where_sql} {order_sql} {pagination_sql}"

    if DATABASE_URL:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
    else:
        cursor = connection.cursor()
        cursor.execute(query, tuple(params))
        rows = [dict(r) for r in cursor.fetchall()]

    cursor.close()
    connection.close()
    return rows


def get_contact_message_by_id(msg_id):
    """
    Fetches a single contact message by its primary key ID.
    """
    connection = get_connection()
    if DATABASE_URL:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT id, name, email, subject, message, created_at, status FROM contact_messages WHERE id = %s", (msg_id,))
        row = cursor.fetchone()
    else:
        cursor = connection.cursor()
        cursor.execute("SELECT id, name, email, subject, message, created_at, status FROM contact_messages WHERE id = ?", (msg_id,))
        row = cursor.fetchone()
        if row:
            row = dict(row)

    cursor.close()
    connection.close()
    return row


def update_contact_message_status(msg_id, status):
    """
    Updates the status of a contact message ('New', 'Read', 'Replied').
    """
    valid_statuses = ["New", "Read", "Replied"]
    matched = [s for s in valid_statuses if s.lower() == str(status).strip().lower()]
    clean_status = matched[0] if matched else str(status).strip()

    connection = get_connection()
    cursor = connection.cursor()
    try:
        if DATABASE_URL:
            cursor.execute("UPDATE contact_messages SET status = %s WHERE id = %s", (clean_status, msg_id))
        else:
            cursor.execute("UPDATE contact_messages SET status = ? WHERE id = ?", (clean_status, msg_id))
        connection.commit()
        return True
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        cursor.close()
        connection.close()


def delete_contact_message(msg_id):
    """
    Deletes a contact message by ID after authorization.
    """
    connection = get_connection()
    cursor = connection.cursor()
    try:
        if DATABASE_URL:
            cursor.execute("DELETE FROM contact_messages WHERE id = %s", (msg_id,))
        else:
            cursor.execute("DELETE FROM contact_messages WHERE id = ?", (msg_id,))
        connection.commit()
        return True
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        cursor.close()
        connection.close()


def get_contact_message_stats():
    """
    Returns counts for total, New, Read, Replied messages dynamically from database.
    """
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN LOWER(status) = 'new' THEN 1 ELSE 0 END) as new_count,
                SUM(CASE WHEN LOWER(status) = 'read' THEN 1 ELSE 0 END) as read_count,
                SUM(CASE WHEN LOWER(status) = 'replied' THEN 1 ELSE 0 END) as replied_count
            FROM contact_messages
        """)
        row = cursor.fetchone()
        if row:
            if isinstance(row, dict):
                total = row.get("total", 0) or 0
                new_c = row.get("new_count", 0) or 0
                read_c = row.get("read_count", 0) or 0
                replied_c = row.get("replied_count", 0) or 0
            else:
                total = row[0] or 0
                new_c = row[1] or 0
                read_c = row[2] or 0
                replied_c = row[3] or 0
            return {
                "total": int(total),
                "new": int(new_c),
                "read": int(read_c),
                "replied": int(replied_c)
            }
        return {"total": 0, "new": 0, "read": 0, "replied": 0}
    finally:
        cursor.close()
        connection.close()
