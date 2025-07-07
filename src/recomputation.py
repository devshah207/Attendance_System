import os
import pickle
import boto3 # type: ignore
import face_recognition

# Configuration
BUCKET_NAME = "attendance-images-upload"  # Your S3 bucket name
PICKLE_S3_KEY = "pickle/encodings.pickle"  # S3 key for the pickle file
KNOWN_FACES_FOLDER = "../known_faces"  # Local folder with known faces

def download_pickle_from_s3():
    """
    Downloads the encodings pickle file from S3.
    Returns an empty dictionary if the file doesn’t exist or an error occurs.
    """
    s3_client = boto3.client('s3')
    try:
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=PICKLE_S3_KEY)
        pickle_data = response['Body'].read()
        encodings_dict = pickle.loads(pickle_data)
        print("Downloaded existing pickle file from S3.")
        return encodings_dict
    except s3_client.exceptions.NoSuchKey:
        print("No existing pickle file found. Starting with an empty dictionary.")
        return {}
    except Exception as e:
        print(f"Error downloading pickle file: {e}")
        return {}

def compute_encodings_for_person(person_name):
    """
    Computes face encodings for all valid images in the person’s subfolder.
    Returns a list of encodings.
    """
    person_folder = os.path.join(KNOWN_FACES_FOLDER, person_name)
    encodings = []
    for filename in os.listdir(person_folder):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(person_folder, filename)
            image = face_recognition.load_image_file(image_path)
            face_encodings = face_recognition.face_encodings(image)
            if face_encodings:
                encodings.append(face_encodings[0])
                print(f"Computed encoding for {filename} in {person_name}'s folder.")
            else:
                print(f"No face found in {filename} in {person_name}'s folder.")
    return encodings

def upload_pickle_to_s3(encodings_dict):
    """
    Serializes the encodings dictionary and uploads it to S3.
    """
    s3_client = boto3.client('s3')
    try:
        pickle_data = pickle.dumps(encodings_dict)
        s3_client.put_object(Bucket=BUCKET_NAME, Key=PICKLE_S3_KEY, Body=pickle_data)
        print("Uploaded updated pickle file to S3.")
    except Exception as e:
        print(f"Error uploading updated pickle file: {e}")

def main():
    # Step 1: Download existing encodings from S3
    encodings_dict = download_pickle_from_s3()

    # Step 2: List all persons in the known_faces folder
    known_persons = [
        name for name in os.listdir(KNOWN_FACES_FOLDER)
        if os.path.isdir(os.path.join(KNOWN_FACES_FOLDER, name))
    ]

    # Step 3: Identify new persons
    existing_persons = set(encodings_dict.keys())
    all_persons = set(known_persons)
    new_persons = all_persons - existing_persons

    # Step 4 & 5: Compute encodings for new persons and update the dictionary
    for person in new_persons:
        person_encodings = compute_encodings_for_person(person)
        if person_encodings:
            encodings_dict[person] = person_encodings
            print(f"Added encodings for {person}.")
        else:
            print(f"No encodings found for {person}.")

    # Step 6: Upload the updated encodings back to S3
    upload_pickle_to_s3(encodings_dict)

if __name__ == "__main__":
    main()