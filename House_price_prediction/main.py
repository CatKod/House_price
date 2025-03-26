from models.model_training import train_model
from models.predict import predict_price
from models.model_evaluation import evaluate_model

def main(features):
    # Huấn luyện mô hình
    train_model()  # Sử dụng bảng SQL

    # Dự đoán giá nhà
    prediction = predict_price(features)
    prediction_in_billion = prediction / 1e9  # Chuyển đổi sang đơn vị tỷ
    print(f"Predicted price: {prediction_in_billion} VND")

    # Đánh giá mô hình
    evaluate_model()  # Sử dụng bảng SQL
