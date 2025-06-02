import tensorflow as tf
from tensorflow import keras
import numpy as np
import os

def create_model():
    """
    Create CNN model for handwriting recognition.
    
    Returns:
        Compiled Keras model
    """
    model = keras.Sequential([
        tf.keras.layers.Conv2D(128, (3, 3), activation='relu', input_shape=(28, 28, 1)),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(10, activation='softmax')    ])
    
    model.compile(optimizer='adam',
                 loss='sparse_categorical_crossentropy',
                 metrics=['accuracy'])
    
    return model

def train_model():
    """
    Train the handwriting recognition model using MNIST dataset.
    
    Returns:
        Trained model and training history
    """
    # Load MNIST dataset
    (train_images, train_labels), (test_images, test_labels) = keras.datasets.mnist.load_data()

    # Preprocess the data
    train_images = train_images.reshape((60000, 28, 28, 1))
    test_images = test_images.reshape((10000, 28, 28, 1))

    # Normalize pixel values
    train_images = train_images.astype('float32') / 255
    test_images = test_images.astype('float32') / 255

    # Create and train the model
    model = create_model()
    
    history = model.fit(train_images, train_labels,
                       epochs=10,
                       validation_data=(test_images, test_labels))
    
    # Create models directory if it doesn't exist
    if not os.path.exists('models'):
        os.makedirs('models')
    
    # Save the model
    model.save('C:/Users/kimvi/OneDrive - Hanoi University of Science and Technology/GitHub/My_AI_Project/HandWriting_detection/models/handwriting_model.h5')
    
    return model, history

if __name__ == '__main__':
    # Train the model
    model, history = train_model()    # Print final metrics
    print("\nTraining completed!")
    print(f"Final training accuracy: {history.history['accuracy'][-1]:.4f}")
    print(f"Final validation accuracy: {history.history['val_accuracy'][-1]:.4f}")
