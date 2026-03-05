# Cloud Image Processing Platform

A modern, cloud-based image processing platform that allows users to upload, process, and store images with AWS S3 integration and MongoDB database.

## ✨ Features

- **Modern UI**: Clean, responsive interface with drag-and-drop support
- **Image Processing**:
  - Resize images to custom dimensions
  - Compress images with adjustable quality
  - Automatic image categorization
- **Cloud Storage**: AWS S3 integration for secure image storage
- **Gallery View**: Browse all uploaded and processed images
- **Real-time Processing**: Live progress indicators and success notifications
- **Download Support**: Download processed images directly from the gallery

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- MongoDB 4.0+
- AWS Account with S3 access
- AWS CLI configured

### Local Development

1. **Clone the repository**

   ```bash
   cd CC_miniproject
   ```

2. **Setup Backend**

   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your AWS credentials
   ```

3. **Start MongoDB**

   ```bash
   # Make sure MongoDB is running on localhost:27017
   mongod
   ```

4. **Run Backend**

   ```bash
   # Linux/Mac
   ./start.sh

   # Windows
   start.bat

   # Or manually
   python app.py
   ```

5. **Open Frontend**
   - Open `frontend/index.html` in your browser
   - Or use a local server: `python -m http.server 8000`

## 📦 Project Structure

```
CC_miniproject/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── database.py            # MongoDB operations
│   ├── image_processor.py     # Image processing logic
│   ├── s3_upload.py          # AWS S3 integration
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example          # Environment variables template
│   ├── start.sh              # Linux/Mac start script
│   └── start.bat             # Windows start script
├── frontend/
│   ├── index.html            # Main HTML file
│   ├── style.css             # Styling
│   └── script.js             # Frontend logic
├── deployment/
│   ├── deploy.sh             # EC2 deployment script
│   ├── image-processor.service  # Systemd service file
│   └── nginx.conf            # Nginx configuration
├── DEPLOYMENT.md             # Complete deployment guide
└── README.md                 # This file
```

## 🌐 EC2 Deployment

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)

### Quick Deploy

1. **Launch EC2 Instance** (Ubuntu 22.04 LTS)

2. **Transfer files to EC2**

   ```bash
   scp -i your-key.pem -r CC_miniproject ubuntu@your-ec2-ip:~/
   ```

3. **Run deployment script**

   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   cd ~/CC_miniproject/deployment
   chmod +x deploy.sh
   sudo ./deploy.sh
   ```

4. **Configure environment**

   ```bash
   nano ~/CC_miniproject/backend/.env
   # Add your AWS credentials and settings
   ```

5. **Start the service**

   ```bash
   sudo systemctl start image-processor
   ```

6. **Access your application**
   - Visit `http://your-ec2-public-ip`

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `backend` directory:

```env
# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your_bucket_name

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/
DB_NAME=image_storage

# Flask Configuration
FLASK_ENV=production
PORT=5000
HOST=0.0.0.0
```

### AWS S3 Setup

1. Create an S3 bucket
2. Configure CORS policy:
   ```json
   [
     {
       "AllowedHeaders": ["*"],
       "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
       "AllowedOrigins": ["*"],
       "ExposeHeaders": []
     }
   ]
   ```
3. Create IAM user with S3 access
4. Save credentials in `.env` file

## 🛠️ Technology Stack

### Backend

- **Flask**: Web framework
- **Pillow**: Image processing
- **boto3**: AWS S3 integration
- **pymongo**: MongoDB driver

### Frontend

- **HTML5/CSS3**: Structure and styling
- **JavaScript (ES6+)**: Interactivity
- **Custom fonts**: Darker Grotesque, Outfit

### Infrastructure

- **AWS S3**: Image storage
- **MongoDB**: Metadata storage
- **Nginx**: Reverse proxy
- **Systemd**: Service management

## 📊 API Endpoints

### `GET /`

Health check and API information

### `POST /upload`

Upload and process an image

**Form Data:**

- `image`: Image file (required)
- `resize`: Boolean (default: true)
- `compress`: Boolean (default: true)
- `width`: Integer (default: 800)
- `height`: Integer (default: 600)
- `quality`: Integer (default: 85)

**Response:**

```json
{
  "status": "success",
  "message": "Image uploaded and processed successfully",
  "image_url": "https://...",
  "original_url": "https://...",
  "processed_size": "245.6 KB",
  "metadata": {
    "file_name": "...",
    "category": "JPEG",
    "original_size": "1.2 MB",
    "processed_size": "245.6 KB",
    "upload_time": "2026-03-04T10:30:00"
  }
}
```

### `GET /images`

Get all uploaded images

### `GET /image/<id>`

Get specific image metadata

### `GET /health`

Health check endpoint

## 🎨 UI Features

- **Drag & Drop**: Intuitive file upload
- **Live Preview**: See image before processing
- **Processing Options**: Customize resize and compression
- **Progress Indicators**: Visual feedback during processing
- **Gallery View**: Browse all processed images
- **Image Details**: View metadata and download
- **Responsive Design**: Works on all devices
- **Error Handling**: User-friendly error messages

## 🔍 Troubleshooting

### Backend Issues

**Port already in use:**

```bash
# Find and kill process using port 5000
lsof -i :5000
kill -9 <PID>
```

**MongoDB connection failed:**

```bash
# Check MongoDB status
sudo systemctl status mongod

# Start MongoDB
sudo systemctl start mongod
```

**AWS S3 upload failed:**

- Verify AWS credentials
- Check S3 bucket permissions
- Test connection: `aws s3 ls s3://your-bucket-name`

### Frontend Issues

**Cannot connect to backend:**

- Ensure backend is running
- Check CORS configuration
- Verify API_URL in script.js

**Images not loading in gallery:**

- Check browser console for errors
- Verify S3 URLs are publicly accessible
- Check CORS policy on S3 bucket

## 📝 Development

### Running Tests

```bash
cd backend
python -m pytest tests/
```

### Code Style

```bash
# Format code
black app.py

# Check linting
pylint app.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available for educational purposes.

## 🙏 Acknowledgments

- Flask documentation
- AWS SDK documentation
- MongoDB documentation
- Google Fonts

---

**Made with ❤️ for cloud computing enthusiasts**
