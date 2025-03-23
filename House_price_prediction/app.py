import tkinter as tk
from tkinter import ttk, messagebox
import pickle

# Load mô hình dự đoán
model_path = "C:/Users/kimvi/OneDrive - Hanoi University of Science and Technology/GitHub/My_AI_Project/House_price_prediction/models/trained_model.pkl"
with open(model_path, "rb") as file:
    model = pickle.load(file)

# Hàm dự đoán giá nhà
def predict_price():
    try:
        area = float(entry_area.get())
        bedrooms = int(entry_bedrooms.get()) if entry_bedrooms.get() else 0
        bathrooms = int(entry_bathrooms.get()) if entry_bathrooms.get() else 0
        floors = int(entry_floors.get()) if entry_floors.get() else 0
        width = float(entry_width.get()) if entry_width.get() else 0.0

        features = [[area, bedrooms, bathrooms, floors, width]]
        predicted_price = model.predict(features)[0]

        messagebox.showinfo("Kết quả", f"Giá dự đoán: {predicted_price:,.0f} VND")
    except ValueError:
        messagebox.showerror("Lỗi", "Vui lòng nhập đúng định dạng số!")

# Giao diện chính
root = tk.Tk()
root.title("Dự đoán giá nhà")
root.geometry("400x300")

# Loại giao dịch
tk.Label(root, text="Loại giao dịch:").pack()
transaction_type = ttk.Combobox(root, values=["Mua nhà", "Thuê nhà"])
transaction_type.pack()

# Nhập diện tích (bắt buộc)
tk.Label(root, text="Diện tích (m²) *").pack()
entry_area = tk.Entry(root)
entry_area.pack()

# Nhập số phòng ngủ
tk.Label(root, text="Số phòng ngủ").pack()
entry_bedrooms = tk.Entry(root)
entry_bedrooms.pack()

# Nhập số phòng tắm
tk.Label(root, text="Số phòng tắm").pack()
entry_bathrooms = tk.Entry(root)
entry_bathrooms.pack()

# Nhập số tầng
tk.Label(root, text="Số tầng").pack()
entry_floors = tk.Entry(root)
entry_floors.pack()

# Nhập chiều rộng
tk.Label(root, text="Chiều rộng (m)").pack()
entry_width = tk.Entry(root)
entry_width.pack()

# Nút dự đoán
btn_predict = tk.Button(root, text="Dự đoán giá", command=predict_price)
btn_predict.pack(pady=10)

# Chạy ứng dụng
root.mainloop()
