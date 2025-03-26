import psycopg2

def delete_duplicates():
    """
    Hàm xóa các dòng dữ liệu trùng lặp trong bảng house_prices.
    """
    try:
        # Kết nối đến PostgreSQL
        conn = psycopg2.connect(
            dbname="house_prices",
            user="postgres",
            password="271205",
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()

        # Xóa các dòng trùng lặp dựa trên cột email, giữ lại dòng có id nhỏ nhất
        cur.execute("""
            DELETE FROM public.house_prices
            WHERE "ID" NOT IN (
	            SELECT MIN("ID")
                FROM public.house_prices
                GROUP BY "Title"
	            );
        """)
        conn.commit()
        print("Đã xóa các dòng dữ liệu trùng lặp.")
    except Exception as e:
        print(f"Lỗi: {e}")
    finally:
        # Đóng kết nối
        cur.close()
        conn.close()


def select_area(area):
    """
    Hàm truy vấn giá nhà trung bình theo khu vực.
    """
    try:
        # Kết nối đến PostgreSQL
        conn = psycopg2.connect(
            dbname="house_prices",
            user="postgres",
            password="271205",
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()
        # Truy vấn giá nhà trung bình theo khu vực
        cur.execute(f"""
            SELECT * FROM public.house_prices
            Where "District" like '%{area}%'
        """)
        conn.commit()
        print("Đã chọn theo khu vực.")
    
    except Exception as e:
        print(f"Lỗi: {e}")
    finally:
        # Đóng kết nối
        cur.close()
        conn.close()

