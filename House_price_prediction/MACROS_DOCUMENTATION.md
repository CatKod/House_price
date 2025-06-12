# Macros Documentation - House Price Prediction Application

This document explains how to use the reusable Jinja2 macros available in `templates/macros.html`.

## Quick Start

To use macros in your templates, first import them:

```jinja2
{% from 'macros.html' import macro_name_1, macro_name_2, ... %}
```

## Available Macros

### 1. Property Display Macros

#### `property_card(property, show_favorite=false, show_compare=false, show_status=false)`
Displays property information in a card format.

**Usage:**
```jinja2
{% from 'macros.html' import property_card %}

<div class="row">
    {% for property in properties %}
    <div class="col-md-4 mb-3">
        {{ property_card(property, show_favorite=true, show_compare=true, show_status=true) }}
    </div>
    {% endfor %}
</div>
```

#### `property_row(property, show_actions=true, show_status=false)`
Displays property information in a row format (like search results).

**Usage:**
```jinja2
{% from 'macros.html' import property_row %}

{% for property in properties %}
    {{ property_row(property, show_actions=true, show_status=true) }}
{% endfor %}
```

#### `property_details_table(property)`
Displays comprehensive property details in a table format.

**Usage:**
```jinja2
{% from 'macros.html' import property_details_table %}

{{ property_details_table(property) }}
```

### 2. UI Component Macros

#### `status_badge(status)`
Displays a colored status badge.

**Usage:**
```jinja2
{% from 'macros.html' import status_badge %}

{{ status_badge("Đang bán") }}
{{ status_badge("Đã bán") }}
{{ status_badge("Đang xử lý") }}
```

#### `loading_spinner(size="md", text="Đang tải...")`
Displays a loading spinner.

**Parameters:**
- `size`: "sm", "md", or "lg"
- `text`: Loading message

**Usage:**
```jinja2
{% from 'macros.html' import loading_spinner %}

{{ loading_spinner(size="lg", text="Đang tải dữ liệu...") }}
```

#### `flash_messages()`
Displays Flash messages with proper styling.

**Usage:**
```jinja2
{% from 'macros.html' import flash_messages %}

{{ flash_messages() }}
```

### 3. Navigation Macros

#### `pagination(page, total_pages, endpoint, **kwargs)`
Displays pagination controls.

**Usage:**
```jinja2
{% from 'macros.html' import pagination %}

{{ pagination(page=current_page, total_pages=total_pages, endpoint='search', q=search_term) }}
```

#### `breadcrumb(items)`
Displays breadcrumb navigation.

**Usage:**
```jinja2
{% from 'macros.html' import breadcrumb %}

{% set breadcrumb_items = [
    {'text': 'Trang chủ', 'url': url_for('index')},
    {'text': 'Tìm kiếm', 'url': url_for('search')},
    {'text': 'Kết quả'}
] %}
{{ breadcrumb(breadcrumb_items) }}
```

### 4. Form Macros

#### `form_input(name, label, type="text", value="", placeholder="", required=false, readonly=false, help_text="")`
Creates form input fields with proper styling.

**Usage:**
```jinja2
{% from 'macros.html' import form_input %}

{{ form_input("email", "Email", type="email", required=true, placeholder="Nhập email của bạn") }}
{{ form_input("phone", "Số điện thoại", help_text="Định dạng: 0123456789") }}
```

#### `search_filters()`
Displays comprehensive search filter form.

**Usage:**
```jinja2
{% from 'macros.html' import search_filters %}

{{ search_filters() }}
```

### 5. Chart Macros

#### `price_comparison_chart(properties)`
Displays a bar chart comparing property prices.

**Requirements:** Chart.js library must be included.

**Usage:**
```jinja2
{% from 'macros.html' import price_comparison_chart %}

{{ price_comparison_chart(properties) }}

<!-- Include Chart.js -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

#### `area_comparison_chart(properties)`
Displays a doughnut chart comparing property areas.

**Usage:**
```jinja2
{% from 'macros.html' import area_comparison_chart %}

{{ area_comparison_chart(properties) }}
```

#### `price_per_sqm_comparison(properties)`
Displays a table comparing price per square meter.

**Usage:**
```jinja2
{% from 'macros.html' import price_per_sqm_comparison %}

{{ price_per_sqm_comparison(properties) }}
```

### 6. Utility Macros

#### `empty_state(icon="fas fa-home", title="Không tìm thấy kết quả", message="...", action_url="", action_text="")`
Displays empty state with optional action button.

**Usage:**
```jinja2
{% from 'macros.html' import empty_state %}

{% if not properties %}
    {{ empty_state(
        icon="fas fa-search",
        title="Không tìm thấy bất động sản",
        message="Thử thay đổi bộ lọc tìm kiếm",
        action_url=url_for('index'),
        action_text="Về trang chủ"
    ) }}
{% endif %}
```

#### `confirm_modal(modal_id, title, message, confirm_text="Xác nhận", cancel_text="Hủy")`
Creates a confirmation modal.

**Usage:**
```jinja2
{% from 'macros.html' import confirm_modal %}

{{ confirm_modal(
    modal_id="deleteModal",
    title="Xác nhận xóa",
    message="Bạn có chắc chắn muốn xóa bất động sản này?",
    confirm_text="Xóa",
    cancel_text="Hủy"
) }}

<!-- Trigger modal -->
<button class="btn btn-danger" data-bs-toggle="modal" data-bs-target="#deleteModal">
    Xóa
</button>
```

## Property Data Structure

The macros expect property objects with the following structure:

```python
property = {
    'house_id': 1,
    'title': 'Nhà đẹp 3 tầng',
    'district': 'Ba Đình',
    'address': '123 Đường ABC',
    'area': 120,  # m²
    'bedrooms': 3,
    'bathrooms': 2,
    'floors': 3,
    'price': 5.5,  # in billions (tỷ)
    'price_formatted': '5.50 tỷ',  # formatted string
    'direction': 'Đông Nam',
    'width_meters': 4.5,
    'legal': 'Sổ đỏ chính chủ',
    'interior': 'Hoàn thiện',
    'entrance_width': 3.5,
    'posting_date': '2024-01-15',
    'post_type': 'Bán',
    'status': 'Đang bán'
}
```

## Best Practices

1. **Import only what you need:** Only import the macros you actually use in each template.

2. **Consistent data format:** Ensure your property data follows the expected structure.

3. **Error handling:** Use conditional checks before calling macros:
   ```jinja2
   {% if properties %}
       {% for property in properties %}
           {{ property_row(property) }}
       {% endfor %}
   {% else %}
       {{ empty_state() }}
   {% endif %}
   ```

4. **Performance:** For large lists, consider pagination and limit the number of items displayed.

## Example Template

Here's a complete example of using multiple macros:

```jinja2
{% extends "base.html" %}
{% from 'macros.html' import property_row, search_filters, pagination, flash_messages, empty_state %}

{% block content %}
{{ flash_messages() }}

<h1>Tìm kiếm bất động sản</h1>

{{ search_filters() }}

{% if properties %}
    <div class="results-section">
        <h3>Kết quả tìm kiếm ({{ total_properties }} bất động sản)</h3>
        
        {% for property in properties %}
            {{ property_row(property, show_actions=true, show_status=true) }}
        {% endfor %}
        
        {{ pagination(page=current_page, total_pages=total_pages, endpoint='search') }}
    </div>
{% else %}
    {{ empty_state(
        title="Không tìm thấy bất động sản",
        message="Thử thay đổi bộ lọc tìm kiếm"
    ) }}
{% endif %}
{% endblock %}
```

## Integration with Existing Templates

To integrate macros into your existing templates:

1. Add the import statement at the top
2. Replace repetitive HTML code with macro calls
3. Ensure your data structure matches the expected format
4. Test thoroughly to ensure proper functionality

This modular approach will make your templates more maintainable and consistent across your application.
