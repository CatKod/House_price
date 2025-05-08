import models.predict_house_price

def main(features):
    # Huấn luyện mô hình
    models.predict_house_price.train_model()  # Sử dụng bảng SQL

    # Dự đoán giá nhà
    features = [240, 3, 2, 1, 10]
    prediction = models.predict_house_price.predict_price(features)
    print(f"Predicted price: {prediction} VND")

    # Đánh giá mô hình
    models.predict_house_price.evaluate_model('house_prices')  # Sử dụng bảng SQL
