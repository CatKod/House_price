import pickle
import pandas as pd
import psycopg2
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

def train_model():
    # Kết nối tới cơ sở dữ liệu
    conn = psycopg2.connect(
            dbname="house_prices",
        user="postgres",
        password="271205",
        host="localhost",
        port="5432"
    )
    query = """
        SELECT "Area", "Bedrooms", "Bathrooms", "Price"::double precision
        FROM house_prices
        WHERE "Price" ~ '^[0-9]+(\.[0-9]+)?$';
    """
    data = pd.read_sql_query(query, conn)
    conn.close()

    # Chuẩn bị dữ liệu
    X = data[["Area", "Bedrooms", "Bathrooms"]].values  # Các cột đặc trưng
    y = data["Price"].values  # Cột mục tiêu

    # Tạo đặc trưng đa thức
    poly = PolynomialFeatures(degree=2)
    X_poly = poly.fit_transform(X)

    # Chia dữ liệu thành tập huấn luyện và kiểm tra
    X_train, X_test, y_train, y_test = train_test_split(X_poly, y, test_size=0.2, random_state=42)

    # Huấn luyện mô hình
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Lưu mô hình và bộ biến đổi đa thức
    import os
    os.makedirs("models", exist_ok=True)
    with open("models/trained_model.pkl", "wb") as f:
        pickle.dump((model, poly), f)
