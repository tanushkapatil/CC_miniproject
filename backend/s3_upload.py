"""
s3_upload.py
This module handles AWS S3 storage operations for the image processing platform.
It uploads both original and processed images to separate S3 folders.
"""

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import os

# AWS S3 Configuration
# NOTE: Replace these with your actual AWS credentials and bucket name
AWS_CONFIG = {
    'access_key': os.environ.get('AWS_ACCESS_KEY_ID', 'your-access-key'),
    'secret_key': os.environ.get('AWS_SECRET_ACCESS_KEY', 'your-secret-key'),
    'region': os.environ.get('AWS_REGION', 'us-east-1'),
    'bucket_name': os.environ.get('S3_BUCKET_NAME', 'your-bucket-name')
}

# S3 folder structure
ORIGINAL_FOLDER = "original-images/"
PROCESSED_FOLDER = "processed-images/"


def get_s3_client():
    """
    Creates and returns an AWS S3 client.
    
    Returns:
        boto3.client: S3 client object
        
    Raises:
        NoCredentialsError: If AWS credentials are not found
    """
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_CONFIG['access_key'],
            aws_secret_access_key=AWS_CONFIG['secret_key'],
            region_name=AWS_CONFIG['region']
        )
        print("✓ S3 client created successfully")
        return s3_client
    except NoCredentialsError:
        print("✗ AWS credentials not found")
        raise
    except Exception as e:
        print(f"✗ Error creating S3 client: {str(e)}")
        raise


def upload_to_s3(file_path, s3_key, content_type='image/jpeg'):
    """
    Uploads a file to AWS S3 bucket.
    
    Args:
        file_path (str): Local path to the file to upload
        s3_key (str): S3 key (path) where the file will be stored
        content_type (str): MIME type of the file (default: 'image/jpeg')
        
    Returns:
        str: Public URL of the uploaded file
        
    Raises:
        Exception: If upload fails
    """
    try:
        s3_client = get_s3_client()
        bucket_name = AWS_CONFIG['bucket_name']
        
        # Upload file to S3
        with open(file_path, 'rb') as file_data:
            s3_client.put_object(
                Bucket=bucket_name,
                Key=s3_key,
                Body=file_data,
                ContentType=content_type
            )
        
        # Generate the public URL
        file_url = f"https://{bucket_name}.s3.{AWS_CONFIG['region']}.amazonaws.com/{s3_key}"
        print(f"✓ File uploaded successfully to S3: {s3_key}")
        
        return file_url
        
    except FileNotFoundError:
        print(f"✗ File not found: {file_path}")
        raise
    except ClientError as e:
        print(f"✗ S3 upload error: {str(e)}")
        raise
    except Exception as e:
        print(f"✗ Unexpected error during upload: {str(e)}")
        raise


def upload_original_image(file_path, file_name):
    """
    Uploads an original (unprocessed) image to S3.
    
    Args:
        file_path (str): Local path to the original image
        file_name (str): Name of the image file
        
    Returns:
        str: Public URL of the uploaded original image
    """
    try:
        # S3 key for original image
        s3_key = f"{ORIGINAL_FOLDER}{file_name}"
        
        # Determine content type based on file extension
        content_type = get_content_type(file_name)
        
        # Upload to S3
        file_url = upload_to_s3(file_path, s3_key, content_type)
        print(f"✓ Original image uploaded: {file_name}")
        
        return file_url
        
    except Exception as e:
        print(f"✗ Error uploading original image: {str(e)}")
        raise


def upload_processed_image(file_path, file_name):
    """
    Uploads a processed image to S3.
    
    Args:
        file_path (str): Local path to the processed image
        file_name (str): Name of the image file
        
    Returns:
        str: Public URL of the uploaded processed image
    """
    try:
        # S3 key for processed image
        s3_key = f"{PROCESSED_FOLDER}{file_name}"
        
        # Determine content type based on file extension
        content_type = get_content_type(file_name)
        
        # Upload to S3
        file_url = upload_to_s3(file_path, s3_key, content_type)
        print(f"✓ Processed image uploaded: {file_name}")
        
        return file_url
        
    except Exception as e:
        print(f"✗ Error uploading processed image: {str(e)}")
        raise


def get_content_type(file_name):
    """
    Determines the MIME type based on file extension.
    
    Args:
        file_name (str): Name of the file
        
    Returns:
        str: MIME type of the file
    """
    extension = file_name.lower().split('.')[-1]
    
    content_types = {
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'bmp': 'image/bmp',
        'webp': 'image/webp'
    }
    
    return content_types.get(extension, 'application/octet-stream')


def delete_from_s3(s3_key):
    """
    Deletes a file from S3 bucket.
    
    Args:
        s3_key (str): S3 key (path) of the file to delete
        
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    try:
        s3_client = get_s3_client()
        bucket_name = AWS_CONFIG['bucket_name']
        
        s3_client.delete_object(
            Bucket=bucket_name,
            Key=s3_key
        )
        
        print(f"✓ File deleted from S3: {s3_key}")
        return True
        
    except Exception as e:
        print(f"✗ Error deleting from S3: {str(e)}")
        return False


def check_bucket_exists():
    """
    Checks if the configured S3 bucket exists.
    
    Returns:
        bool: True if bucket exists, False otherwise
    """
    try:
        s3_client = get_s3_client()
        bucket_name = AWS_CONFIG['bucket_name']
        
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"✓ S3 bucket exists: {bucket_name}")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            print(f"✗ S3 bucket does not exist: {bucket_name}")
        else:
            print(f"✗ Error checking bucket: {str(e)}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}")
        return False


# Test S3 connection when module is run directly
if __name__ == "__main__":
    print("Testing S3 connection...")
    check_bucket_exists()
