// Form data storage
let formData = {
    mainImage: null,
    logoImage: null,
    additionalImages: [],
    facilities: []
};

// Initialize the form
document.addEventListener('DOMContentLoaded', function() {
    initializeImageUploads();
    initializeFormValidation();
    initializeFacilities();
    initializeAdditionalImages();
});

// Image upload functionality
function initializeImageUploads() {
    const mainImageArea = document.getElementById('mainImageArea');
    const logoImageArea = document.getElementById('logoImageArea');
    const mainImageInput = document.getElementById('mainImage');
    const logoImageInput = document.getElementById('logoImage');

    // Setup main image upload
    setupImageUpload(mainImageArea, mainImageInput, 'mainImage');
    
    // Setup logo image upload
    setupImageUpload(logoImageArea, logoImageInput, 'logoImage');
}

// Get elements
const addImagesBtn = document.getElementById("addImagesBtn");
const additionalImagesInput = document.getElementById("additionalImages");
const additionalImagesContainer = document.getElementById("additionalImagesContainer");
const noImagesPlaceholder = document.getElementById("noImagesPlaceholder");

// When user clicks the "Add More Images" button, trigger the hidden file input
addImagesBtn.addEventListener("click", () => {
    additionalImagesInput.click();
});

// When images are selected
additionalImagesInput.addEventListener("change", (event) => {
    const files = Array.from(event.target.files);

    if (files.length > 0) {
        noImagesPlaceholder.style.display = "none";
    }

    files.forEach((file) => {
        const reader = new FileReader();
        reader.onload = function (e) {
            const imagePreview = document.createElement("div");
            imagePreview.classList.add("image-preview");

            const img = document.createElement("img");
            img.src = e.target.result;
            img.alt = file.name;

            imagePreview.appendChild(img);
            additionalImagesContainer.appendChild(imagePreview);
        };
        reader.readAsDataURL(file);
    });

    // Clear the input so same files can be re-selected if needed
    additionalImagesInput.value = "";
});


function setupImageUpload(uploadArea, fileInput, imageType) {
    // Click to upload
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0], uploadArea, imageType);
        }
    });

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect(files[0], uploadArea, imageType);
        }
    });
}

function handleFileSelect(file, uploadArea, imageType) {
    if (file && file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
            showImagePreview(e.target.result, uploadArea);
            formData[imageType] = file;
            
            // Clear any error messages
            if (imageType === 'mainImage') {
                clearError('mainImageError');
            }
        };
        reader.readAsDataURL(file);
    }
}

function showImagePreview(imageSrc, uploadArea) {
    uploadArea.innerHTML = `
        <div class="preview-container">
            <img src="${imageSrc}" alt="Preview" class="preview-image">
            <div class="preview-overlay">
                <p>Click to change image</p>
            </div>
        </div>
    `;
}

// Additional Images functionality
function initializeAdditionalImages() {
    const addImagesBtn = document.getElementById('addImagesBtn');
    const additionalImagesInput = document.getElementById('additionalImages');
    
    addImagesBtn.addEventListener('click', () => {
        additionalImagesInput.click();
    });
    
    additionalImagesInput.addEventListener('change', (e) => {
        const files = Array.from(e.target.files);
        files.forEach(file => {
            if (file.type.startsWith('image/')) {
                addAdditionalImage(file);
            }
        });
        // Clear the input so the same files can be selected again if needed
        e.target.value = '';
    });
}

function addAdditionalImage(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        const imageData = {
            file: file,
            src: e.target.result,
            id: Date.now() + Math.random() // Simple unique ID
        };
        
        formData.additionalImages.push(imageData);
        displayAdditionalImages();
    };
    reader.readAsDataURL(file);
}

function removeAdditionalImage(imageId) {
    formData.additionalImages = formData.additionalImages.filter(img => img.id !== imageId);
    displayAdditionalImages();
}

function displayAdditionalImages() {
    const container = document.getElementById('additionalImagesContainer');
    const placeholder = document.getElementById('noImagesPlaceholder');
    
    if (formData.additionalImages.length === 0) {
        placeholder.style.display = 'block';
        // Remove any existing image items
        const imageItems = container.querySelectorAll('.additional-image-item');
        imageItems.forEach(item => item.remove());
    } else {
        placeholder.style.display = 'none';
        
        // Clear existing images and rebuild
        const imageItems = container.querySelectorAll('.additional-image-item');
        imageItems.forEach(item => item.remove());
        
        formData.additionalImages.forEach(imageData => {
            const imageItem = document.createElement('div');
            imageItem.className = 'additional-image-item';
            imageItem.innerHTML = `
                <img src="${imageData.src}" alt="Additional image">
                <button type="button" class="remove-image-btn" onclick="removeAdditionalImage(${imageData.id})">×</button>
            `;
            container.appendChild(imageItem);
        });
    }
}

// Form validation
function initializeFormValidation() {
    const form = document.getElementById('turfForm');
    form.addEventListener('submit', handleFormSubmit);

    // Real-time validation
    const requiredFields = ['turfName', 'ownerName', 'contactNumber', 'pricePerHour'];
    requiredFields.forEach(fieldName => {
        const field = document.getElementById(fieldName);
        field.addEventListener('blur', () => validateField(fieldName));
        field.addEventListener('input', () => clearError(fieldName + 'Error'));
    });
}

function handleFormSubmit(e) {
    e.preventDefault();
    
    if (validateForm()) {
        // Collect all form data
        const formDataToSubmit = collectFormData();
        console.log('Form submitted successfully:', formDataToSubmit);
        alert('Turf registered successfully!');
        
        // Here you would typically send the data to a server
        // Example: submitToServer(formDataToSubmit);
    } else {
        console.log('Form validation failed');
    }
}

function validateForm() {
    let isValid = true;
    
    // Validate required text fields
    const requiredFields = [
        { name: 'turfName', message: 'Turf name is required' },
        { name: 'ownerName', message: 'Owner name is required' },
        { name: 'contactNumber', message: 'Contact number is required' },
        { name: 'pricePerHour', message: 'Price per hour is required' }
    ];
    
    requiredFields.forEach(field => {
        if (!validateField(field.name, field.message)) {
            isValid = false;
        }
    });
    
    // Validate main image
    if (!formData.mainImage) {
        showError('mainImageError', 'Main turf image is required');
        document.getElementById('mainImageArea').classList.add('error');
        isValid = false;
    }
    
    return isValid;
}

function validateField(fieldName, customMessage) {
    const field = document.getElementById(fieldName);
    const value = field.value.trim();
    const errorId = fieldName + 'Error';
    
    if (!value) {
        const message = customMessage || `${fieldName} is required`;
        showError(errorId, message);
        field.classList.add('error');
        return false;
    } else {
        clearError(errorId);
        field.classList.remove('error');
        return true;
    }
}

function showError(errorId, message) {
    const errorElement = document.getElementById(errorId);
    if (errorElement) {
        errorElement.textContent = message;
    }
}

function clearError(errorId) {
    const errorElement = document.getElementById(errorId);
    if (errorElement) {
        errorElement.textContent = '';
    }
    
    // Clear image upload area error state
    if (errorId === 'mainImageError') {
        document.getElementById('mainImageArea').classList.remove('error');
    }
}

// Facilities handling
function initializeFacilities() {
    const facilityCheckboxes = document.querySelectorAll('input[name="facilities"]');
    facilityCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', (e) => {
            if (e.target.checked) {
                if (!formData.facilities.includes(e.target.value)) {
                    formData.facilities.push(e.target.value);
                }
            } else {
                formData.facilities = formData.facilities.filter(f => f !== e.target.value);
            }
        });
    });
}

// Collect all form data
function collectFormData() {
    const form = document.getElementById('turfForm');
    const formDataObj = new FormData(form);
    
    const data = {
        turfName: formDataObj.get('turfName'),
        ownerName: formDataObj.get('ownerName'),
        contactNumber: formDataObj.get('contactNumber'),
        emailAddress: formDataObj.get('emailAddress'),
        address: formDataObj.get('address'),
        city: formDataObj.get('city'),
        state: formDataObj.get('state'),
        pincode: formDataObj.get('pincode'),
        pricePerHour: formDataObj.get('pricePerHour'),
        turfType: formDataObj.get('turfType'),
        capacity: formDataObj.get('capacity'),
        openingTime: formDataObj.get('openingTime'),
        closingTime: formDataObj.get('closingTime'),
        description: formDataObj.get('description'),
        facilities: formData.facilities,
        mainImage: formData.mainImage,
        logoImage: formData.logoImage,
        additionalImages: formData.additionalImages
    };
    
    return data;
}

// Utility function to submit data to server (example)
function submitToServer(data) {
    // Example implementation - replace with your actual server endpoint
    /*
    const formData = new FormData();
    
    // Add text fields
    Object.keys(data).forEach(key => {
        if (key !== 'mainImage' && key !== 'logoImage' && key !== 'additionalImages' && key !== 'facilities') {
            formData.append(key, data[key]);
        }
    });
    
    // Add facilities as JSON
    formData.append('facilities', JSON.stringify(data.facilities));
    
    // Add images
    if (data.mainImage) {
        formData.append('mainImage', data.mainImage);
    }
    if (data.logoImage) {
        formData.append('logoImage', data.logoImage);
    }
    
    // Add additional images
    data.additionalImages.forEach((imageData, index) => {
        formData.append(`additionalImage_${index}`, imageData.file);
    });
    
    fetch('/api/register-turf', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(result => {
        console.log('Success:', result);
    })
    .catch(error => {
        console.error('Error:', error);
    });
    */
}