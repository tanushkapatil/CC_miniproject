// Configuration
// Automatically detect API URL based on environment
const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5000'
    : '/api';  // Use relative path for production (proxied by Nginx)

// State
let selectedFile = null;
let currentImages = [];

// DOM Elements
const imageInput = document.getElementById('imageInput');
const uploadArea = document.getElementById('uploadArea');
const uploadPlaceholder = uploadArea.querySelector('.upload-placeholder');
const imagePreview = document.getElementById('imagePreview');
const previewImg = document.getElementById('previewImg');
const previewInfo = document.getElementById('previewInfo');
const removeImage = document.getElementById('removeImage');
const processBtn = document.getElementById('processBtn');

// Processing Options
const resizeCheck = document.getElementById('resizeCheck');
const compressCheck = document.getElementById('compressCheck');
const widthInput = document.getElementById('widthInput');
const heightInput = document.getElementById('heightInput');
const qualitySlider = document.getElementById('qualitySlider');
const qualityValue = document.getElementById('qualityValue');
const resizeOptions = document.getElementById('resizeOptions');
const compressOptions = document.getElementById('compressOptions');

// Modals
const processingModal = document.getElementById('processingModal');
const successModal = document.getElementById('successModal');
const resultDetails = document.getElementById('resultDetails');
const closeSuccess = document.getElementById('closeSuccess');
const viewGallery = document.getElementById('viewGallery');
const processAnother = document.getElementById('processAnother');

// Gallery
const galleryGrid = document.getElementById('galleryGrid');
const refreshGallery = document.getElementById('refreshGallery');
const totalImages = document.getElementById('totalImages');
const imageDetailModal = document.getElementById('imageDetailModal');
const detailContent = document.getElementById('detailContent');
const closeDetail = document.getElementById('closeDetail');

// Toast
const errorToast = document.getElementById('errorToast');
const errorMessage = document.getElementById('errorMessage');

// Navigation
const navTabs = document.querySelectorAll('.nav-tab');
const uploadSection = document.getElementById('uploadSection');
const gallerySection = document.getElementById('gallerySection');

// ====================
// NAVIGATION
// ====================

navTabs.forEach(tab => {
    tab.addEventListener('click', () => {
        const targetTab = tab.dataset.tab;
        
        // Update active tab
        navTabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        
        // Show/hide sections
        if (targetTab === 'upload') {
            uploadSection.classList.add('active');
            gallerySection.classList.remove('active');
        } else if (targetTab === 'gallery') {
            uploadSection.classList.remove('active');
            gallerySection.classList.add('active');
            loadGallery();
        }
    });
});

// ====================
// FILE UPLOAD
// ====================

// Click to upload
uploadArea.addEventListener('click', (e) => {
    if (e.target !== removeImage && !removeImage.contains(e.target)) {
        imageInput.click();
    }
});

// Drag and drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.style.transform = 'scale(1.02)';
    uploadPlaceholder.style.borderColor = 'var(--primary)';
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.style.transform = '';
    uploadPlaceholder.style.borderColor = '';
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.style.transform = '';
    uploadPlaceholder.style.borderColor = '';
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelection(files[0]);
    }
});

// File input change
imageInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelection(e.target.files[0]);
    }
});

// Remove image
removeImage.addEventListener('click', (e) => {
    e.stopPropagation();
    resetUploadForm();
});

// Handle file selection
function handleFileSelection(file) {
    // Validate file type
    if (!file.type.startsWith('image/')) {
        showError('Please select a valid image file');
        return;
    }
    
    // Validate file size (10MB max)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
        showError('File size must be less than 10MB');
        return;
    }
    
    selectedFile = file;
    
    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImg.src = e.target.result;
        uploadPlaceholder.classList.add('hidden');
        imagePreview.classList.remove('hidden');
        
        // Show file info
        previewInfo.innerHTML = `
            <strong>${file.name}</strong><br>
            ${formatFileSize(file.size)}
        `;
        
        processBtn.disabled = false;
    };
    reader.readAsDataURL(file);
}

// ====================
// PROCESSING OPTIONS
// ====================

resizeCheck.addEventListener('change', () => {
    resizeOptions.style.display = resizeCheck.checked ? 'block' : 'none';
});

compressCheck.addEventListener('change', () => {
    compressOptions.style.display = compressCheck.checked ? 'block' : 'none';
});

qualitySlider.addEventListener('input', () => {
    qualityValue.textContent = qualitySlider.value;
});

// ====================
// PROCESS IMAGE
// ====================

processBtn.addEventListener('click', async () => {
    if (!selectedFile) {
        showError('Please select an image first');
        return;
    }
    
    // Create form data
    const formData = new FormData();
    formData.append('image', selectedFile);
    formData.append('resize', resizeCheck.checked);
    formData.append('compress', compressCheck.checked);
    formData.append('width', widthInput.value);
    formData.append('height', heightInput.value);
    formData.append('quality', qualitySlider.value);
    
    try {
        // Show processing modal
        processingModal.classList.remove('hidden');
        
        // Upload and process
        const response = await fetch(`${API_URL}/upload`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.status === 'success') {
            showSuccessModal(result);
        } else {
            throw new Error(result.message || 'Processing failed');
        }
        
    } catch (error) {
        console.error('Upload error:', error);
        showError(error.message || 'Failed to process image. Please ensure the backend server is running.');
    } finally {
        processingModal.classList.add('hidden');
    }
});

// Show success modal
function showSuccessModal(result) {
    const metadata = result.metadata || {};
    
    resultDetails.innerHTML = `
        <div class="result-item">
            <span class="result-label">File Name</span>
            <span class="result-value">${metadata.original_file_name || 'Unknown'}</span>
        </div>
        <div class="result-item">
            <span class="result-label">Category</span>
            <span class="result-value">${metadata.category || 'Image'}</span>
        </div>
        <div class="result-item">
            <span class="result-label">Original Size</span>
            <span class="result-value">${metadata.original_size || 'N/A'}</span>
        </div>
        <div class="result-item">
            <span class="result-label">Processed Size</span>
            <span class="result-value">${metadata.processed_size || 'N/A'}</span>
        </div>
        <div class="result-item">
            <span class="result-label">Upload Time</span>
            <span class="result-value">${new Date(metadata.upload_time).toLocaleString()}</span>
        </div>
    `;
    
    successModal.classList.remove('hidden');
}

// Success modal actions
closeSuccess.addEventListener('click', () => {
    successModal.classList.add('hidden');
    resetUploadForm();
});

viewGallery.addEventListener('click', () => {
    successModal.classList.add('hidden');
    document.querySelector('[data-tab="gallery"]').click();
});

processAnother.addEventListener('click', () => {
    successModal.classList.add('hidden');
    resetUploadForm();
});

// Reset upload form
function resetUploadForm() {
    selectedFile = null;
    imageInput.value = '';
    previewImg.src = '';
    uploadPlaceholder.classList.remove('hidden');
    imagePreview.classList.add('hidden');
    processBtn.disabled = true;
}

// ====================
// GALLERY
// ====================

// Load gallery
async function loadGallery() {
    try {
        const response = await fetch(`${API_URL}/images`);
        
        if (!response.ok) {
            throw new Error('Failed to load images');
        }
        
        const result = await response.json();
        
        if (result.status === 'success') {
            currentImages = result.images || [];
            displayGallery(currentImages);
        } else {
            throw new Error(result.message || 'Failed to load gallery');
        }
        
    } catch (error) {
        console.error('Gallery error:', error);
        showError('Failed to load gallery. Please ensure the backend server is running.');
        displayGallery([]);
    }
}

// Display gallery
function displayGallery(images) {
    totalImages.textContent = images.length;
    
    if (images.length === 0) {
        galleryGrid.innerHTML = `
            <div class="gallery-empty">
                <svg class="empty-icon" viewBox="0 0 100 100" fill="none">
                    <circle cx="50" cy="50" r="45" stroke="currentColor" stroke-width="2" opacity="0.3"/>
                    <path d="M35 65L50 45L65 65M40 50L50 35L60 50" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <p class="empty-text">No images yet</p>
                <p class="empty-subtext">Upload your first image to get started</p>
            </div>
        `;
        return;
    }
    
    galleryGrid.innerHTML = images.map((img, index) => `
        <div class="gallery-item" data-index="${index}">
            <img src="${img.image_url}" alt="${img.file_name}" class="gallery-item-image" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22%3E%3Crect fill=%22%23f1f5f9%22 width=%22100%22 height=%22100%22/%3E%3Ctext x=%2250%22 y=%2250%22 text-anchor=%22middle%22 dy=%22.3em%22 fill=%22%2394a3b8%22 font-size=%2214%22%3ENo Image%3C/text%3E%3C/svg%3E'">
            <div class="gallery-item-info">
                <div class="gallery-item-name" title="${img.file_name}">${img.file_name}</div>
                <div class="gallery-item-meta">
                    <span>${img.processed_size}</span>
                    <span>${formatUploadTime(img.upload_time)}</span>
                </div>
                <div class="gallery-item-actions">
                    <button class="btn-icon" onclick="viewImageDetail(${index})" title="View Details">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke="currentColor" stroke-width="2"/>
                            <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
                        </svg>
                    </button>
                    <button class="btn-icon" onclick="downloadImage('${img.image_url}', '${img.file_name}')" title="Download">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

// View image detail
function viewImageDetail(index) {
    const img = currentImages[index];
    
    detailContent.innerHTML = `
        <img src="${img.image_url}" alt="${img.file_name}" class="detail-image">
        <div class="detail-info">
            <div class="detail-info-item">
                <div class="detail-label">File Name</div>
                <div class="detail-value">${img.file_name}</div>
            </div>
            <div class="detail-info-item">
                <div class="detail-label">Original Size</div>
                <div class="detail-value">${img.original_size}</div>
            </div>
            <div class="detail-info-item">
                <div class="detail-label">Processed Size</div>
                <div class="detail-value">${img.processed_size}</div>
            </div>
            <div class="detail-info-item">
                <div class="detail-label">Upload Time</div>
                <div class="detail-value">${new Date(img.upload_time).toLocaleString()}</div>
            </div>
        </div>
        <div class="detail-actions">
            <button class="btn-secondary" onclick="downloadImage('${img.image_url}', '${img.file_name}')">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                Download Image
            </button>
        </div>
    `;
    
    imageDetailModal.classList.remove('hidden');
}

// Download image
function downloadImage(url, filename) {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Close detail modal
closeDetail.addEventListener('click', () => {
    imageDetailModal.classList.add('hidden');
});

// Refresh gallery
refreshGallery.addEventListener('click', () => {
    loadGallery();
});

// Close modals on background click
processingModal.addEventListener('click', (e) => {
    if (e.target === processingModal) {
        processingModal.classList.add('hidden');
    }
});

successModal.addEventListener('click', (e) => {
    if (e.target === successModal) {
        successModal.classList.add('hidden');
    }
});

imageDetailModal.addEventListener('click', (e) => {
    if (e.target === imageDetailModal) {
        imageDetailModal.classList.add('hidden');
    }
});

// ====================
// UTILITIES
// ====================

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

// Format upload time
function formatUploadTime(timeString) {
    const date = new Date(timeString);
    const now = new Date();
    const diff = now - date;
    
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (days > 0) return `${days}d ago`;
    if (hours > 0) return `${hours}h ago`;
    if (minutes > 0) return `${minutes}m ago`;
    return 'Just now';
}

// Show error toast
function showError(message) {
    errorMessage.textContent = message;
    errorToast.classList.remove('hidden');
    
    setTimeout(() => {
        errorToast.classList.add('hidden');
    }, 5000);
}

// ====================
// INITIALIZATION
// ====================

// Load gallery on page load if the gallery tab is active
if (gallerySection.classList.contains('active')) {
    loadGallery();
}
