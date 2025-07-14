import pandas as pd
import numpy as np
import psycopg2
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
import pickle
import os

def load_data():
    """
    Load data from PostgreSQL database, filtering out non-numeric price values.
    """
    try:
        # Connect to PostgreSQL database
        conn = psycopg2.connect(
            dbname="house_prices",
            user="postgres",
            password="271205",
            host="localhost",
            port="5432"
        )
        
        # Query to get only numeric price data
        query = """
            SELECT "Area", "Bedrooms", "Bathrooms", "Floors", "Width_meters", "Price"::double precision
            FROM house_prices
            WHERE "Price" ~ '^[0-9]+(\.[0-9]+)?$';
        """
        
        # Load data into DataFrame
        data = pd.read_sql_query(query, conn)
        conn.close()
        
        print(f"Loaded {len(data)} records with numeric prices")
        return data
    
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def prepare_data(data):
    """
    Prepare data for model training.
    """
    if data is None or data.empty:
        print("No data available for preparation")
        return None, None, None, None
    
    # Extract features and target
    X = data[["Area", "Bedrooms", "Bathrooms", "Floors", "Width_meters"]]
    y = data["Price"]
    
    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    return X_train, X_test, y_train, y_test

def train_model(X_train, y_train):
    """
    Train a polynomial Ridge regression model with optimal lambda using GridSearchCV.
    """
    # Create pipeline with polynomial features and Ridge regression
    pipeline = Pipeline([
        ('poly', PolynomialFeatures(degree=5)),
        ('scaler', StandardScaler()),
        ('ridge', Ridge())
    ])
    
    # Define parameter grid for lambda (alpha)
    param_grid = {
        'ridge__alpha': [0.001, 0.01, 0.1, 1.0, 10.0, 100.0]
    }
    
    # Perform grid search with cross-validation
    grid_search = GridSearchCV(
        estimator=pipeline,
        param_grid=param_grid,
        cv=5,
        scoring='neg_mean_squared_error',
        n_jobs=-1
    )
    
    # Fit the model
    grid_search.fit(X_train, y_train)
    
    # Get the best model
    best_model = grid_search.best_estimator_
    best_lambda = grid_search.best_params_['ridge__alpha']
    
    print(f"Best lambda (alpha) value: {best_lambda}")
    print(f"Polynomial degree: 5")
    
    return best_model

def evaluate_model(model, X_test, y_test):
    """
    Evaluate the model performance.
    """
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    
    # Calculate MAPE (Mean Absolute Percentage Error)
    mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
    
    print("\nModel Evaluation:")
    print(f"Mean Squared Error: {mse:.2f}")
    print(f"Root Mean Squared Error: {rmse:.2f}")
    print(f"R² Score: {r2:.4f}")
    print(f"Mean Absolute Percentage Error: {mape:.2f}%")
    
    return mse, rmse, r2, mape

def save_model(model, filepath="House_price_prediction/models/house_price_model.pkl"):
    """
    Save the trained model to a file.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"Model saved to {filepath}")

def load_model(filepath="House_price_prediction/models/house_price_model.pkl"):
    """
    Load the trained model from a file.
    """
    try:
        with open(filepath, 'rb') as f:
            model = pickle.load(f)
        
        print(f"Model loaded from {filepath}")
        return model
    
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

def predict_price(model, area, bedrooms, bathrooms, floors, width_meters):
    """
    Predict house price based on input features.
    """
    # Create feature array
    features = np.array([[area, bedrooms, bathrooms, floors, width_meters]])
    
    # Make prediction
    prediction = model.predict(features)[0]
    
    return prediction

def format_price(price):
    """
    Format price in billions of VND.
    """
    price_in_billions = price / 1e9
    return f"{price_in_billions:,.2f} tỷ VND"

def plot_feature_importance(model, feature_names):
    """
    Plot feature importance based on model coefficients.
    """
    # Get coefficients from the Ridge model in the pipeline
    coefficients = model.named_steps['ridge'].coef_
    
    # Get feature names from polynomial features
    poly = model.named_steps['poly']
    poly_feature_names = poly.get_feature_names_out(feature_names)
    
    # Create DataFrame
    importance_df = pd.DataFrame({
        'Feature': poly_feature_names,
        'Importance': np.abs(coefficients)
    })
    
    # Sort by importance and take top 10
    importance_df = importance_df.sort_values('Importance', ascending=False).head(10)
    
    # Plot
    plt.figure(figsize=(12, 8))
    plt.bar(importance_df['Feature'], importance_df['Importance'])
    plt.title('Top 10 Feature Importance')
    plt.xlabel('Feature')
    plt.ylabel('Absolute Coefficient Value')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

def main():
    """
    Main function to train the model and make predictions.
    """
    print("=== House Price Prediction System ===")
    
    data = load_data()
    
    if data is None or data.empty:
        print("Failed to load data. Exiting.")
        return
    

    X_train, X_test, y_train, y_test = prepare_data(data)
    
    if X_train is None:
        print("Failed to prepare data. Exiting.")
        return
    
    model = train_model(X_train, y_train)
    
    evaluate_model(model, X_test, y_test)
    
    save_model(model)
    
    example_features = [
        (240, 3, 2, 1, 10),
        (120, 2, 1, 1, 5),
        (500, 5, 3, 3, 15)
    ]
    
    for features in example_features:
        area, bedrooms, bathrooms, floors, width_meters = features
        prediction = predict_price(model, area, bedrooms, bathrooms, floors, width_meters)
        formatted_price = format_price(prediction)
        
        print(f"\nHouse with:")
        print(f"  Area: {area}m²")
        print(f"  Bedrooms: {bedrooms}")
        print(f"  Bathrooms: {bathrooms}")
        print(f"  Floors: {floors}")
        print(f"  Width: {width_meters}m")
        print(f"Predicted price: {formatted_price}")
    
    print("\n=== End of House Price Prediction System ===")

if __name__ == "__main__":
    main()
