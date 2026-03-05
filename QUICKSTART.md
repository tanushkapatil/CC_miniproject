# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Setup Backend (2 minutes)

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
copy .env.example .env  # Windows
# OR
cp .env.example .env    # Linux/Mac

# Edit .env with your AWS credentials
notepad .env  # Windows
# OR
nano .env     # Linux/Mac
```

### Step 2: Start MongoDB (30 seconds)

Make sure MongoDB is running:

```bash
# Check if MongoDB is running
mongosh --eval "db.version()"

# If not running, start it:
# Windows: Start MongoDB service from Services
# Linux/Mac: sudo systemctl start mongod
```

### Step 3: Run the Application (30 seconds)

**Backend:**

```bash
# In backend folder with virtual environment activated
python app.py
```

**Frontend:**

```bash
# Open frontend/index.html in your browser
# OR use a local server:
cd frontend
python -m http.server 8000
# Then visit: http://localhost:8000
```

### Step 4: Test It! (1 minute)

1. Open the application in your browser
2. Click or drag-and-drop an image
3. Adjust processing options (optional)
4. Click "Process Image"
5. View the result and check the Gallery tab

## 📋 Requirements Checklist

Before starting, make sure you have:

- [ ] Python 3.8 or higher installed
- [ ] MongoDB installed and running
- [ ] AWS Account created
- [ ] AWS S3 bucket created
- [ ] AWS IAM user created with S3 access
- [ ] AWS credentials (Access Key ID and Secret Key)

## ⚙️ Minimal .env Configuration

```env
# Required AWS Settings
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name

# MongoDB (use defaults if running locally)
MONGODB_URI=mongodb://localhost:27017/
DB_NAME=image_storage

# Flask (use defaults for development)
FLASK_ENV=development
PORT=5000
HOST=0.0.0.0
```

## 🎯 Common Issues

**"ModuleNotFoundError"**

- Make sure virtual environment is activated
- Run: `pip install -r requirements.txt`

**"Connection refused" when uploading**

- Check if backend is running on port 5000
- Verify MongoDB is running

**"AWS credentials not found"**

- Ensure .env file exists in backend folder
- Check that AWS credentials are correct
- Try: `aws configure` to set up AWS CLI

**"Failed to connect to MongoDB"**

- Start MongoDB service
- Check if MongoDB is listening on port 27017

## 🌐 For EC2 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete EC2 deployment instructions.

Quick EC2 setup:

```bash
# On EC2 instance
cd ~/CC_miniproject/deployment
chmod +x deploy.sh
sudo ./deploy.sh
```

Then configure and start:

```bash
# Edit environment
nano ~/CC_miniproject/backend/.env

# Start service
sudo systemctl start image-processor
```

---

**Need help?** Check [README.md](README.md) or [DEPLOYMENT.md](DEPLOYMENT.md) for detailed documentation.
