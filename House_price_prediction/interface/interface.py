import psycopg2
import os
import pickle
import numpy as np
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
from decimal import Decimal, InvalidOperation

app = Flask(__name__)
app.secret_key = 'cat_and_code'

# Database connection configuration
DB_CONFIG = {
    'dbname': 'house_prices',
    'user': 'postgres',
    'password': '271205',
    'host': 'localhost',
    'port': '5432'
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def format_price(price):
    try:
        price_str = str(price)
        if price_str.lower() in ['thỏa thuận', 'thoả thuận']:
            return price_str
        price_float = float(price)
        return f"{price_float/1e9:.2f} tỷ"
    except Exception:
        return str(price)

@app.route('/')
def index():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Lấy tổng số bất động sản đang bán
        cur.execute("""
            SELECT COUNT(*) FROM public.property p
            JOIN public.statues s ON p.house_id = s.house_id
            WHERE s.statue = 'Đang bán'
        """)
        total_properties = cur.fetchone()[0]

        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        offset = (page - 1) * per_page
        total_pages = (total_properties + per_page - 1) // per_page

        # Lấy danh sách bất động sản đang bán cho trang hiện tại
        cur.execute("""
            SELECT p.house_id, p.title, p.district, p.price, p.area, p.bedrooms, p.bathrooms
            FROM public.property p
            JOIN public.statues s ON p.house_id = s.house_id
            WHERE s.statue = 'Đang bán'
            ORDER BY p.house_id
            LIMIT %s OFFSET %s
        """, (per_page, offset))
        properties = cur.fetchall()

        # Format properties
        formatted_properties = []
        for prop in properties:
            formatted_properties.append({
                'house_id': prop[0],
                'title': prop[1],
                'district': prop[2],
                'price': format_price(prop[3]),
                'area': prop[4],
                'bedrooms': prop[5],
                'bathrooms': prop[6]
            })

        # Lấy thống kê theo quận/huyện (chỉ tính các căn đang bán)
        cur.execute("""
            SELECT p.district, COUNT(*) as count
            FROM public.property p
            JOIN public.statues s ON p.house_id = s.house_id
            WHERE s.statue = 'Đang bán'
            GROUP BY p.district
            ORDER BY count DESC
            LIMIT 10
        """)
        district_stats = cur.fetchall()

        # Lấy giá trung bình theo quận/huyện (chỉ tính các căn đang bán)
        cur.execute("""
            SELECT p.district, AVG(p.price::numeric) as avg_price
            FROM public.property p
            JOIN public.statues s ON p.house_id = s.house_id
            WHERE s.statue = 'Đang bán' AND p.price ~ '^[0-9]+(\\.[0-9]+)?$'
            GROUP BY p.district
            ORDER BY avg_price DESC
            LIMIT 10
        """)
        avg_price_stats = cur.fetchall()

        cur.close()
        conn.close()

        return render_template('index.html',
                             properties=formatted_properties,
                             total_properties=total_properties,
                             current_page=page,
                             total_pages=total_pages,
                             per_page=per_page,
                             district_stats=district_stats,
                             avg_price_stats=avg_price_stats)

    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return render_template('error.html', message=f'Đã xảy ra lỗi: {str(e)}')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']
        
        try:
            conn = get_db_connection()
            cur = conn.cursor()

            # Check if admin exists
            cur.execute("""
                SELECT * FROM public.admin
                WHERE admin_id = %s AND password = %s
            """, (user_id, password))
            admin = cur.fetchone()
            if admin:
                session['user_id'] = user_id
                session['username'] = admin[1]  # admin_name is at index 1
                session['is_admin'] = True
                flash('Admin đăng nhập thành công!', 'success')
                return redirect(url_for('index'))

            # Check if user exists
            cur.execute("""
                SELECT * FROM public.users
                WHERE user_id = %s AND password = %s
            """, (user_id, password))
            user = cur.fetchone()

            if user:
                session['user_id'] = user_id
                session['username'] = user[1]  # username is at index 1
                session['is_admin'] = False
                flash('Login successful!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid credentials', 'error')

            cur.close()
            conn.close()

        except Exception as e:
            flash(f'Error: {str(e)}', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/property/<house_id>')
def property_details(house_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Lấy thông tin chi tiết từ bảng property (để tương thích cũ)
        cur.execute("""
            SELECT * FROM public.property
            WHERE house_id = %s
        """, (house_id,))
        property_row = cur.fetchone()

        # Lấy thông tin chi tiết từ bảng house_prices (ưu tiên hiển thị đầy đủ)
        cur.execute("""
            SELECT * FROM public.house_prices
            WHERE house_id = %s
        """, (house_id,))
        house_prices_row = cur.fetchone()
        house_prices_columns = [desc[0] for desc in cur.description]

        property = None
        if property_row:
            property = {
                'house_id': property_row[0],
                'title': property_row[1],
                'district': property_row[2],
                'price': format_price(property_row[3]),
                'area': property_row[4],
                'bedrooms': property_row[5],
                'bathrooms': property_row[6]
            }        
            house_prices = None
        if house_prices_row:
            house_prices = dict(zip(house_prices_columns, house_prices_row))
            # Format the price if it exists in house_prices
            if 'Price' in house_prices:
                house_prices['Price'] = format_price(house_prices['Price'])

        cur.close()
        conn.close()

        if not property and not house_prices:
            return render_template('error.html', message='Property not found')

        return render_template('property_details.html', property=property, house_prices=house_prices)
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return render_template('error.html', message=e)

@app.route('/search')
def search():
    try:
        search_term = request.args.get('q', '')
        district = request.args.get('district', '')
        price_min = request.args.get('price_min', '')
        price_max = request.args.get('price_max', '')
        area_min = request.args.get('area_min', '')
        area_max = request.args.get('area_max', '')
        bedrooms = request.args.get('bedrooms', '')
        sort_by = request.args.get('sort_by', 'house_id')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        offset = (page - 1) * per_page

        conn = get_db_connection()
        cur = conn.cursor()

        # Build dynamic WHERE clause
        where_clauses = ['s.statue = %s']  # Always filter by "Đang bán" status
        params = ['Đang bán']
        
        if search_term:
            where_clauses.append('(p.title ILIKE %s OR p.district ILIKE %s OR p.house_id ILIKE %s)')
            params.extend([f'%{search_term}%'] * 3)
        if district:
            where_clauses.append('p.district = %s')
            params.append(district)
        if price_min:
            where_clauses.append("p.price ~ '^[0-9]+(\\.[0-9]+)?$' AND p.price::numeric >= %s")
            params.append(float(price_min) * 1e9)
        if price_max:
            where_clauses.append("p.price ~ '^[0-9]+(\\.[0-9]+)?$' AND p.price::numeric <= %s")
            params.append(float(price_max) * 1e9)
        if area_min:
            where_clauses.append('p.area >= %s')
            params.append(float(area_min))
        if area_max:
            where_clauses.append('p.area <= %s')
            params.append(float(area_max))
        if bedrooms:
            where_clauses.append('p.bedrooms >= %s')
            params.append(int(bedrooms))

        where_sql = 'WHERE ' + ' AND '.join(where_clauses)
        order_by_clauses = {
            'house_id': 'ORDER BY p.house_id ASC',
            'newest': 'ORDER BY p.house_id DESC',
            'price_low': 'ORDER BY CASE WHEN p.price ~ \'^[0-9]+(\\.[0-9]+)?$\' THEN p.price::numeric ELSE 999999999999 END ASC',
            'price_high': 'ORDER BY CASE WHEN p.price ~ \'^[0-9]+(\\.[0-9]+)?$\' THEN p.price::numeric ELSE 0 END DESC',
            'area_large': 'ORDER BY p.area DESC'
        }
        order_by_sql = order_by_clauses.get(sort_by, order_by_clauses['house_id'])

        # Get total count
        count_sql = f"""
            SELECT COUNT(*) 
            FROM public.property p
            JOIN public.statues s ON p.house_id = s.house_id
            {where_sql}
        """
        cur.execute(count_sql, params)
        total_properties = cur.fetchone()[0]
        total_pages = (total_properties + per_page - 1) // per_page

        # Get search results
        search_sql = f"""
            SELECT *
            FROM public.property p
            JOIN public.statues s ON p.house_id = s.house_id
            {where_sql}
            {order_by_sql}
            LIMIT %s OFFSET %s
        """
        cur.execute(search_sql, params + [per_page, offset])
        properties = cur.fetchall()

        # Format properties
        formatted_properties = []
        for prop in properties:
            formatted_properties.append({
                'house_id': prop[0],
                'title': prop[1],
                'district': prop[2],
                'price': format_price(prop[3]),
                'area': prop[4],
                'bedrooms': prop[5],
                'bathrooms': prop[6]
            })

        # Lấy danh sách quận/huyện cho dropdown (chỉ các quận có bất động sản đang bán)
        cur.execute("""
            SELECT DISTINCT p.district 
            FROM public.property p
            JOIN public.statues s ON p.house_id = s.house_id
            WHERE s.statue = 'Đang bán'
            ORDER BY p.district
        """)
        districts = [row[0] for row in cur.fetchall()]

        cur.close()
        conn.close()

        return render_template('search.html',
                             properties=formatted_properties,
                             search_term=search_term,
                             current_page=page,
                             total_pages=total_pages,
                             total_properties=total_properties,
                             per_page=per_page,
                             districts=districts,
                             selected_district=district,
                             price_min=price_min,
                             price_max=price_max,
                             area_min=area_min,
                             area_max=area_max,
                             bedrooms=bedrooms,
                             sort_by=sort_by)

    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return render_template('error.html', message='An error occurred while searching')

@app.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    if request.method == 'POST':
        try:
            area = float(request.form['area'])
            bedrooms = int(request.form['bedrooms'])
            bathrooms = int(request.form['bathrooms'])
            floors = int(request.form['floors'])
            width_meters = float(request.form['width_meters'])

            # Load the model
            model_path = os.path.join('C:/Users/kimvi/OneDrive - Hanoi University of Science and Technology/GitHub/My_AI_Project/House_price_prediction/House_price_prediction/models/house_price_model.pkl')
            if not os.path.exists(model_path):
                flash('Model file not found', 'error')
                return redirect(url_for('predict'))

            with open(model_path, 'rb') as f:
                model = pickle.load(f)

            # Make prediction
            features = np.array([[area, bedrooms, bathrooms, floors, width_meters]])
            prediction = model.predict(features)[0]
            formatted_price = format_price(prediction)

            return render_template('predict.html',
                                 prediction=formatted_price,
                                 area=area,
                                 bedrooms=bedrooms,
                                 bathrooms=bathrooms,
                                 floors=floors,
                                 width_meters=width_meters)

        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('predict'))

    return render_template('predict.html')

@app.route('/compare', methods=['GET', 'POST'])
@login_required
def compare():    # Redirect admin users away from compare functionality
    if session.get('is_admin'):
        flash('Chức năng so sánh không khả dụng cho admin.', 'info')
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        try:
            house_id1 = request.form['house_id1']
            house_id2 = request.form['house_id2']

            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute("""
                SELECT *
                FROM public.house_prices hp
                JOIN public.statues s ON hp.house_id = s.house_id
                WHERE (hp.house_id = %s OR hp.house_id = %s) AND s.statue = 'Đang bán'
            """, (house_id1, house_id2))
            properties = cur.fetchall()

            if len(properties) != 2:
                flash('One or both properties not found', 'error')
                return redirect(url_for('compare'))
            
            # Format properties
            formatted_properties = []
            for prop in properties:
                # Convert price string to float for comparison
                try:
                    raw_price = float(str(prop[6]).replace('tỷ', '').replace(',', '.').strip()) / 1e9 if 'tỷ' in str(prop[6]) else float(prop[6]) / 1e9
                except:
                    raw_price = 0
                
                formatted_properties.append({
                    'house_id': prop[0],
                    'title': prop[1],
                    'address': prop[2],
                    'district': prop[3],
                    'posting_date': prop[4],
                    'post_type': prop[5],
                    'price': raw_price,  # Numeric price for comparison
                    'price_formatted': format_price(prop[6]),  # Formatted price for display
                    'area': prop[7],
                    'direction': prop[8],
                    'bedrooms': prop[9],
                    'bathrooms': prop[10],
                    'floors': prop[11],
                    'width_meters': prop[12],
                    'legal': prop[13],
                    'interior': prop[14],
                    'entrance_width': prop[15]
                })

            return render_template('compare.html', properties=formatted_properties)

        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('compare'))

    return render_template('compare.html')

@app.route('/favorites')
@login_required
def favorites():
    # Redirect admin users away from favorites functionality
    if session.get('is_admin'):
        flash('Chức năng yêu thích không khả dụng cho admin.', 'info')
        return redirect(url_for('index'))
        
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT p.* FROM public.property p
            JOIN public.favorite f ON p.house_id = f.house_id
            JOIN public.statues s ON p.house_id = s.house_id
            WHERE f.user_id = %s AND s.statue = 'Đang bán'
            ORDER BY p.house_id
        """, (session['user_id'],))
        properties = cur.fetchall()

        # Format properties
        formatted_properties = []
        for prop in properties:
            formatted_properties.append({
                'house_id': prop[0],
                'title': prop[1],
                'district': prop[2],
                'price': format_price(prop[3]),
                'area': prop[4],
                'bedrooms': prop[5],
                'bathrooms': prop[6]
            })

        cur.close()
        conn.close()

        return render_template('favorites.html', properties=formatted_properties)

    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return render_template('error.html', message='An error occurred while loading favorites')

@app.route('/add_favorite/<house_id>', methods=['POST'])
@login_required
def add_favorite(house_id):
    # Redirect admin users away from favorites functionality
    if session.get('is_admin'):
        flash('Chức năng yêu thích không khả dụng cho admin.', 'info')
        return redirect(url_for('property_details', house_id=house_id))
        
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO public.favorite (user_id, house_id)
            VALUES (%s, %s)
        """, (session['user_id'], house_id))
        conn.commit()

        flash('Property added to favorites', 'success')
        return redirect(url_for('property_details', house_id=house_id))

    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('property_details', house_id=house_id))

    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

@app.route('/remove_favorite/<house_id>', methods=['POST'])
@login_required
def remove_favorite(house_id):
    # Redirect admin users away from favorites functionality
    if session.get('is_admin'):
        flash('Chức năng yêu thích không khả dụng cho admin.', 'info')
        return redirect(url_for('property_details', house_id=house_id))
        
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            DELETE FROM public.favorite
            WHERE user_id = %s AND house_id = %s
        """, (session['user_id'], house_id))
        conn.commit()

        flash('Property removed from favorites', 'success')
        return redirect(url_for('property_details', house_id=house_id))

    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('property_details', house_id=house_id))

    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_id = request.form['user_id']
        username = request.form['username']
        password = request.form['password']
        phone = request.form['phone']
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            # Kiểm tra user_id đã tồn tại chưa
            cur.execute("SELECT * FROM public.users WHERE user_id = %s", (user_id,))
            if cur.fetchone():
                flash('ID người dùng đã tồn tại. Vui lòng chọn ID khác.', 'error')
                return render_template('register.html')
            # Thêm tài khoản mới
            cur.execute("INSERT INTO public.users (user_id, username, password, phone) VALUES (%s, %s, %s, %s)",
                        (user_id, username, password, phone))
            conn.commit()
            cur.close()
            conn.close()
            flash('Đăng ký thành công! Bạn có thể đăng nhập.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Lỗi: {str(e)}', 'error')
            return render_template('register.html')
    return render_template('register.html')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Bạn không có quyền truy cập chức năng này.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/update_status/<house_id>', methods=['GET', 'POST'])
@admin_required
def update_status(house_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        if request.method == 'POST':
            new_status = request.form['statue']
            cur.execute("""
                UPDATE public.statues
                SET statue = %s
                WHERE house_id = %s
            """, (new_status, house_id))
            conn.commit()
            flash('Cập nhật trạng thái thành công!', 'success')
            return redirect(url_for('property_details', house_id=house_id))
        # Lấy trạng thái hiện tại
        cur.execute("SELECT statue FROM public.statues WHERE house_id = %s", (house_id,))
        current_status = cur.fetchone()[0]
        cur.close()
        conn.close()
        return render_template('update_status.html', house_id=house_id, current_status=current_status)
    except Exception as e:
        flash(f'Lỗi: {str(e)}', 'error')
        return redirect(url_for('property_details', house_id=house_id))

@app.route('/admin/users')
@admin_required
def admin_users():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT user_id, username, phone FROM public.users ORDER BY user_id")
        users = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('admin_users.html', users=users)
    except Exception as e:
        flash(f'Lỗi: {str(e)}', 'error')
        return render_template('error.html', message='Không thể tải danh sách người dùng')

@app.route('/admin/delete_user/<user_id>', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Xóa user khỏi bảng users
        cur.execute("DELETE FROM public.users WHERE user_id = %s", (user_id,))
        # Xóa các bản ghi liên quan: favorite, deposit (nếu có)
        cur.execute("DELETE FROM public.favorite WHERE user_id = %s", (user_id,))
        cur.execute("DELETE FROM public.deposit WHERE user_id = %s", (user_id,))
        conn.commit()
        cur.close()
        conn.close()
        flash('Đã xóa user thành công.', 'success')
        return redirect(url_for('admin_users'))
    except Exception as e:
        flash(f'Lỗi: {str(e)}', 'error')
        return redirect(url_for('admin_users'))

@app.route('/deposit/<house_id>', methods=['GET', 'POST'])
@login_required
def deposit(house_id):
    if request.method == 'POST':
        # Đặt cọc, chuyển sang trang xác nhận
        return redirect(url_for('confirm_deposit', house_id=house_id))
    return render_template('deposit.html', house_id=house_id)

@app.route('/confirm_deposit/<house_id>', methods=['GET', 'POST'])
@login_required
def confirm_deposit(house_id):
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            # Cập nhật trạng thái nhà sang "Đang xử lý"
            cur.execute("""
                UPDATE public.statues
                SET statue = %s
                WHERE house_id = %s
            """, ('Đang xử lý', house_id))
            # Thêm vào bảng deposit
            cur.execute("""
                INSERT INTO public.deposit (user_id, house_id)
                VALUES (%s, %s)
            """, (session['user_id'], house_id))
            conn.commit()
            cur.close()
            conn.close()
            flash('Đặt cọc thành công! Trạng thái nhà đã chuyển sang Đang xử lý.', 'success')
            return redirect(url_for('property_details', house_id=house_id))
        except Exception as e:
            flash(f'Lỗi: {str(e)}', 'error')
            return redirect(url_for('property_details', house_id=house_id))
    return render_template('confirm_deposit.html', house_id=house_id)

@app.route('/my_deposits')
@login_required
def my_deposits():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Lấy danh sách các nhà mà user này đã đặt cọc (statue = 'Đang xử lý' và user_id là người đặt cọc)
        cur.execute("""
            SELECT p.house_id, p.title, p.district, p.price, p.area, p.bedrooms, p.bathrooms
            FROM public.property p
            JOIN public.statues s ON p.house_id = s.house_id
            JOIN public.deposit d ON p.house_id = d.house_id
            WHERE s.statue = 'Đang xử lý' AND d.user_id = %s
            ORDER BY p.house_id
        """, (session['user_id'],))
        properties_raw = cur.fetchall()
        
        properties = []
        for prop in properties_raw:
            properties.append((
                prop[0],
                prop[1],
                prop[2],
                format_price(prop[3]),
                prop[4], 
                prop[5],
                prop[6]
            ))
        
        cur.close()
        conn.close()
        return render_template('my_deposits.html', properties=properties)
    except Exception as e:
        flash(f'Lỗi: {str(e)}', 'error')
        return render_template('error.html', message='Không thể tải danh sách đặt cọc')

@app.route('/admin/processing')
@admin_required
def admin_processing():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Lấy tất cả nhà đang xử lý
        cur.execute("""
            SELECT p.house_id, p.title, p.district, p.price, p.area, p.bedrooms, p.bathrooms, d.user_id
            FROM public.property p
            JOIN public.statues s ON p.house_id = s.house_id
            JOIN public.deposit d ON p.house_id = d.house_id
            WHERE s.statue = 'Đang xử lý'
            ORDER BY p.house_id
        """)
        properties = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('admin_processing.html', properties=properties)
    except Exception as e:
        flash(f'Lỗi: {str(e)}', 'error')
        return render_template('error.html', message='Không thể tải danh sách bất động sản đang xử lý')

@app.route('/cancel_deposit/<house_id>', methods=['POST'])
@login_required
def cancel_deposit(house_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM public.deposit WHERE user_id = %s AND house_id = %s", (session['user_id'], house_id))
        cur.execute("SELECT COUNT(*) FROM public.deposit WHERE house_id = %s", (house_id,))
        if cur.fetchone()[0] == 0:
            cur.execute("UPDATE public.statues SET statue = 'Đang bán' WHERE house_id = %s", (house_id,))
        conn.commit()
        cur.close()
        conn.close()
        flash('Đã hủy đặt cọc thành công.', 'success')
        return redirect(url_for('my_deposits'))
    except Exception as e:
        flash(f'Lỗi: {str(e)}', 'error')
        return redirect(url_for('my_deposits'))

@app.route('/admin/cancel_processing/<house_id>', methods=['POST'])
@admin_required
def admin_cancel_processing(house_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM public.deposit WHERE house_id = %s", (house_id,))
        cur.execute("UPDATE public.statues SET statue = 'Đang bán' WHERE house_id = %s", (house_id,))
        conn.commit()
        cur.close()
        conn.close()
        flash('Đã hủy xử lý bất động sản thành công.', 'success')
        return redirect(url_for('admin_processing'))
    except Exception as e:
        flash(f'Lỗi: {str(e)}', 'error')
        return redirect(url_for('admin_processing'))

@app.route('/post_house', methods=['GET', 'POST'])
@login_required
def post_house():
    """Route for posting house listings - both admin and user"""
    if request.method == 'POST':
        try:            # Extract form data
            title = request.form['title']
            address = request.form['address']
            district = request.form['district']
            post_type = request.form['post_type']
            price = request.form['price']
            
            # Remove commas from price if it's a number (not "Thỏa thuận")
            if price not in ['Thỏa thuận', 'Thoả thuận']:
                price = price.replace(',', '')
            
            area = float(request.form['area'])
            direction = request.form.get('direction', '')
            bedrooms = int(request.form['bedrooms'])
            bathrooms = int(request.form['bathrooms'])
            floors = int(request.form['floors'])
            width_meters = float(request.form['width_meters'])
            legal = request.form['legal']
            interior = request.form['interior']
            entrancewidth = float(request.form.get('entrancewidth', 0))

            conn = get_db_connection()
            cur = conn.cursor()

            if session.get('is_admin'):
                # Admin post - goes directly to database
                # Generate new house_id for admin posts
                cur.execute("""
                    SELECT house_id FROM public.house_prices
                    WHERE house_id ~ '^[0-9]+$'
                    ORDER BY house_id::integer DESC
                    LIMIT 1
                """)
                result = cur.fetchone()
                
                if result:
                    last_id = int(result[0])
                    new_house_id = f"{last_id + 1:05d}"
                else:
                    new_house_id = "00001"
                
                current_date = datetime.now().strftime("%Y-%m-%d")
                  # Insert into house_prices table
                cur.execute("""
                    INSERT INTO public.house_prices 
                    (house_id, "Title", "Address", "District", "PostingDate", "PostType", "Price", 
                     "Area", "Direction", "Bedrooms", "Bathrooms", "Floors", "Width_meters", "Legal", "Interior", "Entrancewidth")
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (new_house_id, title, address, district, current_date, post_type, price, 
                      area, direction, bedrooms, bathrooms, floors, width_meters, legal, interior, entrancewidth))
                
                # Insert status as 'Đang bán' with poster_id
                cur.execute("""
                    INSERT INTO public.statues (house_id, statue, poster_id)
                    VALUES (%s, 'Đang bán', %s)
                """, (new_house_id, session['user_id']))
                
                conn.commit()
                flash('Bài đăng đã được thêm thành công!', 'success')
                
            else:
                # User post - goes to wait_for_admin table
                # Generate new house_id for user posts (with 't' prefix)
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
                  # Insert into wait_for_admin table with poster_id
                cur.execute("""
                    INSERT INTO public.wait_for_admin 
                    (house_id, "Title", "Address", "District", "PostingDate", "PostType", "Price", 
                     "Area", "Direction", "Bedrooms", "Bathrooms", "Floors", "Width_meters", "Legal", "Interior", "Entrancewidth", poster_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (new_house_id, title, address, district, current_date, post_type, price, 
                      area, direction, bedrooms, bathrooms, floors, width_meters, legal, interior, entrancewidth, session['user_id']))
                
                conn.commit()
                flash('Bài đăng đã được gửi để chờ admin phê duyệt!', 'success')
            
            cur.close()
            conn.close()
            return redirect(url_for('index'))
            
        except Exception as e:
            flash(f'Lỗi khi đăng bài: {str(e)}', 'error')
            return redirect(url_for('post_house'))
    
    return render_template('post_house.html')

@app.route('/admin/approve_posts')
@admin_required
def admin_approve_posts():
    """Admin page to approve/reject pending user posts"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 10
        offset = (page - 1) * per_page
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get total count of pending posts
        cur.execute("SELECT COUNT(*) FROM public.wait_for_admin")
        total_posts = cur.fetchone()[0]
        total_pages = (total_posts + per_page - 1) // per_page
        
        # Get pending posts with pagination
        cur.execute("""
            SELECT house_id, "Title", "District", "Price", "Area", "Bedrooms", "Bathrooms", "PostingDate"
            FROM public.wait_for_admin
            ORDER BY "PostingDate" DESC
            LIMIT %s OFFSET %s
        """, (per_page, offset))
        
        pending_posts = cur.fetchall()
        
        # Format posts
        formatted_posts = []
        for post in pending_posts:
            formatted_posts.append({
                'house_id': post[0],
                'title': post[1],
                'district': post[2],
                'price': format_price(post[3]),
                'area': post[4],
                'bedrooms': post[5],
                'bathrooms': post[6],
                'posting_date': post[7]
            })
        
        cur.close()
        conn.close()
        
        return render_template('admin_approve_posts.html', 
                             posts=formatted_posts, 
                             page=page, 
                             total_pages=total_pages,
                             total_posts=total_posts)
        
    except Exception as e:
        flash(f'Lỗi: {str(e)}', 'error')
        return render_template('error.html', message='Không thể tải danh sách bài đăng chờ phê duyệt')

@app.route('/admin/approve_post/<house_id>', methods=['POST'])
@admin_required
def approve_post(house_id):
    """Approve a pending user post"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get post data from wait_for_admin
        cur.execute("SELECT * FROM public.wait_for_admin WHERE house_id = %s", (house_id,))
        post_data = cur.fetchone()
        
        if not post_data:
            flash('Bài đăng không tồn tại!', 'error')
            return redirect(url_for('admin_approve_posts'))
        
        # Generate new official house_id
        cur.execute("""
            SELECT house_id FROM public.house_prices
            WHERE house_id ~ '^[0-9]+$'
            ORDER BY house_id::integer DESC
            LIMIT 1
        """)
        result = cur.fetchone()
        
        if result:
            last_id = int(result[0])
            new_house_id = f"{last_id + 1:05d}"
        else:
            new_house_id = "00001"
          # Move to house_prices table with new ID
        cur.execute("""
            INSERT INTO public.house_prices 
            (house_id, "Title", "Address", "District", "PostingDate", "PostType", "Price", 
             "Area", "Direction", "Bedrooms", "Bathrooms", "Floors", "Width_meters", "Legal", "Interior", "Entrancewidth")
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (new_house_id, post_data[1], post_data[2], post_data[3], post_data[4], 
              post_data[5], post_data[6], post_data[7], post_data[8], post_data[9], 
              post_data[10], post_data[11], post_data[12], post_data[13], post_data[14], post_data[15]))
        
        # Insert status as 'Đang bán' with original poster_id
        original_poster_id = post_data[17] if len(post_data) > 17 else 'admin'  # poster_id is at index 17
        cur.execute("""
            INSERT INTO public.statues (house_id, statue, poster_id)
            VALUES (%s, 'Đang bán', %s)
        """, (new_house_id, original_poster_id))
        
        # Remove from wait_for_admin
        cur.execute("DELETE FROM public.wait_for_admin WHERE house_id = %s", (house_id,))
        
        conn.commit()
        cur.close()
        conn.close()
        
        flash('Bài đăng đã được phê duyệt thành công!', 'success')
        return redirect(url_for('admin_approve_posts'))
        
    except Exception as e:
        flash(f'Lỗi khi phê duyệt bài đăng: {str(e)}', 'error')
        return redirect(url_for('admin_approve_posts'))

@app.route('/admin/reject_post/<house_id>', methods=['POST'])
@admin_required
def reject_post(house_id):
    """Reject a pending user post"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Remove from wait_for_admin
        cur.execute("DELETE FROM public.wait_for_admin WHERE house_id = %s", (house_id,))
        
        conn.commit()
        cur.close()
        conn.close()
        
        flash('Bài đăng đã bị từ chối!', 'info')
        return redirect(url_for('admin_approve_posts'))
        
    except Exception as e:
        flash(f'Lỗi khi từ chối bài đăng: {str(e)}', 'error')
        return redirect(url_for('admin_approve_posts'))

@app.route('/admin/view_pending_post/<house_id>')
@admin_required
def view_pending_post(house_id):
    """View detailed information of a pending post"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get post data from wait_for_admin
        cur.execute("SELECT * FROM public.wait_for_admin WHERE house_id = %s", (house_id,))
        post_data = cur.fetchone()
        
        if not post_data:
            flash('Bài đăng không tồn tại!', 'error')
            return redirect(url_for('admin_approve_posts'))
        
        # Get column names
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'wait_for_admin'
            ORDER BY ordinal_position
        """)
        columns = [col[0] for col in cur.fetchall()]
        
        # Create post dictionary
        post = dict(zip(columns, post_data))
        post['price'] = format_price(post['Price'])
        
        cur.close()
        conn.close()
        
        return render_template('view_pending_post.html', post=post)
        
    except Exception as e:
        flash(f'Lỗi: {str(e)}', 'error')
        return redirect(url_for('admin_approve_posts'))

@app.route('/my_posts')
@login_required
def my_posts():
    """View user's posted properties (both approved and pending)"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        pending_posts = []
        approved_posts = []
        
        # Get current user ID (for regular users) or admin status
        current_user_id = session.get('user_id')
        is_admin = session.get('is_admin', False)
        
        # Get pending posts from wait_for_admin table
        if is_admin:
            # Admin can see all pending posts
            cur.execute("""
                SELECT house_id, "Title", "District", "Price", "Area", "Bedrooms", "Bathrooms", "PostingDate", poster_id
                FROM public.wait_for_admin
                ORDER BY "PostingDate" DESC
            """)
        else:
            # Regular users can only see their own pending posts
            cur.execute("""
                SELECT house_id, "Title", "District", "Price", "Area", "Bedrooms", "Bathrooms", "PostingDate", poster_id
                FROM public.wait_for_admin
                WHERE poster_id = %s
                ORDER BY "PostingDate" DESC
            """, (current_user_id,))
        
        pending_data = cur.fetchall()
        
        for post in pending_data:
            pending_posts.append({
                'house_id': post[0],
                'title': post[1],
                'district': post[2],
                'price': format_price(post[3]),
                'area': post[4],
                'bedrooms': post[5],
                'bathrooms': post[6],
                'posting_date': post[7],
                'poster_id': post[8],
                'status': 'Chờ phê duyệt'
            })
        
        # Get approved posts from house_prices table (joined with statues for poster_id)
        if is_admin:
            # Admin can see all approved posts
            cur.execute("""
                SELECT hp.house_id, hp."Title", hp."District", hp."Price", hp."Area", 
                       hp."Bedrooms", hp."Bathrooms", hp."PostingDate", s.poster_id
                FROM public.house_prices hp
                JOIN public.statues s ON hp.house_id = s.house_id
                WHERE s.statue = 'Đang bán'
                ORDER BY hp."PostingDate" DESC
                LIMIT 50
            """)
        else:
            # Regular users can only see their own approved posts
            cur.execute("""
                SELECT hp.house_id, hp."Title", hp."District", hp."Price", hp."Area", 
                       hp."Bedrooms", hp."Bathrooms", hp."PostingDate", s.poster_id
                FROM public.house_prices hp
                JOIN public.statues s ON hp.house_id = s.house_id
                WHERE s.poster_id = %s AND s.statue = 'Đang bán'
                ORDER BY hp."PostingDate" DESC
            """, (current_user_id,))
        
        approved_data = cur.fetchall()
        
        for post in approved_data:
            approved_posts.append({
                'house_id': post[0],
                'title': post[1],
                'district': post[2],
                'price': format_price(post[3]),
                'area': post[4],
                'bedrooms': post[5],
                'bathrooms': post[6],
                'posting_date': post[7],
                'poster_id': post[8],
                'status': 'Đã phê duyệt'
            })
        
        cur.close()
        conn.close()
        
        return render_template('my_posts.html', 
                             pending_posts=pending_posts, 
                             approved_posts=approved_posts,
                             is_admin=is_admin,
                             current_user_id=current_user_id)
        
    except Exception as e:
        flash(f'Lỗi: {str(e)}', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
