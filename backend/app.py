"""
app.py
Main Flask application for Cloud-Based Image Processing and Storage Platform.
This server handles image uploads, processes them, stores them in S3, and saves metadata to MongoDB.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime

# Import our custom modules
import image_processor
import s3_upload
import database

# Initialize Flask application
app = Flask(__name__)

# Enable CORS to allow frontend requests
CORS(app, resources={r"/*": {"origins": "*"}})

# Configuration
UPLOAD_FOLDER = 'temp_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

# Create upload folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    print(f"✓ Created upload folder: {UPLOAD_FOLDER}")


def allowed_file(filename):
    """
    Checks if the uploaded file has an allowed extension.
    
    Args:
        filename (str): Name of the file
        
    Returns:
        bool: True if extension is allowed, False otherwise
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_unique_filename(original_filename):
    """
    Generates a unique filename to avoid conflicts.
    
    Args:
        original_filename (str): Original name of the file
        
    Returns:
        str: Unique filename with UUID prefix
    """
    # Get file extension
    extension = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'jpg'
    
    # Generate unique filename with timestamp and UUID
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    unique_filename = f"{timestamp}_{unique_id}.{extension}"
    
    return unique_filename


@app.route('/', methods=['GET'])
def home():
    """
    Home endpoint - provides basic API information.
    """
    return jsonify({
        'message': 'Cloud-Based Image Processing and Storage Platform API',
        'version': '1.0',
        'endpoints': {
            'upload': '/upload (POST)',
            'health': '/health (GET)'
        },
        'status': 'running'
    })


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint - verifies that the server is running.
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/upload', methods=['POST'])
def upload_image():
    """
    Main upload endpoint - handles image upload and processing.
    
    Accepts:
        - image file (multipart/form-data)
        - processing options (optional):
            - resize: bool (default: true)
            - compress: bool (default: true)
            - width: int (default: 800)
            - height: int (default: 600)
            - quality: int (default: 85)
    
    Returns:
        JSON response with:
            - status: success/error
            - image_url: URL of processed image in S3
            - processed_size: Size of processed image
            - metadata: Additional image information
    """
    try:
        # Step 1: Validate the request
        print("\n" + "="*50)
        print("📥 New image upload request received")
        print("="*50)
        
        # Check if file is present in the request
        if 'image' not in request.files:
            print("✗ No image file in request")
            return jsonify({
                'status': 'error',
                'message': 'No image file provided'
            }), 400
        
        file = request.files['image']
        
        # Check if file is selected
        if file.filename == '':
            print("✗ No file selected")
            return jsonify({
                'status': 'error',
                'message': 'No file selected'
            }), 400
        
        # Check if file type is allowed
        if not allowed_file(file.filename):
            print(f"✗ Invalid file type: {file.filename}")
            return jsonify({
                'status': 'error',
                'message': f'Invalid file type. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        print(f"✓ File validation passed: {file.filename}")
        
        # Step 2: Get processing options from request
        options = {
            'resize': request.form.get('resize', 'true').lower() == 'true',
            'compress': request.form.get('compress', 'true').lower() == 'true',
            'width': int(request.form.get('width', 800)),
            'height': int(request.form.get('height', 600)),
            'quality': int(request.form.get('quality', 85))
        }
        
        print(f"✓ Processing options: {options}")
        
        # Step 3: Save the uploaded file temporarily
        original_filename = secure_filename(file.filename)
        unique_filename = generate_unique_filename(original_filename)
        
        # Paths for temporary files
        temp_original_path = os.path.join(UPLOAD_FOLDER, f"original_{unique_filename}")
        temp_processed_path = os.path.join(UPLOAD_FOLDER, f"processed_{unique_filename}")
        
        # Save the uploaded file
        file.save(temp_original_path)
        print(f"✓ Original image saved temporarily: {temp_original_path}")
        
        # Step 4: Process the image
        print("\n🔄 Processing image...")
        process_result = image_processor.process_image(
            temp_original_path,
            temp_processed_path,
            options
        )
        
        if not process_result['success']:
            # Clean up temporary files
            if os.path.exists(temp_original_path):
                os.remove(temp_original_path)
            
            print(f"✗ Image processing failed: {process_result['message']}")
            return jsonify({
                'status': 'error',
                'message': process_result['message']
            }), 400
        
        print(f"✓ Image processing completed successfully")
        print(f"  Original size: {image_processor.format_size(process_result['original_size'])}")
        print(f"  Processed size: {image_processor.format_size(process_result['processed_size'])}")
        
        # Step 5: Upload images to S3
        print("\n☁️  Uploading to AWS S3...")
        
        try:
            # Upload original image
            original_s3_url = s3_upload.upload_original_image(temp_original_path, unique_filename)
            print(f"✓ Original image uploaded to S3")
            
            # Upload processed image
            processed_s3_url = s3_upload.upload_processed_image(temp_processed_path, unique_filename)
            print(f"✓ Processed image uploaded to S3")
            
        except Exception as e:
            # Clean up temporary files
            if os.path.exists(temp_original_path):
                os.remove(temp_original_path)
            if os.path.exists(temp_processed_path):
                os.remove(temp_processed_path)
            
            print(f"✗ S3 upload failed: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f'Failed to upload to S3: {str(e)}'
            }), 500
        
        # Step 6: Store metadata in database
        print("\n💾 Saving metadata to database...")
        
        try:
            image_id = database.insert_image_metadata(
                file_name=unique_filename,
                original_size=process_result['original_size'],
                processed_size=process_result['processed_size'],
                image_url=processed_s3_url
            )
            print(f"✓ Metadata saved to database (ID: {image_id})")
            
        except Exception as e:
            print(f"✗ Database error: {str(e)}")
            # Note: Images are already uploaded to S3, so we continue
            # In production, you might want to implement rollback
        
        # Step 7: Clean up temporary files
        try:
            if os.path.exists(temp_original_path):
                os.remove(temp_original_path)
            if os.path.exists(temp_processed_path):
                os.remove(temp_processed_path)
            print("✓ Temporary files cleaned up")
        except Exception as e:
            print(f"⚠️  Warning: Failed to clean up temporary files: {str(e)}")
        
        # Step 8: Prepare and send response
        print("\n" + "="*50)
        print("✅ Image processing completed successfully!")
        print("="*50 + "\n")
        
        response_data = {
            'status': 'success',
            'message': 'Image uploaded and processed successfully',
            'image_url': processed_s3_url,
            'original_url': original_s3_url,
            'processed_size': image_processor.format_size(process_result['processed_size']),
            'metadata': {
                'file_name': unique_filename,
                'original_file_name': original_filename,
                'category': process_result['category'],
                'original_size': image_processor.format_size(process_result['original_size']),
                'processed_size': image_processor.format_size(process_result['processed_size']),
                'upload_time': datetime.now().isoformat(),
                'processing_options': options
            }
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"\n✗ Unexpected error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }), 500


@app.route('/images', methods=['GET'])
def get_images():
    """
    Retrieves all uploaded images metadata from the database.
    
    Returns:
        JSON response with list of all images
    """
    try:
        images = database.get_all_images()
        
        # Format the response
        formatted_images = []
        for img in images:
            formatted_images.append({
                'id': img['id'],
                'file_name': img['file_name'],
                'original_size': image_processor.format_size(img['original_size']),
                'processed_size': image_processor.format_size(img['processed_size']),
                'upload_time': img['upload_time'].isoformat() if hasattr(img['upload_time'], 'isoformat') else str(img['upload_time']),
                'image_url': img['image_url']
            })
        
        return jsonify({
            'status': 'success',
            'count': len(formatted_images),
            'images': formatted_images
        }), 200
        
    except Exception as e:
        print(f"✗ Error retrieving images: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to retrieve images: {str(e)}'
        }), 500


@app.route('/image/<int:image_id>', methods=['GET'])
def get_image(image_id):
    """
    Retrieves metadata for a specific image by ID.
    
    Args:
        image_id (int): ID of the image
        
    Returns:
        JSON response with image metadata
    """
    try:
        image = database.get_image_metadata(image_id)
        
        if not image:
            return jsonify({
                'status': 'error',
                'message': 'Image not found'
            }), 404
        
        # Format the response
        formatted_image = {
            'id': image['id'],
            'file_name': image['file_name'],
            'original_size': image_processor.format_size(image['original_size']),
            'processed_size': image_processor.format_size(image['processed_size']),
            'upload_time': image['upload_time'].isoformat() if hasattr(image['upload_time'], 'isoformat') else str(image['upload_time']),
            'image_url': image['image_url']
        }
        
        return jsonify({
            'status': 'success',
            'image': formatted_image
        }), 200
        
    except Exception as e:
        print(f"✗ Error retrieving image: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to retrieve image: {str(e)}'
        }), 500


# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500


# Main entry point
if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Cloud-Based Image Processing and Storage Platform")
    print("="*60)
    print("\n📋 Initializing server components...")
    
    # Initialize database collection
    try:
        database.create_images_collection()
        print("✓ Database initialized")
    except Exception as e:
        print(f"⚠️  Warning: Database initialization failed: {str(e)}")
        print("   Please ensure MongoDB is running on localhost:27017")
    
    # Check S3 connection
    try:
        s3_upload.check_bucket_exists()
        print("✓ S3 connection verified")
    except Exception as e:
        print(f"⚠️  Warning: S3 connection failed: {str(e)}")
        print("   Please ensure AWS credentials are configured correctly")
    
    print("\n" + "="*60)
    print("✅ Server starting on http://0.0.0.0:5000")
    print("="*60)
    print("\n📌 Available endpoints:")
    print("   GET  /           - API information")
    print("   GET  /health     - Health check")
    print("   POST /upload     - Upload and process image")
    print("   GET  /images     - Get all images")
    print("   GET  /image/<id> - Get specific image metadata")
    print("\n💡 Press CTRL+C to stop the server\n")
    
    # Run the Flask application
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
