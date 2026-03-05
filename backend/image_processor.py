"""
image_processor.py
This module handles image processing operations using the Pillow (PIL) library.
It resizes, compresses, and categorizes images based on processing options.
"""

from PIL import Image
import os

# Default image processing settings
DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600
COMPRESSION_QUALITY = 85  # JPEG quality (1-100, higher is better)


def get_image_size(file_path):
    """
    Gets the file size in bytes.
    
    Args:
        file_path (str): Path to the image file
        
    Returns:
        int: File size in bytes
    """
    try:
        return os.path.getsize(file_path)
    except Exception as e:
        print(f"✗ Error getting file size: {str(e)}")
        return 0


def get_image_category(file_path):
    """
    Categorizes the image based on its file type.
    
    Args:
        file_path (str): Path to the image file
        
    Returns:
        str: Category of the image (JPEG, PNG, etc.)
    """
    try:
        with Image.open(file_path) as img:
            return img.format
    except Exception as e:
        print(f"✗ Error categorizing image: {str(e)}")
        return "Unknown"


def validate_image(file_path):
    """
    Validates if the file is a valid image.
    
    Args:
        file_path (str): Path to the image file
        
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        # Try to open the image
        with Image.open(file_path) as img:
            img.verify()  # Verify that it's a valid image
        
        # Re-open the image (verify() closes it)
        with Image.open(file_path) as img:
            # Check if it's a supported format
            supported_formats = ['JPEG', 'PNG', 'GIF', 'BMP', 'WEBP']
            if img.format not in supported_formats:
                return False, f"Unsupported image format: {img.format}"
            
            # Check image dimensions (not too large)
            width, height = img.size
            if width > 10000 or height > 10000:
                return False, "Image dimensions too large (max 10000x10000)"
        
        print(f"✓ Image validation successful: {file_path}")
        return True, None
        
    except Exception as e:
        print(f"✗ Image validation failed: {str(e)}")
        return False, str(e)


def resize_image(input_path, output_path, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT):
    """
    Resizes an image to the specified dimensions.
    
    Args:
        input_path (str): Path to the input image
        output_path (str): Path where the resized image will be saved
        width (int): Target width (default: 800)
        height (int): Target height (default: 600)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with Image.open(input_path) as img:
            # Convert RGBA images to RGB (for JPEG compatibility)
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create a white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Resize the image using LANCZOS resampling for better quality
            resized_img = img.resize((width, height), Image.Resampling.LANCZOS)
            
            # Save the resized image
            resized_img.save(output_path, quality=95, optimize=False)
            
        print(f"✓ Image resized to {width}x{height}: {output_path}")
        return True
        
    except Exception as e:
        print(f"✗ Error resizing image: {str(e)}")
        return False


def compress_image(input_path, output_path, quality=COMPRESSION_QUALITY):
    """
    Compresses an image to reduce file size.
    
    Args:
        input_path (str): Path to the input image
        output_path (str): Path where the compressed image will be saved
        quality (int): JPEG quality (1-100, default: 85)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with Image.open(input_path) as img:
            # Convert RGBA images to RGB
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Save with compression
            img.save(output_path, 'JPEG', quality=quality, optimize=True)
            
        print(f"✓ Image compressed with quality {quality}: {output_path}")
        return True
        
    except Exception as e:
        print(f"✗ Error compressing image: {str(e)}")
        return False


def process_image(input_path, output_path, options=None):
    """
    Processes an image based on the provided options.
    This is the main processing function that combines resize and compress operations.
    
    Args:
        input_path (str): Path to the input image
        output_path (str): Path where the processed image will be saved
        options (dict): Processing options (resize, compress, etc.)
            - resize: bool (default: True)
            - compress: bool (default: True)
            - width: int (default: 800)
            - height: int (default: 600)
            - quality: int (default: 85)
        
    Returns:
        dict: Processing results containing:
            - success: bool
            - original_size: int (bytes)
            - processed_size: int (bytes)
            - category: str
            - message: str
    """
    # Default options
    if options is None:
        options = {}
    
    resize_enabled = options.get('resize', True)
    compress_enabled = options.get('compress', True)
    width = options.get('width', DEFAULT_WIDTH)
    height = options.get('height', DEFAULT_HEIGHT)
    quality = options.get('quality', COMPRESSION_QUALITY)
    
    result = {
        'success': False,
        'original_size': 0,
        'processed_size': 0,
        'category': 'Unknown',
        'message': ''
    }
    
    try:
        # Step 1: Validate the input image
        is_valid, error_msg = validate_image(input_path)
        if not is_valid:
            result['message'] = f"Invalid image: {error_msg}"
            return result
        
        # Step 2: Get original image information
        result['original_size'] = get_image_size(input_path)
        result['category'] = get_image_category(input_path)
        
        # Step 3: Process the image
        temp_path = output_path + ".temp.jpg"
        
        if resize_enabled and compress_enabled:
            # Resize and compress in one step
            with Image.open(input_path) as img:
                # Convert RGBA to RGB
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                # Resize
                resized_img = img.resize((width, height), Image.Resampling.LANCZOS)
                
                # Save with compression
                resized_img.save(output_path, 'JPEG', quality=quality, optimize=True)
            
            print(f"✓ Image resized to {width}x{height} and compressed")
            
        elif resize_enabled:
            # Only resize
            resize_image(input_path, output_path, width, height)
            
        elif compress_enabled:
            # Only compress
            compress_image(input_path, output_path, quality)
            
        else:
            # No processing, just copy
            with Image.open(input_path) as img:
                img.save(output_path, quality=95)
        
        # Step 4: Get processed image size
        result['processed_size'] = get_image_size(output_path)
        
        # Calculate compression ratio
        if result['original_size'] > 0:
            compression_ratio = (1 - result['processed_size'] / result['original_size']) * 100
            print(f"✓ Compression ratio: {compression_ratio:.2f}%")
        
        result['success'] = True
        result['message'] = "Image processed successfully"
        
        return result
        
    except Exception as e:
        result['message'] = f"Processing error: {str(e)}"
        print(f"✗ Image processing failed: {str(e)}")
        return result


def format_size(size_bytes):
    """
    Converts bytes to a human-readable format (KB, MB).
    
    Args:
        size_bytes (int): Size in bytes
        
    Returns:
        str: Formatted size string
    """
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f}KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f}MB"


# Test the image processor when run directly
if __name__ == "__main__":
    print("Image Processor Module")
    print("This module provides image processing functions using Pillow (PIL)")
