import pandas as pd
from decimal import Decimal
from sqlalchemy import create_engine
import os

def Clean_Data(df):
    # Clean and preprocess the data
    df.columns = df.columns.str.strip()  # Remove leading/trailing spaces in column names

    df = df[~df['Price'].astype(str).str.contains('/tháng', na=False)]

    # Xử lý giá có chứa tỷ
    df['Price'] = df.apply(
        lambda row: Decimal(str(row['Price']).replace('"', '').replace('tỷ', '').replace(',', '.').strip()) * Decimal('1e9')
        if 'tỷ' in str(row['Price'])
        else row['Price'],
        axis=1
    )

    # Xử lý các trường hợp còn lại
    df['Price'] = (
        df['Price']
        .astype(str)
        .str.replace(',', '.', regex=True)
        .str.strip()
        .apply(lambda x: Decimal(x) if str(x).replace('.', '', 1).isdigit() else x)
    )

    # Xử lý cột Area
    df['Area'] = (
        df['Area']
        .astype(str)
        .str.replace('m²', '', regex=True)
        .str.replace(',', '.', regex=True)
        .str.strip()
        .apply(lambda x: float(x) if str(x).replace('.', '', 1).isdigit() else None)
    )

    df['Price'] = df.apply(
        lambda row: float(str(row['Price']).replace('triệu/m²', '').replace(',', '.').strip()) * 1e6 * row['Area']
        if str(row['Price']).replace('triệu/m²', '').replace(',', '.').strip().replace('.', '', 1).isdigit() else row['Price'],
        axis=1
    )

    df['Bedrooms'] = (
        df['Bedrooms']
        .str.replace('phòng', '', regex=True)
        .str.strip()
        .astype(int)
        .replace(0, 1)
    )

    df['Bathrooms'] = (
        df['Bathrooms']
        .str.replace('phòng', '', regex=True)
        .str.strip()
        .astype(int)
        .replace(0, 1)
    )

    df['Floors'] = (
        df['Floors']
        .str.replace('tầng', '', regex=True)
        .str.strip()
        .astype(int)
        .replace(0, 1)
    )

    df['Legal'] = df['Legal'].astype(str).replace('0', 'Không')
    df['Interior'] = df['Interior'].astype(str).replace('0', 'Không nội thất')

    df['Width_meters'] = (
        df['Width_meters']
        .astype(str)
        .str.replace('m', '', regex=True)
        .str.replace(',', '.', regex=True)
        .str.strip()
        .astype(float)
    )

    df['Entrancewidth'] = (
        df['Entrancewidth']
        .astype(str)
        .str.replace('m', '', regex=True)
        .str.replace(',', '.', regex=True)
        .str.strip()
        .replace('0', None)
        .astype(float)
    )

    df['house_id'] = df.index + 1
    df['house_id'] = df['house_id'].apply(lambda x: f"{x:05d}")

    cols = df.columns.tolist()
    cols.remove('house_id')
    df = df[['house_id'] + cols]

    return df

def create_property_tables(engine):
    """
    Tạo bảng Property và migrate dữ liệu từ bảng house_prices
    """
    try:
        # Get connection from engine
        conn = engine.raw_connection()
        cur = conn.cursor()

        # Drop existing Property table if exists
        cur.execute("""
            DROP TABLE IF EXISTS public.property CASCADE;
        """)

        # Create the Property table
        cur.execute("""
            CREATE TABLE public.property (
                house_id VARCHAR(5) PRIMARY KEY,
                title TEXT,
                district VARCHAR(100),
                price TEXT,
                area NUMERIC,
                bedrooms INTEGER,
                bathrooms INTEGER
            );
        """)

        # Migrate data from house_prices to Property
        cur.execute("""
            INSERT INTO public.property (house_id, title, district, price, area, bedrooms, bathrooms)
            SELECT 
                house_id,
                "Title",
                "District",
                "Price",
                "Area",
                "Bedrooms",
                "Bathrooms"
            FROM public.house_prices;
        """)

        # Commit the changes
        conn.commit()
        print("Đã tạo và migrate dữ liệu cho bảng Property thành công.")
    except Exception as e:
        print(f"Lỗi khi tạo bảng Property: {e}")
        if 'conn' in locals():
            conn.rollback()
        raise e
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close() # Get connection from engine


# Load the CSV file
csv_file = os.path.join(os.path.dirname(__file__), "HN_Houseprice.csv")
df = pd.read_csv(csv_file)

# Clean the data
df = Clean_Data(df)

# Database connection
db_url = "postgresql://postgres:271205@localhost:5432/house_prices"
engine = create_engine(db_url)

# Insert data into PostgreSQL
table_name = "house_prices"
df.to_sql(table_name, engine, if_exists='replace', index=False)

create_property_tables(engine)

print(f"Data from {csv_file} has been successfully inserted into the '{table_name}' table.")
