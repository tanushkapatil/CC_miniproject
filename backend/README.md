# Cloud-Based Image Processing and Storage Platform - Backend

A Flask-based backend server for processing images and storing them in AWS S3 with MongoDB database integration.

## 🎯 Project Overview

This backend system provides a complete solution for:

- Accepting image uploads from frontend
- Processing images (resize, compress)
- Storing images in AWS S3
- Saving metadata in MongoDB database (local)
- Providing RESTful API endpoints

## 📁 Project Structure

```
backend/
│
├── app.py                  # Main Flask application server
├── image_processor.py      # Image processing logic (Pillow)
├── database.py            # MongoDB database operations (pymongo)
├── s3_upload.py           # AWS S3 upload functionality (boto3)
├── requirements.txt       # Python dependencies
└── temp_uploads/          # Temporary storage (auto-created)
```

## 🚀 Setup Instructions

### Prerequisites

1. **Python 3.8 or higher**
2. **AWS Account** with:
   - S3 bucket created
   - IAM user with S3 access permissions
   - Access Key ID and Secret Access Key
3. **MongoDB** (local):
   - MongoDB installed and running on localhost:27017
   - No authentication required for local development

### Step 1: Install Python Dependencies

Navigate to the backend folder and install required packages:

```bash
cd backend
pip install -r requirements.txt
```

**Required packages:**

- flask - Web framework
- flask-cors - CORS support for frontend
- Pillow - Image processing
- boto3 - AWS S3 integration
- pymongo - MongoDB database connector
- werkzeug - File handling utilities
- python-dotenv - Environment variable management

### Step 2: Configure AWS Credentials

**Option A: Environment Variables (Recommended)**

Create a `.env` file in the backend folder:

```env
# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name

# MongoDB Database Configuration
MONGODB_URI=mongodb://localhost:27017/
DB_NAME=image_storage
```

**Option B: Modify Configuration Files**

Edit the configuration in each file:

**s3_upload.py** (lines 13-18):

```python
AWS_CONFIG = {
    'access_key': 'your-access-key-id',
    'secret_key': 'your-secret-access-key',
    'region': 'us-east-1',
    'bucket_name': 'your-bucket-name'
}
```

**database.py** (lines 12-14):

```python
MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
DB_NAME = os.environ.get('DB_NAME', 'image_storage')
```

### Step 3: Set Up AWS S3 Bucket

1. **Create an S3 bucket** in AWS Console
2. **Configure bucket permissions**:
   - Enable public read access for uploaded images
   - Add CORS configuration if needed

**Sample CORS Configuration for S3:**

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

3. **Create IAM policy** for S3 access:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:PutObject", "s3:GetObject", "s3:DeleteObject"],
      "Resource": "arn:aws:s3:::your-bucket-name/*"
    }
  ]
}
```

### Step 4: Set Up MongoDB Database

1. **Install MongoDB** (if not already installed):
   - Download from: https://www.mongodb.com/try/download/community
   - Or use package manager:
     - Windows: `choco install mongodb`
     - Mac: `brew install mongodb-community`
     - Linux: `sudo apt-get install mongodb`

2. **Start MongoDB service**:
   - Windows: `net start MongoDB`
   - Mac/Linux: `sudo systemctl start mongod` or `brew services start mongodb-community`

3. **Initialize database collection**:

```bash
python database.py
```

This will create the `images` collection with automatic indexing on `upload_time` and `file_name` fields.

**Document structure:**

```json
{
  "_id": "ObjectId(...)",
  "file_name": "image.jpg",
  "original_size": 1234567,
  "processed_size": 654321,
  "upload_time": "2026-03-04T10:30:00",
  "image_url": "https://s3.amazonaws.com/..."
}
```

### Step 5: Run the Server

Start the Flask development server:

```bash
python app.py
```

The server will start on: **http://0.0.0.0:5000**

You should see output like:

```
🚀 Cloud-Based Image Processing and Storage Platform
✓ Database initialized
✓ S3 connection verified
✅ Server starting on http://0.0.0.0:5000
```

## 📡 API Endpoints

### 1. Home / API Info

**GET** `/`

Returns basic API information and available endpoints.

**Response:**

```json
{
    "message": "Cloud-Based Image Processing and Storage Platform API",
    "version": "1.0",
    "endpoints": {...},
    "status": "running"
}
```

### 2. Health Check

**GET** `/health`

Checks if the server is running.

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2026-03-04T10:30:00"
}
```

### 3. Upload Image

**POST** `/upload`

Uploads and processes an image.

**Request:**

- Content-Type: `multipart/form-data`
- Form fields:
  - `image` (file, required) - Image file to upload
  - `resize` (string, optional) - "true" or "false" (default: "true")
  - `compress` (string, optional) - "true" or "false" (default: "true")
  - `width` (int, optional) - Target width in pixels (default: 800)
  - `height` (int, optional) - Target height in pixels (default: 600)
  - `quality` (int, optional) - JPEG quality 1-100 (default: 85)

**Response:**

```json
{
    "status": "success",
    "message": "Image uploaded and processed successfully",
    "image_url": "https://bucket-name.s3.amazonaws.com/processed-images/image.jpg",
    "original_url": "https://bucket-name.s3.amazonaws.com/original-images/image.jpg",
    "processed_size": "450.23KB",
    "metadata": {
        "file_name": "20260304_a1b2c3d4.jpg",
        "original_file_name": "vacation.jpg",
        "category": "JPEG",
        "original_size": "1.2MB",
        "processed_size": "450.23KB",
        "upload_time": "2026-03-04T10:30:00",
        "processing_options": {...}
    }
}
```

### 4. Get All Images

**GET** `/images`

Retrieves metadata for all uploaded images.

**Response:**

```json
{
    "status": "success",
    "count": 5,
    "images": [...]
}
```

### 5. Get Image by ID

**GET** `/image/<id>`

Retrieves metadata for a specific image.

**Response:**

```json
{
  "status": "success",
  "image": {
    "id": 1,
    "file_name": "20260304_a1b2c3d4.jpg",
    "original_size": "1.2MB",
    "processed_size": "450.23KB",
    "upload_time": "2026-03-04T10:30:00",
    "image_url": "https://..."
  }
}
```

## 🧪 Testing the API

### Using cURL

**Upload an image:**

```bash
curl -X POST http://localhost:5000/upload \
  -F "image=@path/to/image.jpg" \
  -F "resize=true" \
  -F "compress=true" \
  -F "width=800" \
  -F "height=600"
```

**Get all images:**

```bash
curl http://localhost:5000/images
```

### Using Postman

1. Create a new POST request to `http://localhost:5000/upload`
2. Select Body → form-data
3. Add key `image` with type `File` and select an image
4. Add other optional parameters (resize, compress, etc.)
5. Send the request

## 📦 S3 Bucket Structure

After uploading images, your S3 bucket will have this structure:

```
your-bucket-name/
├── original-images/
│   ├── 20260304_a1b2c3d4.jpg
│   ├── 20260304_e5f6g7h8.png
│   └── ...
└── processed-images/
    ├── 20260304_a1b2c3d4.jpg
    ├── 20260304_e5f6g7h8.png
    └── ...
```

## 🔧 Troubleshooting

### Database Connection Issues

**Error:** `Database connection failed`

**Solutions:**

1. Verify MongoDB is running (check with `mongo --version` or `mongosh`)
2. Check MongoDB service status
3. Ensure MongoDB is listening on localhost:27017
4. Check connection string in .env file

### S3 Upload Issues

**Error:** `S3 upload failed`

**Solutions:**

1. Verify AWS credentials are correct
2. Check S3 bucket exists and is accessible
3. Verify IAM permissions for S3 operations
4. Check bucket region matches configuration

### Image Processing Issues

**Error:** `Invalid image` or `Processing error`

**Solutions:**

1. Ensure file is a valid image format
2. Check file size (max 10MB by default)
3. Verify Pillow is installed correctly
4. Check file permissions

### CORS Issues

**Error:** `CORS policy blocked`

**Solution:**

- CORS is enabled by default in the Flask app
- For production, update CORS settings in app.py:

```python
CORS(app, resources={r"/*": {"origins": "https://your-frontend-domain.com"}})
```

## 🔐 Security Considerations

### For Production Deployment:

1. **Never commit credentials to version control**
   - Use environment variables or AWS Secrets Manager
   - Add `.env` to `.gitignore`

2. **Restrict CORS origins**
   - Change from `"*"` to specific frontend domain

3. **Use HTTPS**
   - Deploy behind a reverse proxy (Nginx)
   - Use SSL certificates

4. **File validation**
   - Implement file size limits
   - Validate file types thoroughly
   - Scan for malware

5. **Database security**
   - Use parameterized queries (already implemented with pymongo)
   - Enable MongoDB authentication for production
   - Use firewalls to restrict database access

6. **S3 security**
   - Use presigned URLs instead of public read
   - Enable S3 bucket versioning
   - Set up lifecycle policies

## 📝 Environment Variables

Create a `.env` file with these variables:

```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True

# AWS Configuration
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name

# Database Configuration
MONGODB_URI=mongodb://localhost:27017/
DB_NAME=image_storage
DB_PORT=3306

# Application Configuration
MAX_FILE_SIZE=10485760
UPLOAD_FOLDER=temp_uploads
```

To use environment variables, install python-dotenv and add to app.py:

```python
from dotenv import load_dotenv
load_dotenv()
```

## 🎓 College Project Notes

This project demonstrates:

- ✅ Cloud storage integration (AWS S3)
- ✅ Database management (MongoDB)
- ✅ RESTful API design
- ✅ Image processing techniques
- ✅ File handling and validation
- ✅ Error handling and logging
- ✅ CORS and web security basics

**Recommended Improvements:**

- Add user authentication (JWT tokens)
- Implement rate limiting
- Add image format conversion
- Create thumbnail generation
- Add batch upload support
- Implement image gallery pagination
- Add download functionality

## 📚 Dependencies Documentation

- **Flask**: https://flask.palletsprojects.com/
- **Pillow**: https://pillow.readthedocs.io/
- **Boto3**: https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
- **PyMySQL**: https://pymysql.readthedocs.io/

## 🤝 Support

For issues or questions:

1. Check error messages in console
2. Review configuration settings
3. Verify AWS and database credentials
4. Test endpoints individually

## 📄 License

This project is created for educational purposes as a cloud computing mini project.

---

**Created for:** Cloud Computing Mini Project  
**Technology Stack:** Python, Flask, AWS S3, MySQL, Pillow  
**Last Updated:** March 2026
