import models.predict_house_price

"""
Install dependencies: pip install -r requirements.txt

Run ML model training and demonstration: python main.py

Start the web application: python main.py web

Run only ML training: python main.py train
"""

def main():
    """
    Main function to demonstrate the machine learning model functionality.
    This function loads data, trains the model, makes predictions, and evaluates performance.
    """
    print("=== House Price Prediction System ===")
    print("Loading data and training model...")
    
    try:
        # Load data from database
        data = models.predict_house_price.load_data()
        if data is None:
            print("Error: Could not load data from database")
            return
        
        # Prepare data for training
        X_train, X_test, y_train, y_test = models.predict_house_price.prepare_data(data)
        if X_train is None:
            print("Error: Could not prepare data for training")
            return
        
        # Train the model
        print(f"Training with {len(X_train)} samples...")
        model = models.predict_house_price.train_model(X_train, y_train)
        
        # Evaluate the model
        print("Evaluating model performance...")
        mse, rmse, r2, mape = models.predict_house_price.evaluate_model(model, X_test, y_test)
        
        # Save the trained model
        models.predict_house_price.save_model(model, "models/house_price_model.pkl")
        print("Model saved successfully!")
        
        # Make sample predictions
        print("\n=== Sample Predictions ===")
        sample_features = [
            [240, 3, 2, 1, 10],  # Area, Bedrooms, Bathrooms, Floors, Width
            [150, 2, 1, 1, 8],
            [300, 4, 3, 2, 12]
        ]
        
        for i, features in enumerate(sample_features, 1):
            try:
                # Unpack features list: [Area, Bedrooms, Bathrooms, Floors, Width]
                area, bedrooms, bathrooms, floors, width = features
                prediction = models.predict_house_price.predict_price(model, area, bedrooms, bathrooms, floors, width)
                print(f"Sample {i}: Features {features} -> Predicted price: {prediction:,.0f} VND")
            except Exception as e:
                print(f"Error predicting sample {i}: {e}")
        
        print(f"\nModel Performance:")
        print(f"- Mean Squared Error: {mse:,.0f}")
        print(f"- Root Mean Squared Error: {rmse:,.0f}")
        print(f"- R² Score: {r2:.4f}")
        print(f"- Mean Absolute Percentage Error: {mape:.2f}%")
        
    except Exception as e:
        print(f"Error in main execution: {e}")

def run_web_app():
    """
    Function to run the Flask web application.
    """
    try:
        from interface.interface import app
        print("Starting Flask web application...")
        print("Access the application at: http://localhost:5000")
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        print(f"Error starting web application: {e}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'web':
            # Run web application
            run_web_app()
        elif sys.argv[1] == 'train':
            # Run ML training only
            main()
        else:
            print("Usage:")
            print("  python main.py          - Run ML model training and demonstration")
            print("  python main.py web      - Start the web application")
            print("  python main.py train    - Run ML training only")
    else:
        # Default: run ML model demonstration
        main()