import boto3  # type: ignore

# Update these variables with your bucket name and desired S3 key for the pickle file.
BUCKET_NAME = "attendance-images-upload"
PICKLE_FILE = "../encodings/encodings.pickle"
S3_DESTINATION_KEY = "pickle/encodings.pickle"  # Store the file in the "pickle" folder

def upload_pickle_to_s3():
    s3 = boto3.client("s3")
    try:
        s3.upload_file(PICKLE_FILE, BUCKET_NAME, S3_DESTINATION_KEY)
        print(f"Uploaded {PICKLE_FILE} to s3://{BUCKET_NAME}/{S3_DESTINATION_KEY}")
    except Exception as e:
        print(f"Error uploading pickle file: {e}")

if __name__ == "__main__":
    upload_pickle_to_s3()
