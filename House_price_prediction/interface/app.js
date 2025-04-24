const express = require('express');
const path = require('path');
const { Pool } = require('pg');
require('dotenv').config();

const app = express();
const port = process.env.PORT || 3000;

// Thiết lập EJS làm view engine
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Phục vụ các file tĩnh từ thư mục public
app.use(express.static(path.join(__dirname, 'public')));

// Middleware để parse JSON và form data
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

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

// Route chính - hiển thị trang chủ
app.get('/', async (req, res) => {
  try {
    // Lấy số lượng bất động sản theo quận/huyện
    const districtStats = await pool.query(`
      SELECT district, COUNT(*) as count
      FROM public.property
      GROUP BY district
      ORDER BY count DESC
      LIMIT 10
    `);

    // Lấy số lượng bất động sản theo District
    const typeStats = await pool.query(`
      SELECT district, COUNT(*) as count
      FROM public.property
      GROUP BY district
      ORDER BY count DESC
    `);

    // Lấy giá trung bình theo quận/huyện
    const avgPriceStats = await pool.query(`
      SELECT district, AVG(price::numeric) as avg_price
      FROM public.property
      WHERE price ~ '^[0-9]+(\.[0-9]+)?$'
      GROUP BY district
      ORDER BY avg_price DESC
      LIMIT 10
    `);

    res.render('index', {
      districtStats: districtStats.rows,
      typeStats: typeStats.rows,
      avgPriceStats: avgPriceStats.rows.map(row => ({
        ...row,
        formatted_price: formatPrice(row.avg_price)
      }))
    });
  } catch (error) {
    console.error('Lỗi khi lấy dữ liệu thống kê:', error);
    res.status(500).render('error', { message: 'Đã xảy ra lỗi khi lấy dữ liệu thống kê' });
  }
});

// Route hiển thị danh sách bất động sản
app.get('/properties', async (req, res) => {
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

    res.render('properties', {
      properties,
      currentPage: page,
      totalPages,
      totalProperties,
      perPage
    });
  } catch (error) {
    console.error('Lỗi khi lấy danh sách bất động sản:', error);
    res.status(500).render('error', { message: 'Đã xảy ra lỗi khi lấy danh sách bất động sản' });
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

    res.render('house', { house });
  } catch (error) {
    console.error('Lỗi khi lấy thông tin nhà:', error);
    res.status(500).render('error', { message: 'Đã xảy ra lỗi khi lấy thông tin nhà' });
  }
});

// Route để tìm kiếm nhà
app.get('/properties/search', async (req, res) => {
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

// Route để dự đoán giá nhà
app.get('/predict', (req, res) => {
  res.render('predict');
});

// Route để so sánh bất động sản
app.get('/compare', (req, res) => {
  res.render('compare');
});

// Route để phân tích thị trường
app.get('/analysis', (req, res) => {
  res.render('analysis');
});

// Route xử lý lỗi 404
app.use((req, res) => {
  res.status(404).render('error', { message: 'Không tìm thấy trang' });
});

// Khởi động server
app.listen(port, () => {
  console.log(`Server đang chạy tại http://localhost:${port}`);
});