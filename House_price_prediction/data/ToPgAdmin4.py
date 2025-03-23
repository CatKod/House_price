import pandas as pd
from sqlalchemy import create_engine

# Load the CSV file
import os

csv_file = os.path.join(os.path.dirname(__file__), "HN_Houseprice.csv")
df = pd.read_csv(csv_file)

# Clean and preprocess the data
df.columns = df.columns.str.strip()  # Remove leading/trailing spaces in column names

df['Price'] = (
    df['Price']
    .dropna()
    .astype(str)
    .str.replace('tỷ', '', regex=True)
    .str.replace(',', '.', regex=True)
    .str.strip()
    .apply( lambda x: float(x) * 1e9 if x.replace('.', '', 1).isdigit() else x)  #valid numeric values, and keep others as is
)

df['Area'] = (
    df['Area']
    .str.replace('m²', '', regex=True)
    .str.replace(',', '', regex=True)
    .str.strip()
    .astype(float)
)

df['Price'] = df.apply(
    lambda row: float(str(row['Price']).replace('triệu/m²', '').replace(',', '.').strip()) * 1e6 * row['Area']
    if str(row['Price']).replace('triệu/m²', '').replace(',', '.').strip().replace('.', '', 1).isdigit() else row['Price'],
    axis=1
)

df['Width_meters'] = df['Width_meters'].replace(0, None)  # Replace 0 with None for null values
df['Entrancewidth'] = df['Entrancewidth'].replace(0, None)  # Replace 0 with None for null values

df['Bedrooms'] = (
    df['Bedrooms']
    .str.replace('phòng', '', regex=True)
    .str.strip()
    .astype(int)
)

df['Bathrooms'] = (
    df['Bathrooms']
    .str.replace('phòng', '', regex=True)
    .str.strip()
    .astype(int)
    .replace(0, 1)  # Replace 0 with 1
)

df['Floors'] = (
    df['Floors']
    .str.replace('tầng', '', regex=True)
    .str.strip()
    .astype(int)
    .replace(0, 1)  # Replace 0 with 1
)

df['Width_meters'] = (
    df['Width_meters']
    .astype(str)
    .str.replace('m', '', regex=True)
    .str.replace(',', '.', regex=True)
    .str.strip()
    .replace('0', None)  # Replace 0 with None for null values
    .astype(float)
)

# Add a new column 'ID' with sequential values starting from '0001'
df['ID'] = df.index + 1
df['ID'] = df['ID'].apply(lambda x: f"{x:05d}")

# Database connection
db_url = "postgresql://postgres:271205@localhost:5432/house_prices"
engine = create_engine(db_url)

# Insert data into PostgreSQL
table_name = "house_prices"
df.to_sql(table_name, engine, if_exists='replace', index=False)

print(f"Data from {csv_file} has been successfully inserted into the '{table_name}' table.")
