import tkinter as tk
from tkinter import ttk, messagebox, StringVar, Listbox
import pickle
import os
import data.InPgAdmin4 
import data.ToPgAdmin4

data.ToPgAdmin4
data.InPgAdmin4.delete_duplicates()

# Load mô hình dự đoán
model_path = "C:/Users/kimvi/OneDrive - Hanoi University of Science and Technology/GitHub/My_AI_Project/models/trained_model.pkl"

if not os.path.exists(model_path):
    messagebox.showerror("Lỗi", "Không tìm thấy tệp mô hình dự đoán!")
    exit()

try:
    with open(model_path, "rb") as file:
        model, poly = pickle.load(file)  # Tách riêng model và poly
except Exception as e:
    messagebox.showerror("Lỗi", f"Không thể tải mô hình dự đoán: {e}")
    exit()

# Hàm dự đoán giá nhà
def predict_price():
    try:
        area = float(entry_area.get())
        bedrooms = int(entry_bedrooms.get()) if entry_bedrooms.get() else 0
        bathrooms = int(entry_bathrooms.get()) if entry_bathrooms.get() else 0
        floors = int(entry_floors.get()) if entry_floors.get() else 0
        width = float(entry_width.get()) if entry_width.get() else 0.0

        features = [[area, bedrooms, bathrooms, floors, width]]
        features_poly = poly.transform(features)  # Biến đổi đặc trưng đầu vào
        prediction = model.predict(features_poly)[0]  # Dự đoán giá nhà
        prediction_in_billion = prediction / 1e18  # Chuyển đổi sang đơn vị tỷ

        messagebox.showinfo("Kết quả", f"Giá dự đoán: {prediction_in_billion:.2f} tỷ VND")
    except ValueError:
        messagebox.showerror("Lỗi", "Vui lòng nhập đúng định dạng số!")

# Hàm gợi ý khu vực
def suggest_area(event=None):
    input_text = area_input.get().lower()
    suggestions = [area for area in districts if input_text in area.lower()] if input_text else districts
    suggestion_list.delete(0, 'end')
    for suggestion in suggestions:
        suggestion_list.insert('end', suggestion)

def select_area(event):
    selected_area = suggestion_list.get(suggestion_list.curselection())
    area_input.set(selected_area)

# Danh sách các khu vực
districts = [
    "Ba Đình", "Hoàn Kiếm", "Tây Hồ", "Long Biên", "Cầu Giấy", "Đống Đa", 
    "Hai Bà Trưng", "Hoàng Mai", "Thanh Xuân", "Hà Đông", "Bắc Từ Liêm", 
    "Nam Từ Liêm", "Sơn Tây", "Ba Vì", "Chương Mỹ", "Đan Phượng", 
    "Đông Anh", "Gia Lâm", "Hoài Đức", "Mê Linh", "Mỹ Đức", "Phú Xuyên", 
    "Quốc Oai", "Sóc Sơn", "Thạch Thất", "Thanh Oai", 
    "Thanh Trì", "Thường Tín"
]

# Giao diện chính
root = tk.Tk()
root.title("Dự đoán giá nhà")
root.geometry("500x500")

# Nhập khu vực
tk.Label(root, text="Nhập khu vực:").pack()
area_input = StringVar()
area_entry = tk.Entry(root, textvariable=area_input)
area_entry.pack()
area_entry.bind('<KeyRelease>', suggest_area)

suggestion_list = Listbox(root, height=5)
suggestion_list.pack()
suggestion_list.bind('<<ListboxSelect>>', select_area)

# Hiển thị tất cả các khu vực ban đầu
suggest_area()

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

root.mainloop()