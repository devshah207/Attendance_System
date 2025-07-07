import sys
import os

# Add the parent directory to sys.path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)
import cv2
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import face_recognition
from database.database_module import get_student_by_name, create_student, insert_student_image





class RegistrationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Student Registration")
        self.geometry("800x600")
        self.resizable(False, False)

        # Use a themed style for better visuals
        self.style = ttk.Style(self)
        self.style.theme_use('clam')  # You can experiment with other themes like 'alt' or 'default'

        # Initialize instance variables
        self.captured_count = 0
        self.desired_images = 5

        # Setup UI components
        self.create_widgets()

        # Open the webcam
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Cannot access the webcam.")
            self.destroy()
        else:
            self.update_video()

    def create_widgets(self):
        # Top Frame for input controls
        control_frame = ttk.Frame(self, padding="10 10 10 10")
        control_frame.pack(side=tk.TOP, fill=tk.X)

        name_label = ttk.Label(control_frame, text="Enter Your Name:")
        name_label.pack(side=tk.LEFT, padx=5)

        self.name_entry = ttk.Entry(control_frame, width=30)
        self.name_entry.pack(side=tk.LEFT, padx=5)

        capture_button = ttk.Button(control_frame, text="Capture Image", command=self.capture_image)
        capture_button.pack(side=tk.LEFT, padx=5)

        quit_button = ttk.Button(control_frame, text="Quit", command=self.quit_app)
        quit_button.pack(side=tk.LEFT, padx=5)

        # Frame for video display
        self.video_frame = ttk.Frame(self, relief=tk.SUNKEN, padding="10 10 10 10")
        self.video_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.video_label = ttk.Label(self.video_frame)
        self.video_label.pack()

        # Frame for displaying thumbnails of captured images
        self.thumbnail_frame = ttk.Frame(self, padding="10 10 10 10")
        self.thumbnail_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

    def update_video(self):
        # Read a frame from the webcam and update the video label
        ret, frame = self.cap.read()
        if ret:
            # Resize the frame to fit the video display area
            frame = cv2.resize(frame, (640, 480))
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            imgtk = ImageTk.PhotoImage(image=pil_image)
            self.video_label.imgtk = imgtk  # Keep a reference to avoid garbage collection
            self.video_label.configure(image=imgtk)
        # Schedule the next frame update
        self.after(10, self.update_video)

    def capture_image(self):
        # Validate student name entry
        student_name = self.name_entry.get().strip()
        if not student_name:
            messagebox.showinfo("Input Error", "Please enter your name first.")
            return

        ret, frame = self.cap.read()
        if not ret:
            messagebox.showerror("Error", "Failed to capture image from webcam.")
            return

        # Convert frame to RGB for face detection
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        if not face_locations:
            messagebox.showinfo("No Face Detected", "No face detected. Please adjust your position and try again.")
            return

        # Create a directory for the student if it doesn't exist
        # Local directory where images are temporarily stored
        output_dir = os.path.join("..", "known_faces", student_name)
        os.makedirs(output_dir, exist_ok=True)

        # Increment counter and save the captured image
        self.captured_count += 1
        image_filename = f"{self.captured_count}.jpg"
        local_image_path = os.path.join(output_dir, image_filename)
        cv2.imwrite(local_image_path, frame)
        messagebox.showinfo("Captured", f"Captured image {self.captured_count} for {student_name}")

        # Display a thumbnail of the captured image in the UI
        thumb = cv2.resize(frame, (100, 75))
        thumb = cv2.cvtColor(thumb, cv2.COLOR_BGR2RGB)
        thumb_image = Image.fromarray(thumb)
        thumb_photo = ImageTk.PhotoImage(thumb_image)
        thumb_label = ttk.Label(self.thumbnail_frame, image=thumb_photo)
        thumb_label.image = thumb_photo  # Keep a reference
        thumb_label.pack(side=tk.LEFT, padx=5)

        # Handle new student registration and image insertion into MySQL
        student = get_student_by_name(student_name)
        if student is None:
            # Student is new; create a new record
            student_id = create_student(student_name, metadata=None)
            if student_id is None:
                messagebox.showerror("Database Error", "Failed to register student in the database.")
                return
        else:
            student_id = student.get("student_id")

        # Compute the relative path for storage in the database (relative to the known_faces folder)
        relative_path = os.path.join(student_name, image_filename)
        # Insert the image record into the student_images table (storing the relative path)
        if not insert_student_image(student_id, relative_path):
            messagebox.showerror("Database Error", "Failed to save image record in the database.")

        if self.captured_count >= self.desired_images:
            messagebox.showinfo("Registration Completed",
                                f"Successfully captured {self.captured_count} images for {student_name}.")

    def quit_app(self):
        # Cleanly release the webcam and close the application
        if self.cap.isOpened():
            self.cap.release()
        self.destroy()

if __name__ == "__main__":
    app = RegistrationApp()
    app.mainloop()


