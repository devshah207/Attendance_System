import os
import io
import pickle
import boto3  # type: ignore
import face_recognition
from PIL import Image
import numpy as np

# Set these variables as needed.
BUCKET_NAME = "attendance-images-upload"
# Set the prefix for where your images are stored in S3.
# For example, if your images are under a folder "images/", then:
IMAGE_PREFIX = "images/"  # Use an empty string ("") if there's no prefix.

def list_image_keys(bucket, prefix=""):
    """Lists all image object keys in the given S3 bucket under the specified prefix."""
    s3 = boto3.client("s3")
    keys = []
    paginator = s3.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=bucket, Prefix=prefix)
    for page in pages:
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key.lower().endswith((".jpg", ".jpeg", ".png")):
                keys.append(key)
    return keys

def get_encoding_for_image(bucket, key):
    """Streams an image from S3, computes its face encoding, and returns the encoding."""
    s3 = boto3.client("s3")
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        image_data = io.BytesIO(response["Body"].read())
        image = Image.open(image_data)
        if image.mode != "RGB":
            image = image.convert("RGB")
        np_image = np.array(image)
        encodings = face_recognition.face_encodings(np_image)
        if encodings:
            return encodings[0]
        else:
            return None
    except Exception as e:
        print(f"Error processing {key}: {e}")
        return None

def compute_encodings():
    """
    Streams images from S3, computes face encodings, and builds a dictionary.
    The dictionary maps student names (derived from folder names) to a list of encodings.
    
    If IMAGE_PREFIX is provided (e.g., "images/"), the code removes that prefix before splitting
    the key. For example, if an object key is "images/JohnDoe/img1.jpg", then after removing the prefix,
    it splits "JohnDoe/img1.jpg" and takes "JohnDoe" as the student name.
    """
    encodings_dict = {}
    keys = list_image_keys(BUCKET_NAME, IMAGE_PREFIX)
    print(f"Found {len(keys)} image keys in bucket '{BUCKET_NAME}' with prefix '{IMAGE_PREFIX}'.")
    
    for key in keys:
        # Remove the prefix from the key if it exists.
        if IMAGE_PREFIX and key.startswith(IMAGE_PREFIX):
            key_without_prefix = key[len(IMAGE_PREFIX):]
        else:
            key_without_prefix = key

        # Assume the key format is: StudentName/filename.jpg
        parts = key_without_prefix.split("/")
        if len(parts) < 2:
            print(f"Skipping key {key} because it doesn't match expected format.")
            continue
        student_name = parts[0]
        
        encoding = get_encoding_for_image(BUCKET_NAME, key)
        if encoding is not None:
            encodings_dict.setdefault(student_name, []).append(encoding)
            print(f"Processed encoding for {key}.")
        else:
            print(f"No encoding found for {key}.")
    return encodings_dict

def main():
    encodings_dict = compute_encodings()
    output_file = "../encodings/encodings.pickle"
    with open(output_file, "wb") as f:
        pickle.dump(encodings_dict, f)
    print(f"Saved encodings to {output_file}.")

if __name__ == "__main__":
    main()
