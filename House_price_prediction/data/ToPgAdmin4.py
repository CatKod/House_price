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
    # Check if 'Price' contains '/' go to next value
    .apply(lambda x: x.split('/')[0] if '/' in x else x)
    .str.replace('tỷ', '', regex=True)
    .str.replace(',', '.', regex=True)
    .str.strip()  # Remove any extra spaces
    .apply(lambda x: float(x) if x.replace('.', '', 1).isdigit() else None)  # Handle invalid values
    .apply(lambda x: x * 1e9)
)  # Convert 'Price' to numeric (in billions)
df['Area'] = (
    df['Area']
    .dropna()
    .str.replace('m²', '', regex=True)
    .str.replace(',', '', regex=True)
    .str.strip()
    .astype(float)
)  # Handle nulls and convert 'Area' to float
df['Width_meters'] = df['Width_meters'].replace(0, None)  # Replace 0 with None for null values
df['Entrancewidth'] = df['Entrancewidth'].replace(0, None)  # Replace 0 with None for null values

# Replace all 0 values with None
df = df.replace(0, None)

# Database connection
db_url = "postgresql://postgres:271205@localhost:5432/house_prices"
engine = create_engine(db_url)

# Insert data into PostgreSQL
table_name = "house_prices"
df.to_sql(table_name, engine, if_exists='replace', index=False)

print(f"Data from {csv_file} has been successfully inserted into the '{table_name}' table.")
