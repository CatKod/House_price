import pickle
import numpy as np

def predict_price(features):
    # Tải mô hình và bộ biến đổi đa thức
    with open("models/trained_model.pkl", "rb") as f:
        model, poly = pickle.load(f)

    # Biến đổi đặc trưng đầu vào
    features_poly = poly.transform(np.array(features))

    # Dự đoán giá
    return model.predict(features_poly)
