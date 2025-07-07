import boto3#type: ignore
import pickle
import io
import cv2
import face_recognition
from datetime import datetime
from face_encodings.data_preparation import load_or_compute_encodings,load_known_encodings
from database.logging_module import log_attendance

def start_face_recognition():
    # Load or compute the known face encodings with update checking

    known_encodings_dict = load_known_encodings()
    
    if not known_encodings_dict:
        print("No encodings loaded. Cannot proceed with face recognition.")
        return
    # try:
    #     known_encodings = load_or_compute_encodings(
    #         known_faces_dir='../known_faces', 
    #         pickle_path='../encodings/encodings.pickle'
    #     )
    # except Exception as e:
    #     print(f"Error loading face encodings: {e}")
    #     return

    # if not known_encodings:
    #     print("No known faces found. Exiting.")
    #     return

    # Open a connection to the webcam
    try:
        video_capture = cv2.VideoCapture(0)
    except Exception as e:
        print(f"Error initializing webcam: {e}")
        return

    duplicate_threshold = 3600  # in seconds (e.g., 1 hr)

    if not video_capture.isOpened():
        print("Error: Cannot open webcam.")
        return

    # Dictionary to keep track of the last logged time for each student in the current session
    session_log = {}
    tolerance = 0.4  # Face recognition tolerance (adjust as needed)

    try:
        while True:
            # Read a frame from the webcam
            ret, frame = video_capture.read()
            if not ret:
                print("Failed to grab frame from webcam.")
                break

            # Resize and convert the frame for faster processing
            try:
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            except Exception as e:
                print(f"Error processing frame: {e}")
                continue

            # Detect face locations and compute face encodings for the current frame
            try:
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            except Exception as e:
                print(f"Error detecting faces: {e}")
                continue

            names = []
            for face_encoding in face_encodings:
                name = "Unknown"
                try:
                    # Compare with known encodings
                    for student_name, student_encodings in known_encodings_dict.items():
                        matches = face_recognition.compare_faces(student_encodings, face_encoding, tolerance)
                        if True in matches:
                            name = student_name
                            break  # Found a match; no need to check further
                except Exception as e:
                    print(f"Error comparing face encodings: {e}")
                names.append(name)

            # Process and annotate recognized faces
            for (top, right, bottom, left), name in zip(face_locations, names):
                try:
                    # Scale back up face locations (since we resized earlier)
                    top *= 4
                    right *= 4
                    bottom *= 4
                    left *= 4
                except Exception as e:
                    print(f"Error scaling face location coordinates: {e}")
                    continue

                if name != "Unknown":
                    try:
                        # Draw rectangle and label for recognized students
                        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                        cv2.putText(frame, name, (left, top - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
                    except Exception as e:
                        print(f"Error drawing annotations: {e}")

                    try:
                        # Log attendance if not logged recently
                        current_time = datetime.now()
                        if name in session_log:
                            if (current_time - session_log[name]).total_seconds() >= duplicate_threshold:
                                log_attendance(name)
                                session_log[name] = current_time
                        else:
                            log_attendance(name)
                            session_log[name] = current_time
                    except Exception as e:
                        print(f"Error logging attendance for {name}: {e}")

            # Display the resulting frame
            try:
                cv2.imshow("Face Recognition Attendance", frame)
            except Exception as e:
                print(f"Error displaying frame: {e}")

            # Press 'q' to exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("Keyboard interrupt received. Exiting.")
    except Exception as e:
        print(f"An unexpected error occurred during processing: {e}")
    finally:
        # Release the webcam and close windows regardless of errors
        video_capture.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    start_face_recognition()
