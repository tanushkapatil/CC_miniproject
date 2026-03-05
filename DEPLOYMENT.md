# Cloud Image Processing Platform - Deployment Guide

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [AWS Setup](#aws-setup)
4. [EC2 Deployment](#ec2-deployment)
5. [Post-Deployment Configuration](#post-deployment-configuration)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Services

- **AWS Account** with:
  - EC2 instance (t2.micro or better)
  - S3 bucket for image storage
  - IAM user with S3 access
- **Domain name** (optional, but recommended)

### Local Requirements

- Python 3.8+
- MongoDB 4.0+
- Git

---

## Local Development Setup

### 1. Clone/Setup Project

```bash
cd CC_miniproject
```

### 2. Backend Setup

#### For Linux/Mac:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### For Windows:

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your settings
nano .env
```

Required environment variables:

```env
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your_bucket_name

MONGODB_URI=mongodb://localhost:27017/
DB_NAME=image_storage

FLASK_ENV=development
PORT=5000
HOST=0.0.0.0
```

### 4. Install MongoDB (if not installed)

#### Ubuntu/Debian:

```bash
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod
```

#### macOS:

```bash
brew tap mongodb/brew
brew install mongodb-community@6.0
brew services start mongodb-community@6.0
```

#### Windows:

Download from: https://www.mongodb.com/try/download/community

### 5. Start the Backend

#### Using start script (Linux/Mac):

```bash
chmod +x start.sh
./start.sh
```

#### Using start script (Windows):

```bash
start.bat
```

#### Or manually:

```bash
python app.py
```

Backend will run on: http://localhost:5000

### 6. Start the Frontend

Open `frontend/index.html` in your browser, or use a local server:

```bash
cd frontend
python -m http.server 8000
```

Then visit: http://localhost:8000

---

## AWS Setup

### 1. Create S3 Bucket

1. Go to AWS Console → S3
2. Click "Create bucket"
3. Configure:
   - **Bucket name**: `your-unique-bucket-name`
   - **Region**: Choose your preferred region
   - **Block Public Access**: Uncheck (we'll configure CORS)
   - Click "Create bucket"

4. Configure CORS:
   - Select your bucket
   - Go to "Permissions" tab
   - Scroll to "Cross-origin resource sharing (CORS)"
   - Add this configuration:

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

### 2. Create IAM User

1. Go to AWS Console → IAM
2. Click "Users" → "Add user"
3. Configure:
   - **User name**: `image-processor-app`
   - **Access type**: Programmatic access
4. Attach policy: `AmazonS3FullAccess` (or create custom policy)
5. Save the Access Key ID and Secret Access Key

### 3. Launch EC2 Instance

1. Go to AWS Console → EC2
2. Click "Launch Instance"
3. Configure:
   - **Name**: `image-processing-server`
   - **AMI**: Ubuntu Server 22.04 LTS
   - **Instance type**: t2.micro (or t2.small for better performance)
   - **Key pair**: Create or select existing
   - **Network settings**:
     - Allow SSH (port 22) from your IP
     - Allow HTTP (port 80) from anywhere
     - Allow HTTPS (port 443) from anywhere
4. Launch instance

5. Note your instance's Public IP address

---

## EC2 Deployment

### 1. Connect to EC2 Instance

```bash
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

### 2. Transfer Project Files

#### Option A: Using Git (Recommended)

```bash
# On EC2 instance
cd ~
git clone your-repository-url CC_miniproject
```

#### Option B: Using SCP

```bash
# From your local machine
scp -i your-key.pem -r CC_miniproject ubuntu@your-ec2-public-ip:~/
```

### 3. Run Deployment Script

```bash
cd ~/CC_miniproject/deployment
chmod +x deploy.sh
sudo ./deploy.sh
```

This script will:

- Update system packages
- Install Python 3, pip, MongoDB, Nginx, AWS CLI
- Set up virtual environment
- Install Python dependencies
- Configure systemd service
- Set up Nginx

### 4. Configure AWS Credentials

```bash
aws configure
```

Enter:

- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., us-east-1)
- Default output format: json

### 5. Configure Environment Variables

```bash
nano ~/CC_miniproject/backend/.env
```

Update with your actual values:

```env
AWS_ACCESS_KEY_ID=your_actual_key
AWS_SECRET_ACCESS_KEY=your_actual_secret
AWS_REGION=us-east-1
S3_BUCKET_NAME=your_actual_bucket_name

MONGODB_URI=mongodb://localhost:27017/
DB_NAME=image_storage

FLASK_ENV=production
FLASK_DEBUG=False
PORT=5000
HOST=0.0.0.0
```

### 6. Update Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/image-processor
```

Replace `your_domain.com` with your actual domain or EC2 public IP.

Test Nginx configuration:

```bash
sudo nginx -t
```

Reload Nginx:

```bash
sudo systemctl reload nginx
```

### 7. Start the Application

```bash
sudo systemctl start image-processor
sudo systemctl status image-processor
```

---

## Post-Deployment Configuration

### 1. Verify Services

Check backend status:

```bash
sudo systemctl status image-processor
```

Check Nginx status:

```bash
sudo systemctl status nginx
```

Check MongoDB status:

```bash
sudo systemctl status mongod
```

### 2. View Logs

Application logs:

```bash
sudo journalctl -u image-processor -f
```

Nginx logs:

```bash
sudo tail -f /var/log/nginx/image-processor-access.log
sudo tail -f /var/log/nginx/image-processor-error.log
```

### 3. Test the Application

Visit in your browser:

- `http://your-ec2-public-ip`
- Or `http://your-domain.com`

### 4. Optional: Set Up SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Certbot will automatically configure Nginx
# Test auto-renewal
sudo certbot renew --dry-run
```

---

## Troubleshooting

### Backend Not Starting

Check logs:

```bash
sudo journalctl -u image-processor -n 50
```

Common issues:

- **MongoDB not running**: `sudo systemctl start mongod`
- **Missing dependencies**: Reinstall with `pip install -r requirements.txt`
- **Permission issues**: Check file ownership `sudo chown -R ubuntu:ubuntu ~/CC_miniproject`

### Cannot Upload Images

1. Check S3 bucket permissions
2. Verify AWS credentials: `aws s3 ls s3://your-bucket-name`
3. Check CORS configuration on S3 bucket
4. Check Nginx upload size: `client_max_body_size` in nginx.conf

### Frontend Not Loading

1. Check Nginx configuration: `sudo nginx -t`
2. Verify file permissions: `ls -la ~/CC_miniproject/frontend/`
3. Check Nginx error logs: `sudo tail -f /var/log/nginx/error.log`

### Gallery Not Loading Images

1. Verify MongoDB is running: `sudo systemctl status mongod`
2. Check backend connection to MongoDB
3. Verify image URLs in database match S3 bucket
4. Check browser console for errors

### Service Management Commands

```bash
# Start service
sudo systemctl start image-processor

# Stop service
sudo systemctl stop image-processor

# Restart service
sudo systemctl restart image-processor

# Enable auto-start on boot
sudo systemctl enable image-processor

# Disable auto-start
sudo systemctl disable image-processor

# View service status
sudo systemctl status image-processor

# View service logs
sudo journalctl -u image-processor -f
```

---

## Security Best Practices

1. **Firewall Configuration**:

   ```bash
   sudo ufw allow 22/tcp   # SSH
   sudo ufw allow 80/tcp   # HTTP
   sudo ufw allow 443/tcp  # HTTPS
   sudo ufw enable
   ```

2. **Restrict SSH Access**:
   - Use EC2 Security Groups to limit SSH to your IP
   - Consider using AWS Systems Manager Session Manager

3. **Environment Variables**:
   - Never commit `.env` file to Git
   - Use AWS Secrets Manager for production

4. **Regular Updates**:

   ```bash
   sudo apt-get update
   sudo apt-get upgrade -y
   ```

5. **Backup Strategy**:
   - Regular MongoDB backups
   - S3 versioning enabled
   - EC2 AMI snapshots

---

## Updating the Application

### Update Code

```bash
cd ~/CC_miniproject
git pull origin main
```

### Restart Backend

```bash
sudo systemctl restart image-processor
```

### Reload Nginx (if frontend changed)

```bash
sudo systemctl reload nginx
```

---

## Monitoring & Maintenance

### Check Disk Space

```bash
df -h
```

### Check Memory Usage

```bash
free -h
```

### Check MongoDB Database Size

```bash
mongo image_storage --eval "db.stats()"
```

### Clean Temporary Files

```bash
cd ~/CC_miniproject/backend
rm -rf temp_uploads/*
```

---

## Support

For issues or questions:

1. Check application logs
2. Review this documentation
3. Check AWS service status
4. Verify all configuration files

---

**Congratulations! Your Cloud Image Processing Platform is now deployed!** 🎉
