from tensorflow import keras
import numpy as np
import cv2

def preprocess_image(image):
    """
    Preprocess image for handwriting recognition (MNIST style).
    
    Args:
        image: Input image array
        
    Returns:
        Preprocessed image ready for model prediction
    """    # Convert to grayscale if image is colored
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    # Now we expect black background with white digits (MNIST style)
    # No need to invert since canvas already provides this format

    # Apply slight blur to smooth hand-drawn lines
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    # Use simple threshold since we have clean black/white contrast
    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)

    # Find bounding box of the digit
    coords = cv2.findNonZero(binary)
    if coords is not None:
        x, y, w, h = cv2.boundingRect(coords)
        # Add padding around the digit (20% of the smaller dimension)
        padding = max(5, min(w, h) // 5)
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(binary.shape[1] - x, w + 2*padding)
        h = min(binary.shape[0] - y, h + 2*padding)
        digit = binary[y:y+h, x:x+w]
    else:
        digit = binary

    # Create square canvas with proper aspect ratio
    max_dim = max(digit.shape)
    square_size = max(max_dim + 40, 80)  # Ensure minimum size with padding
    padded = np.zeros((square_size, square_size), dtype=np.uint8)
    
    # Center the digit in the square
    x_offset = (square_size - digit.shape[1]) // 2
    y_offset = (square_size - digit.shape[0]) // 2
    padded[y_offset:y_offset+digit.shape[0], x_offset:x_offset+digit.shape[1]] = digit

    # Resize to 28x28 (MNIST standard size)
    resized = cv2.resize(padded, (28, 28), interpolation=cv2.INTER_AREA)

    # Apply morphological operations to clean up the image
    kernel = np.ones((2,2), np.uint8)
    resized = cv2.morphologyEx(resized, cv2.MORPH_CLOSE, kernel)

    # Normalize pixel values to 0-1 range
    normalized = resized.astype('float32') / 255.0
    
    # Reshape for model input (batch_size, height, width, channels)
    preprocessed = normalized.reshape(1, 28, 28, 1)
    
    return preprocessed

def load_model(model_path):
    """
    Load trained model from file.
    
    Args:
        model_path: Path to saved model file
        
    Returns:
        Loaded Keras model
    """
    try:
        model = keras.models.load_model(model_path)
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        return None
