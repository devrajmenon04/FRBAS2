# FRBAS2 - Deployment Guide

Complete guide for deploying the Facial Recognition Based Attendance System (FRBAS2).

## Table of Contents

1. [Local Development](#local-development)
2. [Windows Production](#windows-production)
3. [Linux/Ubuntu Production](#linuxubuntu-production)
4. [Docker Deployment](#docker-deployment)
5. [Cloud Deployment](#cloud-deployment)
6. [SSL/HTTPS Setup](#ssltls-setup)
7. [Performance Optimization](#performance-optimization)
8. [Troubleshooting](#troubleshooting)

---

## Local Development

### Prerequisites
- Python 3.8 or higher
- Git
- Webcam/Camera
- 4GB RAM minimum

### Step-by-Step Setup

#### 1. Clone Repository
```bash
git clone https://github.com/devrajmenon04/FRBAS2.git
cd FRBAS2
```

#### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
# On Windows: notepad .env
# On Linux/macOS: nano .env
```

#### 5. Run Application
```bash
python app.py
```

#### 6. Access Application
Open browser: `http://localhost:5001`

### Development Tips
- Use Flask debug mode (already enabled in app.py)
- Auto-reload on file changes
- Check console for error messages
- Use browser developer tools (F12) for frontend debugging

---

## Windows Production

### Prerequisites
- Windows 10/11
- Python 3.10+
- Administrator privileges

### Step-by-Step Setup

#### 1. Install Python
- Download from [python.org](https://www.python.org/)
- Check "Add Python to PATH" during installation
- Verify: `python --version`

#### 2. Clone Repository
```bash
git clone https://github.com/devrajmenon04/FRBAS2.git
cd FRBAS2
```

#### 3. Setup Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate
```

#### 4. Install Dependencies
```bash
pip install -r requirements.txt
pip install gunicorn
```

#### 5. Create Batch Script (`run.bat`)
```batch
@echo off
cd /d %~dp0
call venv\Scripts\activate.bat
python app.py
pause
```

#### 6. Setup as Windows Service (Using NSSM)

Download NSSM from [nssm.cc](https://nssm.cc/download)

```bash
# Extract NSSM
nssm install FRBAS2 "C:\path\to\FRBAS2\venv\Scripts\python.exe" "C:\path\to\FRBAS2\app.py"

# Start service
nssm start FRBAS2

# Stop service
nssm stop FRBAS2

# Remove service
nssm remove FRBAS2 confirm
```

#### 7. Setup Automatic Startup
- Create shortcut to `run.bat`
- Move to Startup folder: `C:\Users\YourUsername\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup`

#### 8. Configure Firewall
```bash
# Allow port 5001 through Windows Firewall
netsh advfirewall firewall add rule name="FRBAS2" dir=in action=allow protocol=tcp localport=5001
```

### Windows Service Management
```bash
# View all services
sc query

# Check FRBAS2 status
nssm status FRBAS2

# View logs
nssm get FRBAS2 AppStdout
```

---

## Linux/Ubuntu Production

### Prerequisites
- Ubuntu 18.04 LTS or higher
- Python 3.8+
- Sudo access

### Step-by-Step Setup

#### 1. Update System
```bash
sudo apt-get update
sudo apt-get upgrade -y
```

#### 2. Install System Dependencies
```bash
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    git \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libglib2.0-0 \
    libgl1-mesa-glx
```

#### 3. Clone Repository
```bash
cd /opt
sudo git clone https://github.com/devrajmenon04/FRBAS2.git
cd FRBAS2
sudo chown -R $USER:$USER .
```

#### 4. Setup Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 5. Install Dependencies
```bash
pip install -r requirements.txt
pip install gunicorn supervisor
```

#### 6. Create Systemd Service (`/etc/systemd/system/frbas2.service`)
```ini
[Unit]
Description=FRBAS2 Attendance System
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/FRBAS2
ExecStart=/opt/FRBAS2/venv/bin/gunicorn -w 4 -b 0.0.0.0:5001 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 7. Enable and Start Service
```bash
# Reload systemd daemon
sudo systemctl daemon-reload

# Enable on boot
sudo systemctl enable frbas2

# Start service
sudo systemctl start frbas2

# Check status
sudo systemctl status frbas2

# View logs
sudo journalctl -u frbas2 -f
```

#### 8. Setup Nginx Reverse Proxy
```bash
sudo apt-get install -y nginx
```

**Edit `/etc/nginx/sites-available/frbas2`:**
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/frbas2 /etc/nginx/sites-enabled/

# Test config
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

#### 9. Configure Webcam Access
```bash
# Add www-data to video group
sudo usermod -aG video www-data

# Verify permissions
ls -l /dev/video0
```

---

## Docker Deployment

### Prerequisites
- Docker installed ([docker.com](https://www.docker.com/))
- Docker Compose
- Webcam access

### Quick Start
```bash
# Clone repository
git clone https://github.com/devrajmenon04/FRBAS2.git
cd FRBAS2

# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop container
docker-compose down
```

### Docker Commands
```bash
# Build image
docker build -t frbas2:latest .

# Run container
docker run -d \
    --name frbas2 \
    --device /dev/video0:/dev/video0 \
    -p 5001:5001 \
    -v $(pwd)/Attendance:/app/Attendance \
    -v $(pwd)/static:/app/static \
    frbas2:latest

# View logs
docker logs -f frbas2

# Stop container
docker stop frbas2

# Remove container
docker rm frbas2
```

### Docker on Windows/Mac
Note: Direct camera access may have limitations. For best results:
1. Use Linux with native Docker
2. Use Docker Desktop with WSL2 (Windows)
3. Consider web-based camera streaming as alternative

---

## Cloud Deployment

### AWS Deployment

#### 1. Create EC2 Instance
- AMI: Ubuntu 20.04 LTS
- Instance type: t3.medium or higher
- Storage: 20GB+
- Security group: Allow ports 80, 443, 5001

#### 2. SSH into Instance
```bash
ssh -i your-key.pem ubuntu@your-instance-ip
```

#### 3. Follow Linux/Ubuntu Production Setup (above)

#### 4. Optional: Setup RDS for Database
```bash
# Connection string in .env
DATABASE_URL=postgresql://user:password@rds-endpoint:5432/frbas2
```

#### 5. Configure Load Balancer
- Application Load Balancer → Target Group → EC2 instance

### Google Cloud Deployment

#### 1. Create Compute Engine Instance
- Image: Ubuntu 20.04 LTS
- Machine type: n1-standard-2 or higher
- Allow HTTP/HTTPS traffic

#### 2. Connect to Instance
```bash
gcloud compute ssh instance-name --zone=your-zone
```

#### 3. Follow Linux/Ubuntu Production Setup

#### 4. Configure Cloud Load Balancer
- Backend service → Instance group → Compute instances

### Azure Deployment

#### 1. Create Virtual Machine
- Image: Ubuntu 20.04 LTS
- Size: Standard_B2s or higher
- Add public IP

#### 2. Connect via SSH
```bash
ssh azureuser@your-vm-ip
```

#### 3. Follow Linux/Ubuntu Production Setup

#### 4. Configure Application Gateway
- Backend pools → HTTP settings → Compute instance

---

## SSL/TLS Setup

### Using Let's Encrypt with Certbot

#### 1. Install Certbot
```bash
sudo apt-get install -y certbot python3-certbot-nginx
```

#### 2. Generate Certificate
```bash
sudo certbot certonly --standalone -d your-domain.com
```

#### 3. Configure Nginx for HTTPS
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

#### 4. Auto-renewal
```bash
# Automatic renewal via systemd timer (already configured)
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

---

## Performance Optimization

### 1. Gunicorn Configuration
```bash
# workers = 2 * CPU_cores + 1
gunicorn -w 5 -b 0.0.0.0:5001 --timeout 120 app:app
```

### 2. Reduce Face Detection Frequency
```python
# In app.py, adjust:
face_detect_interval = 10  # Detect every 10 frames instead of 5
```

### 3. Camera Resolution Optimization
```python
# Lower resolution for faster processing
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
```

### 4. Database Optimization
```sql
-- Add indexes to attendance table
CREATE INDEX idx_roll ON attendance(roll);
CREATE INDEX idx_date ON attendance(date);
```

### 5. Nginx Caching
```nginx
# Cache static files
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

### 6. Enable Gzip Compression
```nginx
gzip on;
gzip_types text/plain text/css text/js text/xml 
           text/javascript application/javascript 
           application/xml+rss application/json;
```

---

## Troubleshooting

### Issue: Camera Not Accessible
```bash
# Check camera device
ls -l /dev/video0

# Grant permissions
sudo chmod 666 /dev/video0

# Or add user to video group
sudo usermod -aG video $USER
newgrp video
```

### Issue: Port Already in Use
```bash
# Find process on port 5001
lsof -i :5001

# Kill process
kill -9 <PID>

# Or use different port
python app.py --port 5002
```

### Issue: Out of Memory
```bash
# Check memory usage
free -h

# Reduce workers
gunicorn -w 2 -b 0.0.0.0:5001 app:app

# Reduce frame buffer
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
```

### Issue: Slow Face Recognition
```bash
# Increase face detection interval
face_detect_interval = 15

# Reduce resolution
CAMERA_WIDTH=640
CAMERA_HEIGHT=480

# Use GPU (requires CUDA setup)
```

### Issue: Email Not Sending
```bash
# Check credentials in .env
cat .env | grep SMTP

# Test SMTP connection
python -c "import smtplib; smtplib.SMTP('smtp.gmail.com', 587).starttls()"

# Enable Less Secure Apps if needed (Gmail)
# https://myaccount.google.com/lesssecureapps
```

### View Application Logs
```bash
# Docker
docker-compose logs -f frbas2

# Systemd
sudo journalctl -u frbas2 -f

# Application
tail -f nohup.out  # If running with nohup
```

---

## Monitoring & Maintenance

### Health Check Script
```bash
#!/bin/bash
if ! curl -f http://localhost:5001 > /dev/null 2>&1; then
    echo "Service down at $(date)"
    # Restart service
    systemctl restart frbas2
fi
```

### Backup Attendance Data
```bash
# Daily backup
0 2 * * * tar -czf /backups/attendance-$(date +\%Y\%m\%d).tar.gz Attendance/
```

### Monitor Disk Space
```bash
# Check disk usage
df -h

# Clean old attendance files (keep 30 days)
find Attendance/ -name "*.csv" -mtime +30 -delete
```

---

## Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [OpenCV Documentation](https://opencv.org/)
- [Gunicorn Documentation](https://gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Docker Documentation](https://docs.docker.com/)

---

**Last Updated**: April 2026
