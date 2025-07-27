from PIL import Image
import numpy as np

def embed_text_in_image(image, text):
    """Embed text in an image using LSB steganography
    
    Args:
        image (PIL.Image): The image to embed text in
        text (str): The text to hide in the image
        
    Returns:
        PIL.Image: New image with embedded text
    """
    # Make a copy of the image to avoid modifying the original
    img_copy = image.copy()
    
    # Convert image to numpy array
    img_array = np.array(img_copy)
    
    # Ensure image is in RGB mode
    if len(img_array.shape) != 3 or img_array.shape[2] != 3:
        raise ValueError("Image must be in RGB format")
    
    # Get dimensions
    height, width, channels = img_array.shape
    
    # Convert text to binary
    binary_text = ''.join(format(ord(char), '08b') for char in text)
    
    # Add length of binary text as a 32-bit header (supports up to 512MB of text)
    binary_header = format(len(binary_text), '032b')
    binary_data = binary_header + binary_text
    
    # Check if the image is large enough to hold the data
    if len(binary_data) > height * width * channels:
        raise ValueError("Image is too small to hold this message")
    
    # Flatten the image array for easier modification
    flattened = img_array.flatten()
    
    # Embed the binary data into the LSB of each pixel value
    for i, bit in enumerate(binary_data):
        if i >= len(flattened):
            break
        
        # Make sure we're working with uint8 values
        pixel_value = int(flattened[i])
        
        # Clear the LSB and set it to the message bit
        flattened[i] = (pixel_value & 254) | int(bit)  # 254 = ~1 in uint8
    
    # Reshape the array back to the original shape
    modified_array = flattened.reshape(height, width, channels)
    
    # Ensure the array is in the correct datatype
    modified_array = np.clip(modified_array, 0, 255).astype(np.uint8)
    
    # Create a new image from the modified array
    modified_image = Image.fromarray(modified_array)
    
    return modified_image

def extract_text_from_image(image):
    """Extract hidden text from an image
    
    Args:
        image (PIL.Image): The image containing hidden text
        
    Returns:
        str: The extracted text
    """
    # Convert image to numpy array
    img_array = np.array(image)
    
    # Flatten the array for easier processing
    flattened = img_array.flatten()
    
    # Extract the LSB from each pixel value
    extracted_bits = ''.join([str(pixel & 1) for pixel in flattened])
    
    # Extract the header (first 32 bits) to get length of data
    header = extracted_bits[:32]
    data_length = int(header, 2)
    
    # Extract the actual data
    binary_text = extracted_bits[32:32+data_length]
    
    # Check if the extracted data length matches what was expected
    if len(binary_text) != data_length:
        raise ValueError("Extracted data is incomplete or corrupted")
    
    # Convert binary to text
    text = ''
    for i in range(0, len(binary_text), 8):
        byte = binary_text[i:i+8]
        if len(byte) == 8:  # Ensure we have a complete byte
            text += chr(int(byte, 2))
    
    return text
