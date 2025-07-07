from database_module import get_connection

def create_tables():
    conn = get_connection()
    if conn is None:
        print("Failed to connect to MySQL.")
        return

    try:
        cursor = conn.cursor()
        # Create Students table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Students (
                student_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                metadata TEXT
            )
        ''')
        # Create Attendance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Attendance (
                attendance_id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT,
                timestamp DATETIME NOT NULL,
                status VARCHAR(50) DEFAULT 'present',
                FOREIGN KEY (student_id) REFERENCES Students(student_id)
            )
        ''')
        # Create student_images table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS student_images (
                image_id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT,
                image_url VARCHAR(255) NOT NULL,
                FOREIGN KEY (student_id) REFERENCES Students(student_id)
            )
        ''')
        conn.commit()
        print("Tables created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    create_tables()
