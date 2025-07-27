// Document ready function
document.addEventListener('DOMContentLoaded', function() {
    // Image preview functionality
    const imageInput = document.getElementById('image');
    const imagePreview = document.getElementById('imagePreview');
    const imagePreviewContainer = document.getElementById('imagePreviewContainer');
    
    if (imageInput) {
        imageInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const file = this.files[0];
                
                // Verify file type
                const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
                if (!validTypes.includes(file.type)) {
                    alert('Please select a valid image file (JPG, JPEG, PNG)');
                    this.value = '';
                    imagePreviewContainer.style.display = 'none';
                    return;
                }
                
                // Verify file size (max 16MB)
                if (file.size > 16 * 1024 * 1024) {
                    alert('Image is too large. Maximum size is 16MB.');
                    this.value = '';
                    imagePreviewContainer.style.display = 'none';
                    return;
                }
                
                // Show preview
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.src = e.target.result;
                    imagePreviewContainer.style.display = 'block';
                }
                reader.readAsDataURL(file);
            } else {
                imagePreviewContainer.style.display = 'none';
            }
        });
    }
    
    // Form validation for encrypt form
    const encryptForm = document.getElementById('encryptForm');
    if (encryptForm) {
        encryptForm.addEventListener('submit', function(event) {
            const textInput = document.getElementById('text');
            if (textInput.value.trim() === '') {
                event.preventDefault();
                alert('Please enter a message to hide');
                textInput.focus();
                return false;
            }
            
            // Show loading state
            const encryptBtn = document.getElementById('encryptBtn');
            if (encryptBtn) {
                encryptBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
                encryptBtn.disabled = true;
            }
            
            return true;
        });
    }
    
    // Form validation for decrypt form
    const decryptForm = document.getElementById('decryptForm');
    if (decryptForm) {
        decryptForm.addEventListener('submit', function(event) {
            // Show loading state
            const decryptBtn = document.getElementById('decryptBtn');
            if (decryptBtn) {
                decryptBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Extracting...';
                decryptBtn.disabled = true;
            }
            
            return true;
        });
    }
    
    // Custom keys toggle for decrypt form
    const useCustomKeysCheckbox = document.getElementById('use_custom_keys');
    const keyfileContainer = document.getElementById('keyfileContainer');
    
    if (useCustomKeysCheckbox && keyfileContainer) {
        useCustomKeysCheckbox.addEventListener('change', function() {
            if (this.checked) {
                keyfileContainer.style.display = 'block';
                document.getElementById('keyfile').required = true;
            } else {
                keyfileContainer.style.display = 'none';
                document.getElementById('keyfile').required = false;
            }
        });
    }
});

// Function to copy decrypted text to clipboard
function copyToClipboard() {
    const textToCopy = document.querySelector('pre').textContent;
    
    // Create a temporary textarea element to copy from
    const textarea = document.createElement('textarea');
    textarea.value = textToCopy;
    textarea.setAttribute('readonly', '');
    textarea.style.position = 'absolute';
    textarea.style.left = '-9999px';
    document.body.appendChild(textarea);
    
    // Select and copy the text
    textarea.select();
    document.execCommand('copy');
    
    // Remove the temporary element
    document.body.removeChild(textarea);
    
    // Update button text to show copied status
    const copyBtn = document.getElementById('copyBtn');
    const originalText = copyBtn.innerHTML;
    copyBtn.innerHTML = '<i class="fas fa-check me-2"></i>Copied!';
    
    // Reset button text after 2 seconds
    setTimeout(function() {
        copyBtn.innerHTML = originalText;
    }, 2000);
}
