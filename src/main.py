import sys
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)


from face_recognition_module import start_face_recognition
# Rest of your code...
from face_recognition_module import start_face_recognition

if __name__ == '__main__':
    start_face_recognition()