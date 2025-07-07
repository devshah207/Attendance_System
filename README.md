# 🎓 Face Recognition Attendance System

A comprehensive attendance management system that uses facial recognition technology to automatically track student attendance. The system combines computer vision, machine learning, and database management to provide an efficient and accurate attendance solution.

## 🌟 Features

### Core Functionality
- **Real-time Face Recognition**: Automatic student identification using webcam
- **Student Registration**: GUI-based registration system with live camera feed
- **Attendance Logging**: Automatic attendance recording with duplicate prevention
- **Database Management**: MySQL integration for student and attendance data
- **Cloud Integration**: AWS S3 support for image storage and face encodings
- **Admin Interface**: Administrative tools for managing students and attendance records

### Advanced Features
- **Duplicate Prevention**: Prevents multiple attendance entries within configurable time windows (default: 1 hour)
- **Face Encoding Management**: Efficient face encoding computation and storage
- **Multi-image Registration**: Captures multiple images per student for better recognition accuracy
- **Real-time Video Processing**: Live video feed with face detection and recognition overlay
- **Deep Learning Support**: PyTorch integration for advanced computer vision tasks

## 🏗️ Project Structure

```
Attendance System/
├── src/                          # Main source code
│   ├── main.py                   # Application entry point
│   ├── face_recognition_module.py # Core face recognition logic
│   ├── registration_module.py    # Student registration GUI
│   └── recomputation.py         # Face encoding recomputation
├── database/                     # Database modules
│   ├── database_module.py        # Database CRUD operations
│   ├── logging_module.py         # Attendance logging logic
│   ├── initialize_db.py          # Database schema setup
│   └── populate_db.py           # Database population utilities
├── face_encodings/              # Face encoding management
│   ├── data_preparation.py       # Encoding computation and loading
│   ├── upload_images_to_s3.py   # S3 image upload utilities
│   ├── upload_encodings_to_s3.py # S3 encoding upload utilities
│   ├── compute_encodings_from_s3.py # S3-based encoding computation
│   └── test.py                  # Encoding testing utilities
├── Admin/                       # Administrative tools
│   └── admin_module.py          # Admin interface functions
├── known_faces/                 # Local face image storage
├── encodings/                   # Local face encoding storage
├── requirements.txt             # Python dependencies
└── README.md                   # Project documentation
```

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- MySQL Server
- Webcam/Camera
- AWS Account (optional, for cloud features)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd "Attendance System"
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Database Setup
1. Install and start MySQL Server
2. Create database:
```sql
CREATE DATABASE attendance_db;
```
3. Update database configuration in `database/database_module.py`:
```python
DB_CONFIG = {
    "host": "localhost",
    "user": "your_username",
    "password": "your_password",
    "database": "attendance_db"
}
```
4. Initialize database tables:
```bash
cd database
python initialize_db.py
```

### Step 5: AWS Configuration (Optional)
For cloud features, configure AWS credentials:
```bash
aws configure
```
Update S3 bucket name in relevant files:
- `face_encodings/upload_images_to_s3.py`
- `face_encodings/upload_encodings_to_s3.py`
- `database/populate_db.py`

## 📖 Usage

### Student Registration
1. Run the registration module:
```bash
cd src
python registration_module.py
```
2. Enter student name in the GUI
3. Capture 5 images using the "Capture Image" button
4. Images are automatically saved and student is registered in database

### Attendance Tracking
1. Run the main attendance system:
```bash
cd src
python main.py
```
2. The system will:
   - Load face encodings from S3 or local storage
   - Start webcam feed
   - Automatically recognize and log attendance for registered students
   - Display real-time video with face detection rectangles and names
3. Press 'q' to quit the application

### Administrative Tasks
```bash
cd Admin
python admin_module.py
```
Available admin functions:
- List all students
- Update student information
- Delete student records
- View attendance records
- Delete attendance entries

## 🗄️ Database Schema

### Students Table
```sql
CREATE TABLE Students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    metadata TEXT
);
```

### Attendance Table
```sql
CREATE TABLE Attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    timestamp DATETIME NOT NULL,
    status VARCHAR(50) DEFAULT 'present',
    FOREIGN KEY (student_id) REFERENCES Students(student_id)
);
```

### Student Images Table
```sql
CREATE TABLE student_images (
    image_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    image_url VARCHAR(255) NOT NULL,
    FOREIGN KEY (student_id) REFERENCES Students(student_id)
);
```

## ⚙️ Configuration

### Face Recognition Settings
- **Tolerance**: Adjust face recognition sensitivity in `src/face_recognition_module.py`
```python
tolerance = 0.4  # Lower = more strict, Higher = more lenient
```

- **Duplicate Threshold**: Configure attendance logging frequency
```python
duplicate_threshold = 3600  # seconds (1 hour)
```

### Camera Settings
- **Resolution**: Modify frame processing size for performance optimization
```python
small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
```

### AWS S3 Configuration
Update bucket names and paths in:
- `BUCKET_NAME = "your-bucket-name"`
- `S3_IMAGE_FOLDER = "images/"`
- `PICKLE_S3_KEY = "pickle/encodings.pickle"`

## 🔧 Key Components

### Face Recognition Module (`src/face_recognition_module.py`)
- Real-time face detection and recognition
- Attendance logging with duplicate prevention
- Video stream processing and annotation
- Integration with database and cloud storage

### Registration Module (`src/registration_module.py`)
- Tkinter-based GUI for student registration
- Live camera feed with face detection
- Multi-image capture (5 images per student)
- Automatic database integration

### Database Module (`database/database_module.py`)
- Complete CRUD operations for students and attendance
- MySQL connection management
- Error handling and transaction management
- Support for filtered queries and bulk operations

### Face Encodings Management (`face_encodings/`)
- **data_preparation.py**: Local encoding computation and caching
- **upload_images_to_s3.py**: Batch image upload to S3
- **compute_encodings_from_s3.py**: Cloud-based encoding computation
- **upload_encodings_to_s3.py**: Encoding synchronization with S3

## 🚨 Troubleshooting

### Common Issues

**1. Camera Access Error**
```
Error: Cannot open webcam
```
- Ensure webcam is connected and not used by other applications
- Check camera permissions in system settings
- Try different camera indices: `cv2.VideoCapture(1)` or `cv2.VideoCapture(2)`

**2. Database Connection Error**
```
Error connecting to MySQL
```
- Verify MySQL server is running
- Check database credentials in `database/database_module.py`
- Ensure database `attendance_db` exists

**3. Face Recognition Not Working**
```
No encodings loaded. Cannot proceed with face recognition.
```
- Run student registration first to create face encodings
- Check if S3 bucket contains encodings.pickle file
- Verify AWS credentials for S3 access

**4. Import Errors**
```
ModuleNotFoundError: No module named 'face_recognition'
```
- Activate virtual environment: `source venv/bin/activate`
- Install requirements: `pip install -r requirements.txt`
- For dlib issues on Windows, install Visual Studio Build Tools

### Performance Optimization

**1. Improve Recognition Speed**
- Reduce frame processing size
- Increase tolerance value for faster matching
- Use GPU acceleration if available

**2. Reduce Memory Usage**
- Limit number of face encodings loaded
- Process smaller video frames
- Implement encoding caching strategies

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **dlib**: Face detection and recognition algorithms
- **OpenCV**: Computer vision and image processing
- **face_recognition**: Simplified face recognition API
- **PyTorch**: Deep learning framework support
- **MySQL**: Database management system
- **AWS S3**: Cloud storage solution

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the configuration settings

---

**Note**: This system is designed for educational and small-scale institutional use. For production deployment, consider additional security measures, scalability optimizations, and compliance requirements.