import psycopg2
import os
import pickle
import numpy as np
from datetime import datetime

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
            WHERE "House_id" NOT IN (
	            SELECT MIN("House_id")
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

def select_area(area, page=1, per_page=10):
    """
    Hàm truy vấn nhà theo khu vực.
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

        # Tính offset dựa trên số trang
        offset = (page - 1) * per_page

        # Lấy tổng số bất động sản
        cur.execute("SELECT COUNT(*) FROM public.property")
        total_properties = cur.fetchone()[0]
        total_pages = (total_properties + per_page - 1) // per_page

        # Lấy danh sách bất động sản cho trang hiện tại
        cur.execute(f"""
            SELECT house_id, title, district, price, area, bedrooms, bathrooms
            FROM public.property
            WHERE district ILIKE '%{area}%'
            ORDER BY house_id
            LIMIT {per_page}
            OFFSET {offset}
        """)
        
        properties = cur.fetchall()
        
        # Hiển thị thông tin
        print(f"\n=== Trang {page}/{total_pages} ===")
        print(f"Tổng số bất động sản: {total_properties}")
        print("\nDanh sách bất động sản:")
        print("-" * 100)
        print(f"{'ID':<8} {'Tiêu đề':<30} {'Quận/Huyện':<15} {'Giá (tỷ)':<10} {'Diện tích':<10} {'Phòng ngủ':<10} {'Phòng tắm':<10}")
        print("-" * 100)
        
        for prop in properties:
            house_id, title, district, price, area, bedrooms, bathrooms = prop
            formatted_price = format_price(price)
            print(f"{house_id:<8} {title[:30]:<30} {district[:15]:<15} {formatted_price:<10} {area:<10.1f} {bedrooms:<10} {bathrooms:<10}")
        
        print("-" * 100)
        print(f"Trang {page}/{total_pages}")
        
    except Exception as e:
        print(f"Lỗi: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

def select_price(price_low, price_up, page=1, per_page=10):
    """
    Hàm truy vấn nhà trong khoảng giá từ price_low đến price_up.
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

        # Tính offset dựa trên số trang
        offset = (page - 1) * per_page

        # Lấy tổng số bất động sản
        cur.execute("SELECT COUNT(*) FROM public.property")
        total_properties = cur.fetchone()[0]
        total_pages = (total_properties + per_page - 1) // per_page

        # Lấy danh sách bất động sản cho trang hiện tại
        cur.execute(f"""
            SELECT house_id, title, district, price, area, bedrooms, bathrooms
            FROM public.property
            WHERE price >= {price_low} AND price <= {price_up}
            ORDER BY house_id
            LIMIT {per_page}
            OFFSET {offset}
        """)
        
        properties = cur.fetchall()
        
        # Hiển thị thông tin
        print(f"\n=== Trang {page}/{total_pages} ===")
        print(f"Tổng số bất động sản: {total_properties}")
        print("\nDanh sách bất động sản:")
        print("-" * 100)
        print(f"{'ID':<8} {'Tiêu đề':<30} {'Quận/Huyện':<15} {'Giá (tỷ)':<10} {'Diện tích':<10} {'Phòng ngủ':<10} {'Phòng tắm':<10}")
        print("-" * 100)
        
        for prop in properties:
            house_id, title, district, price, area, bedrooms, bathrooms = prop
            formatted_price = format_price(price)
            print(f"{house_id:<8} {title[:30]:<30} {district[:15]:<15} {formatted_price:<10} {area:<10.1f} {bedrooms:<10} {bathrooms:<10}")
        
        print("-" * 100)
        print(f"Trang {page}/{total_pages}")
        
    except Exception as e:
        print(f"Lỗi: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

def select_area_price(area, price_low, price_up, page=1, per_page=10):
    """
    Hàm truy vấn nhà trong khoảng giá và khu vực.
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

        # Tính offset dựa trên số trang
        offset = (page - 1) * per_page

        # Lấy tổng số bất động sản
        cur.execute("SELECT COUNT(*) FROM public.property")
        total_properties = cur.fetchone()[0]
        total_pages = (total_properties + per_page - 1) // per_page

        # Lấy danh sách bất động sản cho trang hiện tại
        cur.execute(f"""
            SELECT house_id, title, district, price, area, bedrooms, bathrooms
            FROM public.property
            WHERE district ILIKE '%{area}%' AND price >= {price_low} AND price <= {price_up}
            ORDER BY house_id
            LIMIT {per_page}
            OFFSET {offset}
        """)
        
        properties = cur.fetchall()
        
        # Hiển thị thông tin
        print(f"\n=== Trang {page}/{total_pages} ===")
        print(f"Tổng số bất động sản: {total_properties}")
        print("\nDanh sách bất động sản:")
        print("-" * 100)
        print(f"{'ID':<8} {'Tiêu đề':<30} {'Quận/Huyện':<15} {'Giá (tỷ)':<10} {'Diện tích':<10} {'Phòng ngủ':<10} {'Phòng tắm':<10}")
        print("-" * 100)
        
        for prop in properties:
            house_id, title, district, price, area, bedrooms, bathrooms = prop
            formatted_price = format_price(price)
            print(f"{house_id:<8} {title[:30]:<30} {district[:15]:<15} {formatted_price:<10} {area:<10.1f} {bedrooms:<10} {bathrooms:<10}")
        
        print("-" * 100)
        print(f"Trang {page}/{total_pages}")
        
    except Exception as e:
        print(f"Lỗi: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

def add_to_favorite(user_id, house_id):
    """
    Hàm thêm nhà vào danh sách yêu thích của người dùng.
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
        # Thêm nhà vào danh sách yêu thích
        cur.execute(f"""
            INSERT INTO public.favorite (user_id, house_id)
            VALUES ('{user_id}', '{house_id}')
        """)
        conn.commit()
        print("Đã thêm nhà vào danh sách yêu thích.")
    
    except Exception as e:
        print(f"Lỗi: {e}")

def remove_from_favorite(user_id, house_id):
    """
    Hàm xóa nhà khỏi danh sách yêu thích của người dùng.
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
        # Xóa nhà khỏi danh sách yêu thích
        cur.execute(f"""
            DELETE FROM public.favorite
            WHERE user_id = '{user_id}' AND house_id = '{house_id}'
        """)
        conn.commit()
        print("Đã xóa nhà khỏi danh sách yêu thích.")
    
    except Exception as e:
        print(f"Lỗi: {e}")

def get_favorite_list(user_id):
    """
    Hàm lấy và hiển thị danh sách nhà yêu thích của người dùng.
    Args:
        user_id (int): ID của người dùng
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
        
        # Lấy danh sách nhà yêu thích
        cur.execute(f"""
            SELECT p.house_id, p.title, p.district, p.price, p.area, p.bedrooms, p.bathrooms 
            FROM public.favorite f
            JOIN public.property p ON f.house_id = p.house_id
            WHERE f.user_id = '{user_id}'
            ORDER BY p.house_id
        """)
        
        properties = cur.fetchall()
        
        if not properties:
            print(f"\nKhông tìm thấy nhà yêu thích nào cho người dùng ID: {user_id}")
            return
        
        # Hiển thị thông tin
        print(f"\n=== Danh sách nhà yêu thích của người dùng ID: {user_id} ===")
        print(f"Tổng số nhà yêu thích: {len(properties)}")
        print("\nDanh sách bất động sản:")
        print("-" * 100)
        print(f"{'ID':<8} {'Tiêu đề':<30} {'Quận/Huyện':<15} {'Giá (tỷ)':<10} {'Diện tích':<10} {'Phòng ngủ':<10} {'Phòng tắm':<10}")
        print("-" * 100)
        
        for prop in properties:
            house_id, title, district, price, area, bedrooms, bathrooms = prop
            formatted_price = format_price(price)
            print(f"{house_id:<8} {title[:30]:<30} {district[:15]:<15} {formatted_price:<10} {area:<10.1f} {bedrooms:<10} {bathrooms:<10}")
        
        print("-" * 100)
    
    except Exception as e:
        print(f"Lỗi: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

def format_price(price_str):
    """
    Chuyển đổi giá từ chuỗi sang số tỉ đồng
    """
    try:
        # Loại bỏ các ký tự không cần thiết
        price_str = str(price_str).replace('tỷ', '').replace(',', '.').strip()
        # Chuyển đổi sang số
        price = float(price_str)
        # Chuyển đổi sang tỉ đồng và làm tròn 2 chữ số thập phân
        return f"{price/1e9:.2f}"
    except:
        return price_str

def display_properties(page=1, per_page=10):
    """
    Hiển thị danh sách bất động sản theo trang.
    Args:
        page (int): Số trang hiện tại (mặc định là 1)
        per_page (int): Số bất động sản trên mỗi trang (mặc định là 10)
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

        # Tính offset dựa trên số trang
        offset = (page - 1) * per_page

        # Lấy tổng số bất động sản
        cur.execute("SELECT COUNT(*) FROM public.property")
        total_properties = cur.fetchone()[0]
        total_pages = (total_properties + per_page - 1) // per_page

        # Lấy danh sách bất động sản cho trang hiện tại
        cur.execute(f"""
            SELECT house_id, title, district, price, area, bedrooms, bathrooms
            FROM public.property
            ORDER BY house_id
            LIMIT {per_page}
            OFFSET {offset}
        """)
        
        properties = cur.fetchall()
        
        # Hiển thị thông tin
        print(f"\n=== Trang {page}/{total_pages} ===")
        print(f"Tổng số bất động sản: {total_properties}")
        print("\nDanh sách bất động sản:")
        print("-" * 100)
        print(f"{'ID':<8} {'Tiêu đề':<30} {'Quận/Huyện':<15} {'Giá (tỷ)':<10} {'Diện tích':<10} {'Phòng ngủ':<10} {'Phòng tắm':<10}")
        print("-" * 100)
        
        for prop in properties:
            house_id, title, district, price, area, bedrooms, bathrooms = prop
            formatted_price = format_price(price)
            print(f"{house_id:<8} {title[:30]:<30} {district[:15]:<15} {formatted_price:<10} {area:<10.1f} {bedrooms:<10} {bathrooms:<10}")
        
        print("-" * 100)
        print(f"Trang {page}/{total_pages}")
        
    except Exception as e:
        print(f"Lỗi: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

def display_properties_by_id(house_id):
    """
    Hàm hiển thị thông tin bất động sản dựa trên house_id.
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
        # Truy vấn thông tin bất động sản
        cur.execute(f"""
            SELECT * FROM public.property   
            WHERE house_id = '{house_id}'
        """)
        house = cur.fetchone()
        if house:
            print(f"{house[0]:<8} {house[1][:30]:<30} {house[2]:<15} {house[3]:<10} {house[4]:<10.1f} {house[5]:<10} {house[6]:<10}")
        else:
            print("Không tìm thấy thông tin bất động sản.")
        
        # Đóng kết nối
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Lỗi khi hiển thị thông tin bất động sản: {e}")

def user_login(user_id, password):
    """
    Hàm kiểm tra đăng nhập của người dùng.
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
        # Kiểm tra đăng nhập
        cur.execute(f"""
            SELECT * FROM public.users
            WHERE user_id = '{user_id}' AND password = '{password}'
        """)
        user = cur.fetchone()
        if user:
            print("Đăng nhập thành công.")
        else:
            cur.execute(f"""
            SELECT * FROM public.admin
            WHERE admin_id = '{user_id}' AND password = '{password}'
            """)
            admin = cur.fetchone()
            if admin:
                print("Admin đăng nhập thành công.")
            else:
                print("Đăng nhập thất bại.")
    
    except Exception as e:
        print(f"Lỗi: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

def user_register(user_id, username, password, phone):
    """
    Hàm đăng ký tài khoản người dùng.
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
        # Thêm tài khoản người dùng
        cur.execute(f"""
            INSERT INTO public.users (user_id, username, password, phone)
            VALUES ({user_id}, '{username}', '{password}', '{phone}')
        """)
        conn.commit()
        print("Đăng ký tài khoản thành công.")
    
    except Exception as e:
        print(f"Lỗi: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

def compare_house(house_id1, house_id2) :
    """
    Hàm so sánh hai bất động sản dựa trên các tiêu chí khác nhau.
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
        # Truy vấn thông tin bất động sản
        cur.execute(f"""
            SELECT * FROM public.house_prices
            WHERE house_id = '{house_id1}' OR house_id = '{house_id2}'
        """)
        properties = cur.fetchall()
        if len(properties) != 2:
            print("Không tìm thấy đủ số lượng bất động sản để so sánh.")
            return
        
        # Hiển thị thông tin theo chiều dọc
        print(f"\n=== So sánh bất động sản ===")
        
        # Lấy tên các cột
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'house_prices'
            ORDER BY ordinal_position
        """)
        columns = [col[0] for col in cur.fetchall()]
        
        # Hiển thị tiêu đề
        print(f"{'Tiêu chí':<20} {'Bất động sản 1':<30} {'Bất động sản 2':<30}")
        print("-" * 80)
        
        # Hiển thị dữ liệu theo từng tiêu chí
        for i, col in enumerate(columns):
            value1 = properties[0][i]
            value2 = properties[1][i]
            
            # Xử lý giá trị đặc biệt
            if col == 'Price':
                value1 = format_price(value1)
                value2 = format_price(value2)
                print(f"{col:<20} {str(value1) + ' tỷ':<30} {str(value2) + ' tỷ':<30}")
                continue
            
            # Chuyển đổi giá trị thành chuỗi
            value1_str = str(value1) if value1 is not None else "None"
            value2_str = str(value2) if value2 is not None else "None"
            
            # Xử lý giá trị dài bằng cách xuống dòng
            max_width = 30
            value1_lines = []
            value2_lines = []
            
            # Chia giá trị thành nhiều dòng nếu quá dài
            for i in range(0, len(value1_str), max_width):
                value1_lines.append(value1_str[i:i+max_width])
            for i in range(0, len(value2_str), max_width):
                value2_lines.append(value2_str[i:i+max_width])
            
            # Đảm bảo ít nhất có một dòng
            if not value1_lines:
                value1_lines = [""]
            if not value2_lines:
                value2_lines = [""]
            
            # In dòng đầu tiên với tên tiêu chí
            print(f"{col:<20} {value1_lines[0]:<30} {value2_lines[0]:<30}")
            
            # In các dòng tiếp theo nếu có
            max_lines = max(len(value1_lines), len(value2_lines))
            for j in range(1, max_lines):
                value1_line = value1_lines[j] if j < len(value1_lines) else ""
                value2_line = value2_lines[j] if j < len(value2_lines) else ""
                print(f"{'':<20} {value1_line:<30} {value2_line:<30}")
            
            # In dòng phân cách giữa các tiêu chí
            print("-" * 80)
            
    except Exception as e:
        print(f"Lỗi: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()           

def view_house_details(house_id):
    """
    Hàm hiển thị chi tiết thông tin của một bất động sản dựa trên house_id.
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
        # Truy vấn thông tin bất động sản
        cur.execute(f"""
            SELECT * FROM public.house_prices
            WHERE house_id = '{house_id}'
        """)
        house = cur.fetchone()
        
        if house:
            # Lấy tên các cột
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'house_prices'
                ORDER BY ordinal_position
            """)
            columns = [col[0] for col in cur.fetchall()]
            
            # Hiển thị thông tin chi tiết
            print(f"\n=== CHI TIẾT BẤT ĐỘNG SẢN ===")
            print(f"{'Mã bất động sản:':<20} {house_id}")
            print("-" * 80)
            
            # Hiển thị từng thông tin
            for i, col in enumerate(columns):
                value = house[i]
                
                # Xử lý giá trị đặc biệt
                if col == 'Price':
                    value = format_price(value)
                    print(f"{col:<20} {str(value) + ' tỷ':<30}")
                    continue
                
                # Chuyển đổi giá trị thành chuỗi
                value_str = str(value) if value is not None else "Không có thông tin"
                
                # Xử lý giá trị dài bằng cách xuống dòng
                max_width = 60
                value_lines = []
                
                # Chia giá trị thành nhiều dòng nếu quá dài
                for j in range(0, len(value_str), max_width):
                    value_lines.append(value_str[j:j+max_width])
                
                # Đảm bảo ít nhất có một dòng
                if not value_lines:
                    value_lines = [""]
                
                # In dòng đầu tiên với tên tiêu chí
                print(f"{col:<20} {value_lines[0]:<60}")
                
                # In các dòng tiếp theo nếu có
                for j in range(1, len(value_lines)):
                    print(f"{'':<20} {value_lines[j]:<60}")
                
                # In dòng phân cách giữa các tiêu chí
                print("-" * 80)
        else:
            print("Không tìm thấy thông tin bất động sản.")
    except Exception as e:
        print(f"Lỗi: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

def find_house(string):
    """
    Hàm tìm kiếm bất động sản dựa trên tên bất động sản.
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
        # Truy vấn bất động sản dựa trên tên
        cur.execute(f"""
            SELECT * FROM public.house_prices
            WHERE "Title" ILIKE '%{string}%' OR "Address" ILIKE '%{string}%' OR house_id ILIKE '%{string}%'
        """)
        houses = cur.fetchall()
        
        if houses:
            print(f"\nKết quả tìm kiếm cho '{string}':")
            print(f"{'ID':<8} {'Tiêu đề':<30} {'Quận/Huyện':<15} {'Giá (tỷ)':<10} {'Diện tích':<10} {'Phòng ngủ':<10} {'Phòng tắm':<10}")
            print("-" * 100)
            
            for house in houses:
                # Lấy các thông tin cần thiết từ kết quả truy vấn
                house_id = house[0]
                title = house[1]
                district = house[2]
                price = house[3]
                area = house[4]
                bedrooms = house[5]
                bathrooms = house[6]
                
                # Định dạng giá
                formatted_price = format_price(price)
                
                # Kiểm tra kiểu dữ liệu của area trước khi định dạng
                try:
                    area_value = float(area)
                    area_str = f"{area_value:<10.1f}"
                except (ValueError, TypeError):
                    area_str = f"{str(area):<10}"
                
                # In thông tin theo định dạng bảng
                print(f"{house_id:<8} {title[:30]:<30} {district[:15]:<15} {formatted_price:<10} {area_str} {bedrooms:<10} {bathrooms:<10}")
            
            print("-" * 100)
            print(f"Tìm thấy {len(houses)} kết quả.")
        else:
            print(f"Không tìm thấy bất động sản nào phù hợp với '{string}'.")
    
    except Exception as e:
        print(f"Lỗi khi tìm kiếm bất động sản: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

def predict_price(area, bedrooms, bathrooms, floors, width_meters):
    """
    Hàm dự đoán giá nhà dựa trên các tiêu chí đã cho.
    
    Args:
        area (float): Diện tích nhà (m²)
        bedrooms (int): Số phòng ngủ
        bathrooms (int): Số phòng tắm
        floors (int): Số tầng
        width_meters (float): Chiều rộng nhà (m)
        
    Returns:
        float: Giá nhà dự đoán (VND)
    """
    try:
        # Đường dẫn đến file model
        model_path = r"House_price_prediction/models/house_price_model.pkl"
        
        # Kiểm tra xem file model có tồn tại không
        if not os.path.exists(model_path):
            print(f"Không tìm thấy file model tại đường dẫn: {model_path}")
            return None
        
        # Tải model từ file
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        # Tạo mảng features từ dữ liệu đầu vào
        features = np.array([[area, bedrooms, bathrooms, floors, width_meters]])
        
        # Dự đoán giá
        prediction = model.predict(features)[0]
        
        # Định dạng giá
        formatted_price = format_price(prediction)
        
        # Hiển thị kết quả
        print("\n=== Kết quả dự đoán giá nhà ===")
        print(f"Diện tích: {area} m²")
        print(f"Số phòng ngủ: {bedrooms}")
        print(f"Số phòng tắm: {bathrooms}")
        print(f"Số tầng: {floors}")
        print(f"Chiều rộng: {width_meters} m")
        print(f"Giá dự đoán: {formatted_price} tỷ")
        
        return prediction
    
    except Exception as e:
        print(f"Lỗi khi dự đoán giá nhà: {e}")
        return None

def user_buy_house(id, house_id):
    """
    Hàm xử lý việc mua bất động sản của người dùng.
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
        #kiểm tra id là user hay admin
        cur.execute(f"""
            SELECT * FROM public.users
            WHERE user_id = '{id}'
        """)
        user = cur.fetchone()
        if user:
            cur.execute(f"""
            UPDATE public.statues
            SET statue = 'Đang xử lý'
            WHERE house_id = '{house_id}'
            """)
        conn.commit()
        print("Đã cập nhật trạng thái bất động sản.")
    except Exception as e:
        print(f"Lỗi: {e}")

def admin_update_house(admin_id, house_id, status):
    """
    Hàm cập nhật trạng thái bất động sản của admin.
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
        
        # Kiểm tra xem admin có tồn tại không
        cur.execute(f"""
            SELECT * FROM public.admin
            WHERE admin_id = '{admin_id}'
        """)
        admin = cur.fetchone()
        
        if admin:
            # Cập nhật trạng thái bất động sản
            cur.execute(f"""
                UPDATE public.statues
                SET statue = '{status}'
                WHERE house_id = '{house_id}'
            """)
            conn.commit()
            print(f"Đã cập nhật trạng thái bất động sản {house_id} thành '{status}'.")
        else:
            print("Admin không tồn tại.")
    
    except Exception as e:
        print(f"Lỗi: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

def user_sell_house(title, address, district, postType, price, area, bedrooms, bathrooms, floors, width_meters, legal, interior, entrancewidth):
    """
    Hàm xử lý việc bán bất động sản của người dùng.
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
        
        cur.execute("""
            SELECT house_id FROM public.wait_for_admin
            WHERE house_id LIKE 't%'
            ORDER BY house_id DESC
            LIMIT 1
        """)
        result = cur.fetchone()
        
        if result:
            last_id = result[0]
            num_part = int(last_id[1:]) + 1
            new_house_id = f"t{num_part:04d}"
        else:
            new_house_id = "t0001"
        
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        cur.execute("""
            INSERT INTO public.wait_for_admin 
            (house_id, "Title", "Address", "District", "PostingDate", "PostType", "Price", 
             "Area", "Bedrooms", "Bathrooms", "Floors", "Width_meters", "Legal", "Interior", "Entrancewidth")
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (new_house_id, title, address, district, current_date, postType, price, 
              area, bedrooms, bathrooms, floors, width_meters, legal, interior, entrancewidth))
        
        conn.commit()
        print(f"Đã thêm bất động sản vào danh sách chờ phê duyệt với ID: {new_house_id}")
        return new_house_id
    
    except Exception as e:
        print(f"Lỗi khi thêm bất động sản: {e}")
        return None
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()






