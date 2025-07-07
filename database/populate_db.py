import os
from database_module import get_student_by_name, create_student, insert_student_image

# Define the base directory for known faces relative to this script's location.
KNOWN_FACES_DIR = os.path.join("..", "known_faces")
# Define your S3 bucket name.
BUCKET_NAME = "attendance-images-upload"
# Define the S3 base URL (this may vary depending on your region/configuration).
S3_BASE_URL = f"https://{BUCKET_NAME}.s3.amazonaws.com/"
# Define the S3 folder prefix for images (update if you changed it when uploading).
S3_IMAGE_FOLDER = "images/"  # for example, images/StudentName/filename.jpg

def populate_database():
    # Iterate through each student folder in KNOWN_FACES_DIR.
    for student_name in os.listdir(KNOWN_FACES_DIR):
        student_folder = os.path.join(KNOWN_FACES_DIR, student_name)
        if not os.path.isdir(student_folder):
            continue  # Skip any files that are not directories

        print(f"Processing student: {student_name}")

        # Check if the student already exists in the database.
        student = get_student_by_name(student_name)
        if student is None:
            # Create a new student record if not found.
            student_id = create_student(student_name, metadata=None)
            if not student_id:
                print(f"Failed to create record for student: {student_name}")
                continue
            print(f"Created student '{student_name}' with ID {student_id}")
        else:
            student_id = student.get("student_id")
            print(f"Student '{student_name}' already exists with ID {student_id}")

        # For each image in the student's folder, insert a record into the student_images table.
        for image_filename in os.listdir(student_folder):
            # Process only files with typical image extensions.
            if not image_filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue

            # Construct a relative image path (relative to the known_faces directory).
            relative_image_path = os.path.join(student_name, image_filename)
            # Build the full S3 key by prepending the S3 folder prefix.
            s3_key = S3_IMAGE_FOLDER + relative_image_path.replace(os.sep, "/")
            # Build the full S3 URL for the image.
            image_url = S3_BASE_URL + s3_key
            success = insert_student_image(student_id, image_url)
            if success:
                print(f"Inserted image '{image_url}' for student '{student_name}'")
            else:
                print(f"Failed to insert image '{image_url}' for student '{student_name}'")

if __name__ == '__main__':
    populate_database()
