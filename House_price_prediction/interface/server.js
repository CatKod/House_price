const express = require('express');
const { Pool } = require('pg');
const path = require('path');
require('dotenv').config();

const app = express();
const port = process.env.PORT || 3000;

// Thiết lập EJS làm view engine
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Phục vụ các file tĩnh từ thư mục public
app.use(express.static(path.join(__dirname, 'public')));

// Kết nối đến PostgreSQL
const pool = new Pool({
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || '271205',
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  database: process.env.DB_NAME || 'house_prices'
});

// Hàm định dạng giá
function formatPrice(price) {
  if (price === null || price === undefined) return 'N/A';
  try {
    const priceInBillions = parseFloat(price) / 1e9;
    return `${priceInBillions.toFixed(2)} tỷ VND`;
  } catch (error) {
    return 'N/A';
  }
}

// Route chính - hiển thị danh sách nhà
app.get('/', async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const perPage = parseInt(req.query.per_page) || 10;
    const offset = (page - 1) * perPage;

    // Lấy tổng số bất động sản
    const countResult = await pool.query('SELECT COUNT(*) FROM public.property');
    const totalProperties = parseInt(countResult.rows[0].count);
    const totalPages = Math.ceil(totalProperties / perPage);

    // Lấy danh sách bất động sản cho trang hiện tại
    const result = await pool.query(`
      SELECT house_id, title, district, price, area, bedrooms, bathrooms
      FROM public.property
      ORDER BY house_id
      LIMIT $1
      OFFSET $2
    `, [perPage, offset]);

    // Định dạng dữ liệu
    const properties = result.rows.map(property => ({
      ...property,
      formatted_price: formatPrice(property.price)
    }));

    res.render('index', {
      properties,
      currentPage: page,
      totalPages,
      totalProperties,
      perPage
    });
  } catch (error) {
    console.error('Lỗi khi lấy dữ liệu:', error);
    res.status(500).render('error', { message: 'Đã xảy ra lỗi khi lấy dữ liệu' });
  }
});

// Route để xem chi tiết một ngôi nhà
app.get('/house/:id', async (req, res) => {
  try {
    const houseId = req.params.id;
    
    const result = await pool.query(`
      SELECT * FROM public.property
      WHERE house_id = $1
    `, [houseId]);

    if (result.rows.length === 0) {
      return res.status(404).render('error', { message: 'Không tìm thấy thông tin bất động sản' });
    }

    const house = result.rows[0];
    house.formatted_price = formatPrice(house.price);

    res.render('house-detail', { house });
  } catch (error) {
    console.error('Lỗi khi lấy thông tin nhà:', error);
    res.status(500).render('error', { message: 'Đã xảy ra lỗi khi lấy thông tin nhà' });
  }
});

// Route để tìm kiếm nhà
app.get('/search', async (req, res) => {
  try {
    const searchTerm = req.query.q || '';
    const page = parseInt(req.query.page) || 1;
    const perPage = parseInt(req.query.per_page) || 10;
    const offset = (page - 1) * perPage;

    // Lấy tổng số kết quả tìm kiếm
    const countResult = await pool.query(`
      SELECT COUNT(*) FROM public.property
      WHERE title ILIKE $1 OR district ILIKE $1 OR house_id ILIKE $1
    `, [`%${searchTerm}%`]);
    
    const totalProperties = parseInt(countResult.rows[0].count);
    const totalPages = Math.ceil(totalProperties / perPage);

    // Lấy kết quả tìm kiếm
    const result = await pool.query(`
      SELECT house_id, title, district, price, area, bedrooms, bathrooms
      FROM public.property
      WHERE title ILIKE $1 OR district ILIKE $1 OR house_id ILIKE $1
      ORDER BY house_id
      LIMIT $2
      OFFSET $3
    `, [`%${searchTerm}%`, perPage, offset]);

    // Định dạng dữ liệu
    const properties = result.rows.map(property => ({
      ...property,
      formatted_price: formatPrice(property.price)
    }));

    res.render('search', {
      properties,
      searchTerm,
      currentPage: page,
      totalPages,
      totalProperties,
      perPage
    });
  } catch (error) {
    console.error('Lỗi khi tìm kiếm:', error);
    res.status(500).render('error', { message: 'Đã xảy ra lỗi khi tìm kiếm' });
  }
});

// Khởi động server
app.listen(port, () => {
  console.log(`Server đang chạy tại http://localhost:${port}`);
}); 