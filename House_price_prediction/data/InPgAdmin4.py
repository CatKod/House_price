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
            WHERE id NOT IN (
                SELECT MIN(public.house_prices.id)
                FROM public.house_prices
                GROUP BY email
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

# Gọi hàm delete_duplicates
delete_duplicates()

# Kết nối đến PostgreSQL
conn = psycopg2.connect(
    dbname="house_prices",
    user="postgres",
    password="271205",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# Đóng kết nối
cur.close()
conn.close()