import os
import boto3 # type: ignore
from botocore.exceptions import ClientError# type: ignore

def upload_images_to_s3(bucket_name, known_faces_dir='../known_faces'):
    """
    Uploads only new images from the local known_faces directory to the specified S3 bucket.
    The S3 object key mirrors the folder structure: images/<StudentName>/<image_filename>.
    It checks if an object already exists in S3 before uploading.
    """
    # Create an S3 client using default credentials.
    s3_client = boto3.client('s3')

    # Iterate over each student's subfolder
    for student_name in os.listdir(known_faces_dir):
        student_folder = os.path.join(known_faces_dir, student_name)
        if not os.path.isdir(student_folder):
            continue  # Skip non-directory files

        # Upload each image in the student's folder
        for image_file in os.listdir(student_folder):
            # Only process typical image files
            if not image_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue

            local_path = os.path.join(student_folder, image_file)
            # Construct the S3 object key, e.g., "images/John_Doe/image1.jpg"
            s3_key = f"images/{student_name}/{image_file}"

            try:
                # Check if the file already exists in S3
                s3_client.head_object(Bucket=bucket_name, Key=s3_key)
                print(f"File {s3_key} already exists in bucket {bucket_name}, skipping upload.")
            except ClientError as e:
                # If the error code indicates the object does not exist, then upload it.
                if e.response['Error']['Code'] == "404":
                    try:
                        s3_client.upload_file(local_path, bucket_name, s3_key)
                        print(f"Uploaded {local_path} to s3://{bucket_name}/{s3_key}")
                    except Exception as upload_err:
                        print(f"Error uploading {local_path}: {upload_err}")
                else:
                    print(f"Error checking {s3_key}: {e}")

def main():
    # Replace with the name of your S3 bucket
    bucket_name = "attendance-images-upload"
    
    # Call the upload function
    upload_images_to_s3(bucket_name)

if __name__ == '__main__':
    main()
