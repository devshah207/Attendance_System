
import mysql.connector # type: ignore
from mysql.connector import Error # type: ignore
from urllib.parse import quote_plus

# Database configuration – adjust host, user, and database as needed.
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",  # Use an empty string if no password is set
    "database": "attendance_db"
}

def get_connection():
    """Establish a connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"]
        )
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# =========================
# CRUD for Students Table
# =========================

def create_student(name, metadata=None):
    """
    Insert a new student record into the Students table.
    'metadata' can be a JSON string with additional info if needed.
    """
    conn = get_connection()
    if conn is None:
        return None
    try:
        cursor = conn.cursor()
        sql = "INSERT INTO Students (name, metadata) VALUES (%s, %s)"
        cursor.execute(sql, (name, metadata))
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"Error creating student: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_student(student_id):
    """Retrieve a student's details using their student_id."""
    conn = get_connection()
    if conn is None:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT * FROM Students WHERE student_id = %s"
        cursor.execute(sql, (student_id,))
        return cursor.fetchone()
    except Error as e:
        print(f"Error fetching student: {e}")
        return None
    finally:
        if conn:
            conn.close()

def update_student(student_id, name=None, metadata=None):
    """Update details for a student. Only provided fields are updated."""
    conn = get_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        updates = []
        params = []
        if name:
            updates.append("name = %s")
            params.append(name)
        if metadata:
            updates.append("metadata = %s")
            params.append(metadata)
        if not updates:
            return False  # Nothing to update.
        params.append(student_id)
        sql = "UPDATE Students SET " + ", ".join(updates) + " WHERE student_id = %s"
        cursor.execute(sql, tuple(params))
        conn.commit()
        return cursor.rowcount > 0
    except Error as e:
        print(f"Error updating student: {e}")
        return False
    finally:
        if conn:
            conn.close()

def delete_student(student_id):
    """Delete a student record from the Students table."""
    conn = get_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        sql = "DELETE FROM Students WHERE student_id = %s"
        cursor.execute(sql, (student_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Error as e:
        print(f"Error deleting student: {e}")
        return False
    finally:
        if conn:
            conn.close()

# =========================
# CRUD for Attendance Table
# =========================

def log_attendance_record(student_id, timestamp, status="present"):
    """Insert a new attendance record for a student."""
    conn = get_connection()
    if conn is None:
        return None
    try:
        cursor = conn.cursor()
        sql = "INSERT INTO Attendance (student_id, timestamp, status) VALUES (%s, %s, %s)"
        cursor.execute(sql, (student_id, timestamp, status))
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"Error logging attendance: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_attendance_records(student_id=None, start_date=None, end_date=None):
    """
    Retrieve attendance records.
    If student_id is provided, filter by student.
    Use start_date and end_date to filter by timestamp.
    """
    conn = get_connection()
    if conn is None:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT * FROM Attendance WHERE 1=1"
        params = []
        if student_id:
            sql += " AND student_id = %s"
            params.append(student_id)
        if start_date:
            sql += " AND timestamp >= %s"
            params.append(start_date)
        if end_date:
            sql += " AND timestamp <= %s"
            params.append(end_date)
        cursor.execute(sql, tuple(params))
        return cursor.fetchall()
    except Error as e:
        print(f"Error retrieving attendance records: {e}")
        return None
    finally:
        if conn:
            conn.close()

def update_attendance_record(attendance_id, status):
    """Update the status (e.g., present, absent) for an attendance record."""
    conn = get_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        sql = "UPDATE Attendance SET status = %s WHERE attendance_id = %s"
        cursor.execute(sql, (status, attendance_id))
        conn.commit()
        return cursor.rowcount > 0
    except Error as e:
        print(f"Error updating attendance record: {e}")
        return False
    finally:
        if conn:
            conn.close()

def delete_attendance_record(attendance_id):
    """Delete an attendance record."""
    conn = get_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        sql = "DELETE FROM Attendance WHERE attendance_id = %s"
        cursor.execute(sql, (attendance_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Error as e:
        print(f"Error deleting attendance record: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_student_by_name(name):
    """Retrieve a student's details using their name."""
    conn = get_connection()
    if conn is None:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT * FROM Students WHERE name = %s"
        cursor.execute(sql, (name,))
        return cursor.fetchone()
    except Error as e:
        print(f"Error retrieving student by name: {e}")
        return None
    finally:
        if conn:
            conn.close()

def insert_student_image(student_id, image_url):
    """
    Insert a new image record for a student into the student_images table.
    image_path should be a relative path or URL pointing to the image stored in S3.
    """
    conn = get_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        sql = "INSERT INTO student_images (student_id, image_url) VALUES (%s, %s)"
        cursor.execute(sql, (student_id, image_url))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error inserting student image: {e}")
        return False
    finally:
        if conn:
            conn.close()
