import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

# URL chứa dữ liệu giá nhà tại Hà Nội (dạng cơ bản để phân trang)
BASE_URL = "https://thuviennhadat.vn/bang-gia-dat/ha-noi"

def fetch_test_data():
    all_data = []
    page = 1

    # Chỉ lấy dữ liệu từ trang 1
    url = f"{BASE_URL}?trang={page}&FromPrice=0&ToPrice=0"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code != 200:
        print(f"⚠️ Không thể truy cập trang {page}!")
        return
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Tìm bảng dữ liệu trên trang
    table = soup.find("table")  # Giả sử dữ liệu nằm trong bảng
    if not table:
        print(f"⚠️ Không tìm thấy bảng dữ liệu trên trang {page}!")
        return

    # Đọc dữ liệu từ bảng
    rows = table.find_all("tr")
    if len(rows) <= 1:  # Nếu không có dữ liệu (chỉ có tiêu đề)
        print(f"⚠️ Không có dữ liệu trên trang {page}!")
        return

    for row in rows[1:]:  # Bỏ qua tiêu đề
        cols = row.find_all("td")
        all_data.append([col.text.strip() for col in cols])
    
    print(f"✅ Đã lấy dữ liệu từ trang {page}")

    # Chuyển thành DataFrame
    if all_data:
        df = pd.DataFrame(all_data, columns=["STT", "Quận/Huyện", "Tên đường/Làng xã", "Đoạn: Từ - Đến", "Vị trí 1", "Vị trí 2", "Vị trí 3", "Vị trí 4", "Vị trí 5", "Loại đất"][:len(all_data[0])])
        
        # Tách cột "Đoạn: Từ - Đến" thành "Địa chỉ" và "Ngày update"
        df[["Địa chỉ", "Ngày update"]] = df["Đoạn: Từ - Đến"].str.extract(r"(.+)\s+(\d{8}-\w+)")
        df.drop(columns=["Đoạn: Từ - Đến"], inplace=True)

        # Lưu dữ liệu vào file CSV
        file_path = "House_Price_Prediction/data/test_house_prices.csv"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        df.to_csv(file_path, index=False, encoding="utf-8-sig")
        
        print(f"✅ Dữ liệu đã được lưu vào {file_path}")
    else:
        print("⚠️ Không có dữ liệu để lưu!")

if __name__ == "__main__":
    fetch_test_data()
