import pickle
import pandas as pd
import psycopg2
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PolynomialFeatures

def evaluate_model():
    # Kết nối tới cơ sở dữ liệu
    conn = psycopg2.connect(
        dbname="house_prices",
        user="postgres",
        password="271205",
        host="localhost",
        port="5432"
    )
    query = """
        SELECT "Area", "Bedrooms", "Bathrooms", "Floors", "Width_meters", "Price"::double precision
        FROM house_prices
        WHERE "Price" ~ '^[0-9]+(\.[0-9]+)?$';
    """
    data = pd.read_sql_query(query, conn)
    conn.close()

    # Chuẩn bị dữ liệu
    X = data[["Area", "Bedrooms", "Bathrooms", "Floors", "Width_meters"]].values  # Các cột đặc trưng
    y = data["Price"].values  # Cột mục tiêu

    # Tải mô hình và bộ biến đổi đa thức
    with open("models/trained_model.pkl", "rb") as f:
        model, poly = pickle.load(f)

    # Tạo đặc trưng đa thức
    X_poly = poly.transform(X)

    # Chia dữ liệu thành tập kiểm tra
    _, X_test, _, y_test = train_test_split(X_poly, y, test_size=0.2, random_state=42)

    # Dự đoán và tính toán lỗi
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print(f"Mean Squared Error: {mse}")
