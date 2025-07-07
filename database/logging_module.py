import datetime
from database.database_module import get_student_by_name, log_attendance_record, get_attendance_records

def log_attendance(name, duplicate_threshold=3600):
    """
    Log attendance by inserting a new record into the MySQL Attendance table.
    This function:
      - Retrieves the student record using the student's name.
      - Checks if an attendance record exists within the last 'duplicate_threshold' seconds.
      - Inserts a new attendance record with the current timestamp and status "present"
        only if no recent record is found.
    """
    now = datetime.datetime.now()

    # Retrieve the student's record from the database
    student = get_student_by_name(name)
    if student is None:
        print(f"Student '{name}' not found in the database.")
        return

    student_id = student.get("student_id")
    if student_id is None:
        print(f"Student ID for '{name}' not found.")
        return

    # Check for duplicate attendance entries within duplicate_threshold seconds
    start_time = now - datetime.timedelta(seconds=duplicate_threshold)
    recent_records = get_attendance_records(student_id=student_id, start_date=start_time, end_date=now)
    if recent_records and len(recent_records) > 0:
        print(f"Attendance for '{name}' was already logged within the last {duplicate_threshold} seconds.")
        return

    # Log the attendance record into the Attendance table
    record_id = log_attendance_record(student_id, now, status="present")
    if record_id:
        print(f"Logged attendance for '{name}' at {now} (Record ID: {record_id}).")
    else:
        print(f"Failed to log attendance for '{name}'.")
