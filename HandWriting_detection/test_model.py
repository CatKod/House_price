import tensorflow as tf
from tensorflow import keras
import numpy as np
import matplotlib.pyplot as plt
from preprocessing import load_model

def test_model_on_mnist():
    """Test the trained model on some MNIST samples"""
    
    # Load the model
    model_path = "C:/Users/kimvi/OneDrive - Hanoi University of Science and Technology/GitHub/My_AI_Project/HandWriting_detection/models/handwriting_model.h5"
    model = load_model(model_path)
    
    if model is None:
        print("Could not load model. Please train the model first.")
        return
    
    # Load MNIST test data
    (_, _), (test_images, test_labels) = keras.datasets.mnist.load_data()
    
    # Preprocess test data same way as training
    test_images = test_images.reshape((10000, 28, 28, 1))
    test_images = test_images.astype('float32') / 255
    
    # Test on first 10 samples
    predictions = model.predict(test_images[:10])
    predicted_digits = np.argmax(predictions, axis=1)
    
    print("Testing model on first 10 MNIST samples:")
    print("True labels:", test_labels[:10])
    print("Predictions:", predicted_digits)
    print("Confidences:", [f"{np.max(pred):.3f}" for pred in predictions])
    
    # Calculate accuracy on larger sample
    test_predictions = model.predict(test_images[:1000])
    test_predicted_digits = np.argmax(test_predictions, axis=1)
    accuracy = np.mean(test_predicted_digits == test_labels[:1000])
    print(f"\nAccuracy on 1000 test samples: {accuracy:.4f}")
    
    return model, test_images, test_labels

if __name__ == "__main__":
    test_model_on_mnist()
