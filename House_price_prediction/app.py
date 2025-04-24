from flask import Flask, render_template, request, jsonify
from models.predict_house_price import load_model, predict_price, format_price
import os

app = Flask(__name__)

# Load the trained model
model = load_model()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get input values from the form
        area = float(request.form['area'])
        bedrooms = int(request.form['bedrooms'])
        bathrooms = int(request.form['bathrooms'])
        floors = int(request.form['floors'])
        width_meters = float(request.form['width_meters'])
        
        # Make prediction
        prediction = predict_price(model, area, bedrooms, bathrooms, floors, width_meters)
        formatted_price = format_price(prediction)
        
        return jsonify({
            'success': True,
            'prediction': formatted_price
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True)