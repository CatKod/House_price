from flask import Flask, request, render_template, jsonify
import numpy as np
import cv2
import base64
from preprocessing import preprocess_image, load_model
import os

app = Flask(__name__)

# Load the trained model
model = None

def init_model():
    global model
    model_path = "C:/Users/kimvi/OneDrive - Hanoi University of Science and Technology/GitHub/My_AI_Project/HandWriting_detection/models/handwriting_model.h5"
    if os.path.exists(model_path):
        model = load_model(model_path)
    else:
        print("No model found. Please train the model first.")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get image data from request
        image_data = request.json['image']
          # Decode base64 image
        encoded_data = image_data.split(',')[1]
        nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

        # Debug: Save original image before processing
        cv2.imwrite('C:/Users/kimvi/OneDrive - Hanoi University of Science and Technology/GitHub/My_AI_Project/HandWriting_detection/image/debug_original_image.png', image)
        print(f"Original image shape: {image.shape}")
        print(f"Original image min/max: {image.min()}/{image.max()}")

        processed_image = preprocess_image(image)
        
        # Debug: Save processed image to see what the model is receiving
        debug_image = (processed_image[0, :, :, 0] * 255).astype(np.uint8)
        cv2.imwrite('C:/Users/kimvi/OneDrive - Hanoi University of Science and Technology/GitHub/My_AI_Project/HandWriting_detection/image/debug_processed_image.png', debug_image)
        print(f"Processed image shape: {processed_image.shape}")
        print(f"Processed image min/max: {processed_image.min():.3f}/{processed_image.max():.3f}")
        
        # Make prediction
        if model is not None:
            prediction = model.predict(processed_image)
            predicted_digit = np.argmax(prediction, axis=1)[0]  # Get the actual digit value
            confidence = float(prediction[0][predicted_digit])  # Use the digit as index
            
            # Debug information (you can remove this later)
            print(f"Prediction probabilities: {prediction}")
            print(f"Predicted digit: {predicted_digit}")
            print(f"Confidence: {confidence:.4f}")
            
            return jsonify({
                'success': True,
                'digit': int(predicted_digit),
                'confidence': f"{confidence:.2%}"
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Model not loaded. Please train the model first.'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    init_model()
    app.run(host='0.0.0.0', port=5000, debug=True)
