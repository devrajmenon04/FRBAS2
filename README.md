# Facial Recognition Based Attendance System (FRBAS2)

A Flask-based web application that uses facial recognition and emotion detection to automatically mark attendance while analyzing student moods.

## Features

✨ **Core Features:**
- 🎭 **Facial Recognition**: Identify students using KNN-based face recognition
- 😊 **Emotion Detection**: Analyze student moods (happy, sad, angry, etc.) using DeepFace
- 📱 **Web Interface**: Clean web dashboard for attendance management
- 📊 **Attendance Tracking**: Real-time attendance with timestamps and mood records
- 💾 **Excel Export**: Export attendance reports to Excel format
- 📧 **Email Integration**: Send attendance reports via email
- 👥 **User Management**: Add, delete, and manage student profiles
- 🎥 **Real-time Processing**: Live camera feed with instant face/emotion detection

## Requirements

- Python 3.8+
- Webcam/Camera
- 4GB+ RAM (recommended for smooth operation)
- Windows/Linux/macOS

## Installation

### Option 1: Local Development

1. **Clone the repository**
```bash
git clone https://github.com/devrajmenon04/FRBAS2.git
cd FRBAS2
```

2. **Create virtual environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
python app.py
```

5. **Access the app**
Open your browser and go to: `http://localhost:5001`

### Option 2: Docker Deployment

1. **Install Docker** (if not already installed)
   - Download from [docker.com](https://www.docker.com/)

2. **Build and run**
```bash
docker-compose up -d
```

3. **Access the app**
Open your browser and go to: `http://localhost:5001`

## Configuration

### Email Setup (Optional)

To enable attendance report email functionality:

1. Create `.env` file in project root:
```
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

2. For Gmail:
   - Enable 2-factor authentication
   - Generate [App Password](https://support.google.com/accounts/answer/185833)
   - Use the app password in `.env`

### Camera Configuration

- Default camera index: 0
- To use different camera, modify `cv2.VideoCapture(0)` in `app.py`

## Usage

### Add New Student

1. Click **"Add New Student"** on home page
2. Enter name and roll number
3. Capture 10 face images (press SPACE to capture, ESC to exit)
4. System automatically trains the model

### Mark Attendance

1. Click **"Take Attendance"** 
2. Position face in front of camera
3. System detects face and emotion
4. Press ESC to confirm and save attendance
5. View attendance on dashboard

### View Attendance

- **Home Page**: Shows today's attendance
- **Dashboard**: View recent entries and statistics
- **Export**: Download attendance as Excel file

### Manage Students

- **List Users**: View all registered students
- **Delete User**: Remove student and retrain model
- **Clear Attendance**: Remove specific student from today's attendance

## Project Structure

```
FRBAS2/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── haarcascade_frontalface_default.xml  # Face detection model
├── Dockerfile                      # Docker configuration
├── docker-compose.yml              # Docker Compose setup
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore rules
├── static/
│   ├── faces/                      # Student face images
│   ├── face_recognition_model.pkl  # Trained KNN model
│   └── label_mapping.pkl           # Label mapping
├── Attendance/
│   └── Attendance-*.csv            # Daily attendance records
└── templates/
    ├── home.html                   # Home page
    ├── add_user.html               # Add student page
    ├── listusers.html              # List students page
    └── dashboard.html              # Dashboard page
```

## Troubleshooting

### Camera Not Working
- Check camera permissions
- Try different camera index (0, 1, 2)
- Restart the application

### Face Not Detected
- Ensure adequate lighting
- Face should be clearly visible
- Try capturing from different angles
- Ensure minimum 10 images were captured

### Model Training Error
- Ensure at least one student is registered
- Check disk space
- Verify file permissions in `static/` directory

### Email Not Sending
- Verify email credentials in `.env`
- Check Gmail app password
- Ensure firewall allows SMTP (port 587)
- Enable "Less secure apps" if not using app password

### Performance Issues
- Reduce video resolution in `app.py`
- Increase `face_detect_interval` for fewer detections
- Close other heavy applications
- Use GPU if available

## Technologies Used

- **Flask**: Web framework
- **OpenCV**: Computer vision and face detection
- **DeepFace**: Emotion recognition
- **scikit-learn**: KNN classifier for face recognition
- **pandas**: Data manipulation
- **openpyxl**: Excel file generation

## API Endpoints

```
GET  /                    - Home page
GET  /dashboard          - Dashboard
GET  /adduser            - Add student form
POST /add                - Submit new student
GET  /start              - Start attendance capture
GET  /listusers          - List all students
GET  /deleteuser         - Delete student
GET  /clearattendance    - Clear attendance record
POST /export_attendance  - Export and email attendance
```

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | i3 | i5+ |
| RAM | 4GB | 8GB+ |
| Storage | 2GB | 10GB+ |
| Camera | 0.3MP | 2MP+ |
| Internet | Optional* | For email feature |

*Optional unless using email functionality

## Performance Tips

1. **Reduce Resolution**: Lower video resolution for faster processing
2. **Skip Frames**: Increase `face_detect_interval` to reduce CPU usage
3. **Batch Processing**: Process multiple students sequentially
4. **GPU Acceleration**: Use GPU for faster face recognition (optional setup)

## Security Considerations

⚠️ **Important**: 
- Never commit `.env` file with real credentials
- Change `app.secret_key` in production
- Use HTTPS in production
- Implement proper authentication
- Secure face image storage
- Comply with privacy regulations (GDPR, FERPA)

## Deployment Options

### Local Windows/Linux
Use provided setup scripts and install locally

### Docker Container
Use `docker-compose up` for containerized deployment

### Cloud Platforms
- **AWS EC2**: Deploy on Ubuntu instance
- **Google Cloud**: Use Compute Engine
- **Azure**: Deploy on Virtual Machines
- **Heroku**: Limited support (requires headless mode)

See `DEPLOYMENT_GUIDE.md` for detailed cloud deployment instructions.

## Known Limitations

- Single camera only
- Requires manual face capture during enrollment
- May struggle in low light conditions
- Works best with frontal face orientation
- Emotion detection accuracy depends on face visibility

## Future Enhancements

- [ ] Multi-camera support
- [ ] Real-time emotion statistics
- [ ] Mobile app integration
- [ ] Advanced analytics dashboard
- [ ] Multi-model face recognition
- [ ] Attendance predictions
- [ ] SMS notifications
- [ ] Biometric liveness detection

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or suggestions:
- Open an [Issue](https://github.com/devrajmenon04/FRBAS2/issues)
- Contact: devrajmenon04@github.com

## Disclaimer

This system is for educational and authorized use only. Ensure compliance with local privacy laws and obtain necessary permissions before deploying facial recognition systems.

---

**Last Updated**: April 2026
**Version**: 2.0
