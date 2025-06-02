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
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        offset = (page - 1) * per_page

        conn = get_db_connection()
        cur = conn.cursor()

        # Build dynamic WHERE clause
        where_clauses = []
        params = []
        if search_term:
            where_clauses.append('(title ILIKE %s OR district ILIKE %s OR house_id ILIKE %s)')
            params.extend([f'%{search_term}%'] * 3)
        if district:
            where_clauses.append('district = %s')
            params.append(district)
        if price_min:
            where_clauses.append("price ~ '^[0-9]+(\\.[0-9]+)?$' AND price::numeric >= %s")
            params.append(float(price_min) * 1e9)
        if price_max:
            where_clauses.append("price ~ '^[0-9]+(\\.[0-9]+)?$' AND price::numeric <= %s")
            params.append(float(price_max) * 1e9)
        if area_min:
            where_clauses.append('area >= %s')
            params.append(float(area_min))
        if area_max:
            where_clauses.append('area <= %s')
            params.append(float(area_max))
        if bedrooms:
            where_clauses.append('bedrooms >= %s')
            params.append(int(bedrooms))

        where_sql = ' AND '.join(where_clauses)
        if where_sql:
            where_sql = 'WHERE ' + where_sql

        # Get total count
        count_sql = f"SELECT COUNT(*) FROM public.property {where_sql}"
        cur.execute(count_sql, params)
        total_properties = cur.fetchone()[0]
        total_pages = (total_properties + per_page - 1) // per_page

        # Get search results
        search_sql = f"""
            SELECT house_id, title, district, price, area, bedrooms, bathrooms
            FROM public.property
            {where_sql}
            ORDER BY house_id
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

        # Lấy danh sách quận/huyện cho dropdown
        cur.execute('SELECT DISTINCT district FROM public.property ORDER BY district')
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
                             selected_district=district)

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
            model_path = os.path.join('models', 'house_price_model.pkl')
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
def compare():
    if request.method == 'POST':
        try:
            house_id1 = request.form['house_id1']
            house_id2 = request.form['house_id2']

            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute("""
                SELECT * FROM public.property
                WHERE house_id = %s OR house_id = %s
            """, (house_id1, house_id2))
            properties = cur.fetchall()

            if len(properties) != 2:
                flash('One or both properties not found', 'error')
                return redirect(url_for('compare'))

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

            return render_template('compare.html', properties=formatted_properties)

        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('compare'))

    return render_template('compare.html')

@app.route('/favorites')
@login_required
def favorites():
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
        properties = cur.fetchall()
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
        # Xóa bản ghi đặt cọc của user này cho nhà này
        cur.execute("DELETE FROM public.deposit WHERE user_id = %s AND house_id = %s", (session['user_id'], house_id))
        # Nếu không còn ai đặt cọc thì chuyển statue về 'Đang bán'
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
        # Xóa tất cả bản ghi đặt cọc cho nhà này
        cur.execute("DELETE FROM public.deposit WHERE house_id = %s", (house_id,))
        # Chuyển statue về 'Đang bán'
        cur.execute("UPDATE public.statues SET statue = 'Đang bán' WHERE house_id = %s", (house_id,))
        conn.commit()
        cur.close()
        conn.close()
        flash('Đã hủy xử lý bất động sản thành công.', 'success')
        return redirect(url_for('admin_processing'))
    except Exception as e:
        flash(f'Lỗi: {str(e)}', 'error')
        return redirect(url_for('admin_processing'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
