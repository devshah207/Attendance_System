import os
import pickle
import cv2
import face_recognition
import boto3 #type: ignore
import pickle
import io

BUCKET_NAME = "attendance-images-upload"
PICKLE_S3_KEY = "pickle/encodings.pickle"

def get_latest_modification_time(directory):
    """
    Walk through the directory and return the latest modification time of any file.
    """
    latest_time = 0
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_time = os.path.getmtime(file_path)
            if file_time > latest_time:
                latest_time = file_time
    return latest_time

def compute_face_encodings(known_faces_dir):
    """
    Iterate through the known_faces directory, compute face encodings for each student,
    and store them in a dictionary where each key is the student's name and the value
    is a list of their face encodings.
    """
    encodings = {}  # {student_name: [encoding1, encoding2, ...]}
    
    for student_name in os.listdir(known_faces_dir):
        student_folder = os.path.join(known_faces_dir, student_name)
        if not os.path.isdir(student_folder):
            continue  # Skip non-directory files
        encodings[student_name] = []
        
        for image_file in os.listdir(student_folder):
            image_path = os.path.join(student_folder, image_file)
            image = cv2.imread(image_path)
            if image is None:
                continue  # Skip unreadable images
            # Convert the image from BGR (OpenCV format) to RGB (face_recognition format)
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            face_encs = face_recognition.face_encodings(rgb_image)
            if face_encs:
                encodings[student_name].append(face_encs[0])
    
    return encodings

def load_or_compute_encodings(known_faces_dir='../known_faces', pickle_path='../encodings/encodings.pickle'):
    """
    Load precomputed face encodings from a pickle file if available and up-to-date.
    Otherwise, compute the encodings and save them to the pickle file.
    """
    recompute = False
    if os.path.exists(pickle_path):
        try:
            with open(pickle_path, 'rb') as f:
                encodings = pickle.load(f)
            print("Encodings loaded from pickle file.")

            # Check modification times
            pickle_mod_time = os.path.getmtime(pickle_path)
            faces_mod_time = get_latest_modification_time(known_faces_dir)
            if faces_mod_time > pickle_mod_time:
                print("New images detected. Recomputing encodings...")
                recompute = True
        except (EOFError, pickle.UnpicklingError, Exception) as e:
            print(f"Error loading pickle file: {e}")
            recompute = True
    else:
        recompute = True

    if recompute:
        print("Computing face encodings from images...")
        encodings = compute_face_encodings(known_faces_dir)
        os.makedirs(os.path.dirname(pickle_path), exist_ok=True)
        with open(pickle_path, 'wb') as f:
            pickle.dump(encodings, f)
        print("Encodings computed and saved to pickle file.")
    
    return encodings

def load_known_encodings():
    """Load face encodings from a pickle file stored in S3."""
    s3_client = boto3.client('s3')
    try:
        # Download the pickle file as a byte stream
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=PICKLE_S3_KEY)
        pickle_data = response['Body'].read()
        # Deserialize the pickle data into a dictionary
        encodings_dict = pickle.loads(pickle_data)
        print("Loaded encodings from S3 successfully.")
        return encodings_dict
    except Exception as e:
        print(f"Error loading encodings from S3: {e}")
        return {}
