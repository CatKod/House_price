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
    """
    # Convert to grayscale if image is colored
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    # Invert if background is white (MNIST expects white digit on black)
    if np.mean(gray) > 127:
        gray = 255 - gray

    # Threshold to binary
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Find bounding box of the digit
    coords = cv2.findNonZero(binary)
    if coords is not None:
        x, y, w, h = cv2.boundingRect(coords)
        digit = binary[y:y+h, x:x+w]
    else:
        digit = binary

    # Pad to square
    size = max(digit.shape)
    padded = np.zeros((size, size), dtype=np.uint8)
    x_offset = (size - digit.shape[1]) // 2
    y_offset = (size - digit.shape[0]) // 2
    padded[y_offset:y_offset+digit.shape[0], x_offset:x_offset+digit.shape[1]] = digit

    # Resize to 28x28 (MNIST standard size)
    resized = cv2.resize(padded, (28, 28), interpolation=cv2.INTER_AREA)

    # Normalize pixel values
    normalized = resized.astype('float32') / 255.0
    
    # Reshape for model input
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
