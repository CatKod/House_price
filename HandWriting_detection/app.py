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
        
        # Preprocess image
        processed_image = preprocess_image(image)
        
        # Make prediction
        if model is not None:
            prediction = model.predict(processed_image)
            predicted_digit = np.argmax(prediction[0])
            confidence = float(prediction[0][predicted_digit])
            
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
