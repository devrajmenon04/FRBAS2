import cv2
import os
from flask import Flask, request, render_template, flash, redirect, url_for
from datetime import date
from datetime import datetime
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
import pandas as pd
import joblib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email import encoders
from flask import jsonify, send_file
import json
from datetime import timedelta
from openpyxl import Workbook

# Defining Flask App
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for flash messages

# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "deepalimenon2004@gmail.com"  # Replace with your email
SMTP_PASSWORD = "kxdf jnvk zbyp wblc"     # Replace with your app password

nimgs = 10

# Saving Date today in 2 different formats
datetoday = date.today().strftime("%m_%d_%y")
datetoday2 = date.today().strftime("%d-%B-%Y")


# Initializing VideoCapture object to access WebCam
face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Verify the classifier is loaded
if face_detector.empty():
    raise ValueError("Error: Cascade classifier not loaded properly!")


# If these directories don't exist, create them

# Ensure Attendance directory exists before any file operations
if not os.path.isdir('Attendance'):
    os.makedirs('Attendance')

# Ensure static/faces directory exists before any file operations
if not os.path.isdir('static/faces'):
    os.makedirs('static/faces')

# Now it's safe to check for the CSV file
if f'Attendance-{datetoday}.csv' not in os.listdir('Attendance'):
    with open(f'Attendance/Attendance-{datetoday}.csv', 'w') as f:
        f.write('Name,Roll,Time,Mood\n')  # Added newline character


# get a number of total registered users
def totalreg():
    return len(os.listdir('static/faces'))


# extract the face from an image
def extract_faces(img):
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_points = face_detector.detectMultiScale(gray, 1.2, 5, minSize=(20, 20))
        return face_points
    except:
        return []


# Identify face using ML model
def train_model():
    faces = []
    labels = []
    userlist = os.listdir('static/faces')
    
    # Create a label mapping dictionary
    label_to_name = {}
    for idx, user in enumerate(userlist):
        label_to_name[idx] = user
    
    for idx, user in enumerate(userlist):
        user_images = os.listdir(f'static/faces/{user}')
        for imgname in user_images:
            img = cv2.imread(f'static/faces/{user}/{imgname}')
            if img is None:
                continue
                
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)
            resized_face = cv2.resize(gray, (50, 50))
            
            face_normalized = (resized_face - np.mean(resized_face)) / np.std(resized_face)
            faces.append(face_normalized.ravel())
            labels.append(idx)
    
    if len(faces) == 0:
        raise ValueError("No valid faces found for training")
    
    faces = np.array(faces)
    labels = np.array(labels)
    
    knn = KNeighborsClassifier(n_neighbors=5, weights='distance', metric='euclidean')
    knn.fit(faces, labels)
    
    # Save model and mapping separately
    joblib.dump(knn, 'static/face_recognition_model.pkl')
    joblib.dump(label_to_name, 'static/label_mapping.pkl')

def identify_face(facearray):
    try:
        # Load model and mapping separately
        model = joblib.load('static/face_recognition_model.pkl')
        label_mapping = joblib.load('static/label_mapping.pkl')
    except FileNotFoundError:
        return ["Unknown"]
    
    # Convert the input face to grayscale and normalize
    if len(facearray.shape) == 3:
        gray = cv2.cvtColor(facearray.reshape((50, 50, 3)), cv2.COLOR_BGR2GRAY)
    else:
        gray = facearray.reshape((50, 50))
    
    # Normalize the face image
    face_normalized = (gray - np.mean(gray)) / np.std(gray)
    face_vector = face_normalized.ravel()
    
    n_neighbors = 5
    distances, indices = model.kneighbors(face_vector.reshape(1, -1), n_neighbors=n_neighbors)
    
    min_distance = distances[0][0]
    mean_distance = np.mean(distances[0])
    
    predictions = [model._y[idx] for idx in indices[0]]
    most_common = max(set(predictions), key=predictions.count)
    prediction_confidence = predictions.count(most_common) / len(predictions)
    
    distance_threshold = 11000
    confidence_threshold = 0.6
    mean_distance_threshold = 13000
    
    is_unknown = (
        min_distance > distance_threshold or
        mean_distance > mean_distance_threshold or
        prediction_confidence < confidence_threshold
    )
    
    if is_unknown:
        return ["Unknown"]
    
    return [label_mapping[most_common]]

# First, update the CSV initialization
if not os.path.isdir('Attendance'):
    os.makedirs('Attendance')

# Remove any existing attendance file to ensure clean start
# Remove these lines that recreate the file
# if os.path.exists(f'Attendance/Attendance-{datetoday}.csv'):
#     os.remove(f'Attendance/Attendance-{datetoday}.csv')

# Only create the file if it doesn't exist
if not os.path.isdir('Attendance'):
    os.makedirs('Attendance')

if not os.path.exists(f'Attendance/Attendance-{datetoday}.csv'):
    with open(f'Attendance/Attendance-{datetoday}.csv', 'w', newline='') as f:
        f.write('Name,Roll,Time,Mood\n')

# Update add_attendance function to properly append
def add_attendance(name, mood="Unknown"):
    if name == "Unknown":
        return
        
    username = name.split('_')[0]
    userid = name.split('_')[1]
    current_time = datetime.now().strftime("%H:%M:%S")

    try:
        df = pd.read_csv(f'Attendance/Attendance-{datetoday}.csv')
        if int(userid) not in list(df['Roll']):
            with open(f'Attendance/Attendance-{datetoday}.csv', 'a', newline='') as f:
                f.write(f'{username},{userid},{current_time},{mood}\n')
    except Exception as e:
        print(f"Error adding attendance: {str(e)}")

# Add this new function after extract_attendance()
def clear_attendance(userid):
    try:
        # Read the CSV file
        df = pd.read_csv(f'Attendance/Attendance-{datetoday}.csv')
        
        # Convert Roll column to string for comparison
        df['Roll'] = df['Roll'].astype(str)
        
        # Filter out the rows where Roll matches userid
        df = df[df['Roll'] != str(userid)]
        
        # Write the updated dataframe back to CSV
        df.to_csv(f'Attendance/Attendance-{datetoday}.csv', index=False)
        
    except Exception as e:
        print(f"Error clearing attendance: {str(e)}")

# Add this new route before the main function
## A function to get names and rol numbers of all users
def getallusers():
    userlist = os.listdir('static/faces')
    names = []
    rolls = []
    l = len(userlist)

    for i in userlist:
        name, roll = i.split('_')
        names.append(name)
        rolls.append(roll)

    return userlist, names, rolls, l


## A function to delete a user folder 
def deletefolder(duser):
    pics = os.listdir(duser)
    for i in pics:
        os.remove(duser+'/'+i)
    os.rmdir(duser)




################## ROUTING FUNCTIONS #########################

# Extract info from today's attendance file in attendance folder
# Remove the duplicate CSV initialization and keep only this one at the beginning
if not os.path.isdir('Attendance'):
    os.makedirs('Attendance')
if f'Attendance-{datetoday}.csv' not in os.listdir('Attendance'):
    with open(f'Attendance/Attendance-{datetoday}.csv', 'w') as f:
        f.write('Name,Roll,Time,Mood\n')

# Update the extract_attendance function
def extract_attendance():
    try:
        df = pd.read_csv(f'Attendance/Attendance-{datetoday}.csv')
        # Ensure all required columns exist
        required_columns = ['Name', 'Roll', 'Time', 'Mood']
        for col in required_columns:
            if col not in df.columns:
                df[col] = 'Unknown'
        
        names = df['Name']
        rolls = df['Roll']
        times = df['Time']
        moods = df['Mood']
        l = len(df)
        return names, rolls, times, moods, l
    except Exception as e:
        print(f"Error reading attendance file: {str(e)}")
        # Return empty data if there's an error
        return [], [], [], [], 0

# Our main page
# Add this new route

# Update the home route
@app.route('/')
def home():
    names, rolls, times, moods, l = extract_attendance()
    return render_template('home.html', names=names, rolls=rolls, times=times, moods=moods, l=l, totalreg=totalreg(), datetoday2=datetoday2)

@app.route('/dashboard')
def dashboard():
    names, rolls, times, moods, l = extract_attendance()
    recent_entries = min(5, l)
    return render_template('dashboard.html', 
                         names=names, 
                         rolls=rolls, 
                         times=times, 
                         moods=moods,
                         l=l, 
                         recent_entries=recent_entries,
                         totalreg=totalreg(), 
                         datetoday2=datetoday2)

@app.route('/clearattendance', methods=['GET'])
def clearattendance():
    userid = request.args.get('userid')
    clear_attendance(userid)
    names, rolls, times, moods, l = extract_attendance()
    return render_template('home.html', names=names, rolls=rolls, times=times, moods=moods, l=l, totalreg=totalreg(), datetoday2=datetoday2)


## List users page
@app.route('/listusers')
def listusers():
    userlist, names, rolls, l = getallusers()
    return render_template('listusers.html', userlist=userlist, names=names, rolls=rolls, l=l, totalreg=totalreg(), datetoday2=datetoday2)


## Delete functionality
@app.route('/deleteuser', methods=['GET'])
def deleteuser():
    duser = request.args.get('user')
    deletefolder('static/faces/'+duser)

    ## if all the face are deleted, delete the trained files...
    if os.listdir('static/faces/')==[]:
        if os.path.exists('static/face_recognition_model.pkl'):
            os.remove('static/face_recognition_model.pkl')
        if os.path.exists('static/label_mapping.pkl'):
            os.remove('static/label_mapping.pkl')
    
    try:
        train_model()
    except Exception as e:
        print(f"Error training model: {str(e)}")
    
    # Redirect back to the list users page
    return redirect(url_for('listusers'))


# Our main Face Recognition functionality. 
# This function will run when we click on Take Attendance Button.
# In the start route
# Add this import at the top with other imports
from deepface import DeepFace

# Add these imports at the top with other imports
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Add this function after the emotion_emojis dictionary
def draw_text_with_emoji(frame, text, position, font_size=30):
    # Convert OpenCV BGR to RGB for PIL
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(rgb_frame)
    draw = ImageDraw.Draw(pil_image)
    
    try:
        # Try to use a font that supports emojis (Segoe UI Emoji for Windows)
        font = ImageFont.truetype("seguiemj.ttf", font_size)
    except:
        # Fallback to default font if emoji font not available
        font = ImageFont.load_default()
    
    # Draw the text with emoji
    draw.text(position, text, font=font, fill=(255, 255, 255))
    
    # Convert back to OpenCV format
    frame = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    return frame

# Modify the start() function to include mood detection
@app.route('/start', methods=['GET'])
def start():
    if 'face_recognition_model.pkl' not in os.listdir('static'):
        return render_template('home.html', names=[], rolls=[], times=[], l=0, totalreg=totalreg(), datetoday2=datetoday2, mess='There is no trained model in the static folder. Please add a new face to continue.')

    # Try multiple camera indices with optimized initialization
    cap = None
    for camera_index in [0, 1]:
        cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)  # Use DirectShow
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize frame buffer
        if cap.isOpened():
            # Set camera properties immediately after successful opening
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            cap.set(cv2.CAP_PROP_FPS, 30)  # Set FPS explicitly
            cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)  # Enable autofocus
            # Warm up the camera
            for _ in range(5):
                cap.read()
            break
    
    if not cap or not cap.isOpened():
        return render_template('home.html', names=[], rolls=[], times=[], l=0, totalreg=totalreg(), datetoday2=datetoday2, mess='Could not access the camera. Please check your camera connection.')

    # Remove the duplicate property settings since we set them above
    cv2.namedWindow('Attendance System', cv2.WINDOW_NORMAL)
    cv2.setWindowProperty('Attendance System', cv2.WND_PROP_AUTOSIZE, cv2.WINDOW_AUTOSIZE)
    cv2.setWindowProperty('Attendance System', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    identified_person = "Unknown"
    dominant_emotion = "Unknown"
    ret = True  # Initialize ret variable
    
    # After other imports
    from collections import deque
    import numpy as np
    
    # Add this dictionary after other global variables
    emotion_emojis = {
        'happy': '😊',
        'sad': '😢',
        'angry': '😠',
        'surprise': '😮',
        'fear': '😨',
        'disgust': '🤢',
        'neutral': ''
    }

    # Add after other global variables (after datetoday2 definition)
    emotion_history = deque(maxlen=5)  # Store last 5 frames of emotions
    last_emotion = "neutral"
    emotion_stability_threshold = 3  # Number of frames needed for stable emotion
    
    # Add these variables before the while loop
    last_face_coords = None
    face_detect_interval = 5  # Detect face every 5 frames
    frame_count = 0

    while ret:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        # Only run face detection every N frames
        if frame_count % face_detect_interval == 0 or last_face_coords is None:
            faces = extract_faces(frame)
            if len(faces) > 0:
                last_face_coords = faces[0]
        # Use last detected face for intermediate frames
        if last_face_coords is not None:
            (x, y, w, h) = last_face_coords
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            overlay = frame.copy()
            cv2.rectangle(overlay, (x, y-60), (x+w, y), (0, 128, 0), -1)
            frame = cv2.addWeighted(overlay, 0.3, frame, 0.7, 0)

            face = cv2.resize(frame[y:y+h, x:x+w], (50, 50))
            face_gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
            identified_person = identify_face(face_gray)[0]

            # Enhanced emotion detection with multiple models and preprocessing
            try:
                if h > 0 and w > 0:
                    face_img = frame[max(0, y):min(y+h, frame.shape[0]), 
                                   max(0, x):min(x+w, frame.shape[1])]
                    face_img_yuv = cv2.cvtColor(face_img, cv2.COLOR_BGR2YUV)
                    face_img_yuv[:,:,0] = cv2.equalizeHist(face_img_yuv[:,:,0])
                    face_img = cv2.cvtColor(face_img_yuv, cv2.COLOR_YUV2BGR)
                    face_analysis = DeepFace.analyze(
                        face_img,
                        actions=['emotion'],
                        enforce_detection=False,
                        detector_backend='opencv'
                    )
                    if face_analysis and len(face_analysis) > 0:
                        emotions = face_analysis[0]['emotion']
                        # Print emotions for debugging
                        print("Detected emotions:", emotions)
                        dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0]
                        confidence = emotions[dominant_emotion]
                        emoji = emotion_emojis.get(dominant_emotion.lower(), '')
                        emotion_text = f'Mood: {dominant_emotion.title()} {emoji} ({confidence:.1f}%)'
                        frame = draw_text_with_emoji(frame, emotion_text, (10, 70))
                    else:
                        dominant_emotion = "neutral"
                else:
                    dominant_emotion = "neutral"
            except Exception as e:
                print(f"Emotion detection error: {str(e)}")
                dominant_emotion = "neutral"

            if identified_person != "Unknown":
                cv2.putText(frame, f'{identified_person}', (x+5, y-20),
                           cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 2)
            else:
                cv2.putText(frame, 'Unknown', (x+5, y-20),
                           cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 0, 255), 2)

        cv2.putText(frame, 'Press ESC to mark attendance and exit', (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        timestamp = datetime.now().strftime("%H:%M:%S")
        cv2.putText(frame, timestamp, (frame.shape[1]-140, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow('Attendance System', frame)
        key = cv2.waitKey(1)
        if key == 27:  # ESC key
            if identified_person != "Unknown":
                add_attendance(identified_person, dominant_emotion)
            break

    cap.release()
    cv2.destroyAllWindows()
    names, rolls, times, moods, l = extract_attendance()
    return render_template('home.html', names=names, rolls=rolls, times=times, moods=moods, l=l, totalreg=totalreg(), datetoday2=datetoday2)

# Remove this incorrect block from start() function:
#    if i > 0:
#        print('Training Model')
#        try:
#            train_model()
#            flash('User added successfully!', 'success')
#        except Exception as e:
#            flash(f'Error training model: {str(e)}', 'error')
#    else:
#        # Remove the empty user folder if no images were captured
#        if os.path.exists(userimagefolder):
#            os.rmdir(userimagefolder)
#        flash('No images were captured. User not registered.', 'warning')
#
#    return redirect(url_for('home'))

# Modify the add_attendance function to include mood
def add_attendance(name, mood="Unknown"):
    if name == "Unknown":
        return
        
    username = name.split('_')[0]
    userid = name.split('_')[1]
    current_time = datetime.now().strftime("%H:%M:%S")

    df = pd.read_csv(f'Attendance/Attendance-{datetoday}.csv')
    if int(userid) not in list(df['Roll']):
        with open(f'Attendance/Attendance-{datetoday}.csv', 'a') as f:
            f.write(f'\n{username},{userid},{current_time},{mood}')

# Modify the CSV file creation to include the Mood column
if f'Attendance-{datetoday}.csv' not in os.listdir('Attendance'):
    with open(f'Attendance/Attendance-{datetoday}.csv', 'w') as f:
        f.write('Name,Roll,Time,Mood')

# Update the extract_attendance function to include mood



# A function to add a new user.
# This function will run when we add a new user.
# Add this new route
@app.route('/adduser')
def adduser():
    return render_template('add_user.html', totalreg=totalreg(), datetoday2=datetoday2)

# Update the existing add route to redirect after completion
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'GET':
        return redirect(url_for('adduser'))
        
    newusername = request.form['newusername']
    newuserid = request.form['newuserid']
    userimagefolder = f'static/faces/{newusername}_{newuserid}'

    os.makedirs(userimagefolder, exist_ok=True)

    i = 0
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        cap.open(0)

    # Set camera properties for better detection
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert to grayscale for better face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        # Draw rectangle for each detected face
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Display counter and instructions
            cv2.putText(frame, f'Images Captured: {i}/{nimgs}', (30, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 20), 2, cv2.LINE_AA)
            cv2.putText(frame, 'Press SPACE to capture', (30, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 20), 2, cv2.LINE_AA)
            cv2.putText(frame, 'Press ESC to exit', (30, 110),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 20), 2, cv2.LINE_AA)

        cv2.imshow('Adding new User', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == 32 and len(faces) > 0:  # SPACE key and face detected
            (x, y, w, h) = faces[0]  # Take first detected face
            name = f'{newusername}_{i}.jpg'
            face_img = frame[y:y+h, x:x+w]
            cv2.imwrite(f'{userimagefolder}/{name}', face_img)
            i += 1
            if i >= nimgs:
                break
        elif key == 27:  # ESC key
            break

    cap.release()
    cv2.destroyAllWindows()

    if i > 0:
        print('Training Model')
        try:
            train_model()
            flash('User added successfully!', 'success')
        except Exception as e:
            flash(f'Error training model: {str(e)}', 'error')
    else:
        flash('No images were captured', 'warning')

    return redirect(url_for('home'))

# Our main function which runs the Flask App
# Move these functions before if __name__ == '__main__':
def export_to_excel():
    df = pd.read_csv(f'Attendance/Attendance-{datetoday}.csv')
    excel_file = f'Attendance/Attendance-{datetoday}.xlsx'
    df.to_excel(excel_file, index=False)
    return excel_file

def send_email(recipient_email, file_path):
    sender_email = "deepalimenon2004@gmail.com"  # Replace with your email
    password = "kxdf jnvk zbyp wblc"  # Replace with your app password

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = f"Attendance Report - {datetoday2}"

    body = f"Please find attached the attendance report for {datetoday2}."
    msg.attach(MIMEText(body, 'plain'))

    with open(file_path, 'rb') as f:
        attachment = MIMEApplication(f.read(), _subtype='xlsx')
        attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file_path))
        msg.attach(attachment)

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, password)
        server.send_message(msg)

@app.route('/export_attendance', methods=['POST'])
def export_attendance():
    try:
        email = request.form.get('email')
        if not email:
            flash('Email address is required', 'error')
            return jsonify({'status': 'error', 'message': 'Email is required'})

        excel_file = export_to_excel()
        send_email(email, excel_file)
        flash('Attendance report sent successfully!', 'success')
        return jsonify({'status': 'success', 'message': 'Attendance report sent successfully!'})
    except Exception as e:
        flash(f'Failed to send attendance report: {str(e)}', 'error')
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/send_report', methods=['POST'])
def send_report():
    recipient_email = request.form.get('email')
    if not recipient_email:
        flash('Please provide an email address', 'error')
        return render_template('home.html', names=[], rolls=[], times=[], 
                             l=0, totalreg=totalreg(), datetoday2=datetoday2)
    
    if send_attendance_report(recipient_email):
        flash('Attendance report sent successfully!', 'success')
    else:
        flash('Failed to send attendance report', 'error')
    
    names, rolls, times, l = extract_attendance()
    return render_template('home.html', names=names, rolls=rolls, times=times, 
                         l=l, totalreg=totalreg(), datetoday2=datetoday2)

# Then put this at the end
if __name__ == '__main__':
    app.run(debug=True, port=5001)
