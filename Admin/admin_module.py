from database.database_module import (
    get_student,
    delete_student,
    update_student,
    get_attendance_records,
    delete_attendance_record,
    get_connection,
    get_student_by_name,
)

def list_all_students():
    """Retrieve and return all student records."""
    conn = get_connection()
    if conn is None:
        print("Could not connect to the database.")
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT * FROM Students"
        cursor.execute(sql)
        students = cursor.fetchall()
        return students
    except Exception as e:
        print(f"Error retrieving students: {e}")
        return []
    finally:
        if conn:
            conn.close()

def admin_delete_student(student_id):
    """Delete a student record via the admin interface."""
    if delete_student(student_id):
        print(f"Student with ID {student_id} deleted successfully.")
    else:
        print(f"Failed to delete student with ID {student_id}.")

def admin_update_student(student_id, name=None, metadata=None):
    """Update a student's record via the admin interface."""
    if update_student(student_id, name, metadata):
        print(f"Student with ID {student_id} updated successfully.")
    else:
        print(f"Failed to update student with ID {student_id}.")

def admin_list_attendance(student_id=None, start_date=None, end_date=None):
    """
    Print attendance records. If student_id is provided, filter by student.
    Use start_date and end_date to filter by timestamp.
    """
    records = get_attendance_records(student_id, start_date, end_date)
    if records:
        for record in records:
            print(record)
    else:
        print("No attendance records found.")

def admin_delete_attendance(attendance_id):
    """Delete an attendance record via the admin interface."""
    if delete_attendance_record(attendance_id):
        print(f"Attendance record {attendance_id} deleted successfully.")
    else:
        print(f"Failed to delete attendance record {attendance_id}.")

if __name__ == "__main__":
    # Simple admin CLI demonstration.
    print("Listing all students:")
    students = list_all_students()
    for student in students:
        print(student)
