#!/bin/bash

# EC2 Deployment Script for Cloud Image Processing Platform
# Run this script on your EC2 instance to set up the application

set -e  # Exit on error

echo "=========================================="
echo "  EC2 Deployment Setup"
echo "  Cloud Image Processing Platform"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Update system packages
echo -e "${YELLOW}[1/8] Updating system packages...${NC}"
sudo apt-get update
sudo apt-get upgrade -y

# Install Python 3 and pip
echo ""
echo -e "${YELLOW}[2/8] Installing Python 3 and pip...${NC}"
sudo apt-get install -y python3 python3-pip python3-venv

# Install MongoDB
echo ""
echo -e "${YELLOW}[3/8] Installed MongoDB...${NC}"


# Install Nginx
echo ""
echo -e "${YELLOW}[4/8] Installing Nginx...${NC}"
sudo apt-get install -y nginx
sudo systemctl enable nginx
echo -e "${GREEN}✓ Nginx installed${NC}"

# Install AWS CLI
echo ""
echo -e "${YELLOW}[5/8] Installing AWS CLI...${NC}"
if ! command -v aws &> /dev/null; then
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    sudo apt-get install -y unzip
    unzip awscliv2.zip
    sudo ./aws/install
    rm -rf aws awscliv2.zip
    echo -e "${GREEN}✓ AWS CLI installed${NC}"
else
    echo -e "${GREEN}✓ AWS CLI already installed${NC}"
fi

# Create project directory
echo ""
echo -e "${YELLOW}[6/8] Setting up project directory...${NC}"


# Setup virtual environment for backend
echo ""
echo -e "${YELLOW}[7/8] Setting up Python virtual environment...${NC}"
cd $PROJECT_DIR/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo -e "${GREEN}✓ Virtual environment created and dependencies installed${NC}"

# Configure environment variables
echo ""
echo -e "${YELLOW}[8/8] Configuring environment variables...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${YELLOW}⚠ Please edit .env file with your AWS credentials and configuration${NC}"
    echo -e "${YELLOW}  Run: nano $PROJECT_DIR/backend/.env${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Setup systemd service
echo ""
echo -e "${YELLOW}Setting up systemd service...${NC}"
sudo cp $PROJECT_DIR/deployment/image-processor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable image-processor.service
echo -e "${GREEN}✓ Systemd service configured${NC}"

# Setup Nginx
echo ""
echo -e "${YELLOW}Setting up Nginx...${NC}"
sudo cp $PROJECT_DIR/deployment/nginx.conf /etc/nginx/sites-available/image-processor
sudo ln -sf /etc/nginx/sites-available/image-processor /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
echo -e "${GREEN}✓ Nginx configured${NC}"

# Create temp uploads directory
mkdir -p $PROJECT_DIR/backend/temp_uploads

echo ""
echo "=========================================="
echo -e "${GREEN}✓ Deployment setup complete!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Configure AWS credentials: aws configure"
echo "2. Edit environment file: nano $PROJECT_DIR/backend/.env"
echo "3. Update Nginx config with your domain: sudo nano /etc/nginx/sites-available/image-processor"
echo "4. Start the application: sudo systemctl start image-processor"
echo "5. Check status: sudo systemctl status image-processor"
echo ""
echo "Useful commands:"
echo "  - View logs: sudo journalctl -u image-processor -f"
echo "  - Restart service: sudo systemctl restart image-processor"
echo "  - Check Nginx: sudo nginx -t"
echo ""