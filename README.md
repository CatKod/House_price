# 🏠 House Price Prediction System

A comprehensive real estate price prediction and management system for Hanoi, Vietnam. This project combines machine learning models with a full-featured web application for property listing, price prediction, and user management.

## 📋 Table of Contents
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Machine Learning Model](#machine-learning-model)
- [Database Schema](#database-schema)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

### 🤖 Machine Learning
- **Price Prediction**: Advanced polynomial Ridge regression model for accurate house price estimation
- **Model Training**: Automated training pipeline with hyperparameter optimization
- **Cross-validation**: 5-fold cross-validation for robust model evaluation
- **Feature Engineering**: Polynomial features with degree 5 for complex pattern recognition

### 🌐 Web Application
- **User Authentication**: Secure login/registration system
- **Property Listings**: Browse and search through extensive house listings
- **Price Prediction Interface**: Interactive web interface for price estimation
- **Admin Dashboard**: Administrative controls for user and post management
- **Favorites System**: Save and manage favorite properties
- **Deposit Management**: Handle property deposits and transactions
- **Responsive Design**: Mobile-friendly interface

### 📊 Data Management
- **PostgreSQL Integration**: Robust database management
- **Real Estate Data**: Comprehensive dataset of Hanoi house prices
- **Data Validation**: Input validation and error handling
- **Batch Processing**: Efficient data import and export capabilities

## 🛠 Technology Stack

### Backend
- **Python 3.x**: Core programming language
- **Flask**: Web framework for the application
- **PostgreSQL**: Database management system
- **psycopg2**: PostgreSQL adapter for Python

### Machine Learning
- **scikit-learn**: Machine learning library
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **matplotlib**: Data visualization
- **pickle**: Model serialization

### Frontend
- **HTML5/CSS3**: Modern web standards
- **Jinja2**: Template engine
- **Bootstrap**: Responsive design framework

## 📁 Project Structure

```
House_price/
├── main.py                 # Main application entry point
├── test.py                 # Test scripts
├── README.md              # Project documentation
├── app/                   # Application modules
├── config/                # Configuration files
├── data/                  # Data files and database scripts
│   ├── HN_Houseprice.csv  # Main dataset (13,500+ records)
│   ├── InPgAdmin4.py      # Database import utilities
│   ├── ToPgAdmin4.py      # Database export utilities
│   └── UpdateData.py      # Data update scripts
├── interface/             # Web interface
│   ├── interface.py       # Flask web application
│   └── templates/         # HTML templates
│       ├── index.html     # Homepage
│       ├── predict.html   # Price prediction interface
│       ├── login.html     # User authentication
│       └── [other templates]
├── models/                # Machine learning models
│   ├── predict_house_price.py  # ML model implementation
│   └── house_price_model.pkl   # Trained model file
└── src/                   # Source code utilities
```

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- PostgreSQL 12 or higher
- pip package manager

### 1. Clone the Repository
```bash
git clone https://github.com/CatKod/My_AI_Project.git
cd House_price
```

### 2. Install Dependencies
```bash
pip install pandas numpy scikit-learn matplotlib flask psycopg2-binary pickle5
```

### 3. Database Setup
1. Install and start PostgreSQL
2. Create a database named `house_prices`
3. Update database credentials in the code:
   - Database: `house_prices`
   - User: `postgres`
   - Password: `271205` (change this in production)
   - Host: `localhost`
   - Port: `5432`

### 4. Import Data
```bash
python data/InPgAdmin4.py
```

### 5. Train the Model
```bash
python main.py
```

## 🎯 Usage

### Web Application
1. Start the Flask server:
```bash
python interface/interface.py
```

2. Open your browser and navigate to `http://localhost:5000`

3. Features available:
   - **Register/Login**: Create an account or sign in
   - **Browse Properties**: View available house listings
   - **Predict Prices**: Use the ML model to estimate house prices
   - **Search & Filter**: Find properties based on criteria
   - **Manage Favorites**: Save interesting properties
   - **Admin Panel**: Administrative functions (admin accounts only)

### Machine Learning Model
```python
import models.predict_house_price as model

# Train the model
model.train_model()

# Make predictions
features = [240, 3, 2, 1, 10]  # [Area, Bedrooms, Bathrooms, Floors, Width]
price = model.predict_price(features)
print(f"Predicted price: {price} VND")

# Evaluate model performance
model.evaluate_model('house_prices')
```

## 🧠 Machine Learning Model

### Model Architecture
- **Algorithm**: Polynomial Ridge Regression
- **Polynomial Degree**: 5
- **Regularization**: Ridge (L2) with optimized alpha parameter
- **Feature Scaling**: StandardScaler for normalized inputs
- **Cross-validation**: 5-fold CV for hyperparameter tuning

### Input Features
1. **Area** (m²): Property area in square meters
2. **Bedrooms**: Number of bedrooms
3. **Bathrooms**: Number of bathrooms
4. **Floors**: Number of floors
5. **Width** (meters): Property width

### Model Performance
- Optimized using GridSearchCV
- Alpha values tested: [0.001, 0.01, 0.1, 1.0, 10.0, 100.0]
- Evaluation metrics: MSE, R² score
- Training data: 13,500+ real estate records from Hanoi

### Training Pipeline
```python
# Data loading from PostgreSQL
data = load_data()

# Data preprocessing
X_train, X_test, y_train, y_test = prepare_data(data)

# Model training with hyperparameter optimization
model = train_model(X_train, y_train)

# Model evaluation
evaluate_model(model, X_test, y_test)

# Model persistence
save_model(model)
```

## 🗄 Database Schema

### Main Tables
- **house_prices**: Property listings with features and prices
- **users**: User authentication and profile data
- **deposits**: Property deposit transactions
- **favorites**: User favorite properties
- **admin_approvals**: Administrative approval workflow

### Key Fields
```sql
-- House prices table structure
Area            NUMERIC     -- Property area (m²)
Bedrooms        INTEGER     -- Number of bedrooms
Bathrooms       INTEGER     -- Number of bathrooms
Floors          INTEGER     -- Number of floors
Width_meters    NUMERIC     -- Property width (m)
Price           NUMERIC     -- Property price (VND)
District        TEXT        -- Location district
Address         TEXT        -- Full address
```

## 🔧 Configuration

### Database Configuration
Update the database connection settings in `interface/interface.py`:
```python
DB_CONFIG = {
    'dbname': 'house_prices',
    'user': 'your_username',
    'password': 'your_password',
    'host': 'localhost',
    'port': '5432'
}
```

### Flask Configuration
```python
app.secret_key = 'your_secret_key'  # Change for production
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is part of an academic assignment at Hanoi University of Science and Technology.

## 👥 Authors

- **CatKod** - Initial work and development

## 🙏 Acknowledgments

- Hanoi University of Science and Technology
- Real estate data sources for Hanoi market
- Open source libraries and frameworks used

---

For questions or support, please contact the development team or create an issue in the repository.