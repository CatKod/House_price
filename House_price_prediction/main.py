from models.model_training import train_model
from models.predict import predict_price
from models.model_evaluation import evaluate_model

if __name__ == "__main__":
    # Huấn luyện mô hình
    train_model()  # Sử dụng bảng SQL

    # Dự đoán giá nhà
    sample_features = [[1200, 3, 2]]  # Ví dụ: diện tích, số phòng ngủ, số phòng tắm
    prediction = predict_price(sample_features)
    prediction_in_billion = prediction / 1e9  # Chuyển đổi sang đơn vị tỷ
    print(f"Predicted price: {prediction_in_billion} tỷ")

    # Đánh giá mô hình
    evaluate_model()  # Sử dụng bảng SQL
