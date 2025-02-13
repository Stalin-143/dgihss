import pandas as pd
import os

# Directory where the scraped data is saved
base_dir = "data"

# Ask user for the website domain
domain = input("Enter the website domain (e.g., xyz_onion): ").strip()
save_path = os.path.join(base_dir, domain)

# List of expected CSV files
csv_files = ["text.csv", "links.csv", "images.csv", "videos.csv", "payments.csv"]

# Function to read CSV files safely
def read_csv_safe(file_path):
    if not os.path.exists(file_path):
        print(f"⚠️ File not found: {file_path}")
        return None
    
    try:
        df = pd.read_csv(file_path, encoding="utf-8", on_bad_lines="skip")
        if df.empty:
            print(f"⚠️ Warning: {file_path} is empty!")
            return None
        
        print(f"✅ Successfully loaded: {file_path}")
        return df
    except pd.errors.EmptyDataError:
        print(f"⚠️ Warning: {file_path} is empty!")
        return None
    except pd.errors.ParserError:
        print(f"⚠️ Error: {file_path} is corrupted or has bad formatting!")
        return None
    except UnicodeDecodeError:
        print(f"⚠️ Encoding issue in {file_path}, trying a different encoding...")
        try:
            df = pd.read_csv(file_path, encoding="latin1", on_bad_lines="skip")
            print(f"✅ Successfully loaded {file_path} with alternative encoding.")
            return df
        except Exception as e:
            print(f"❌ Failed to read {file_path}: {e}")
            return None
    except Exception as e:
        print(f"❌ Unexpected error while reading {file_path}: {e}")
        return None

# Load all CSV files
dataframes = {}
for csv_file in csv_files:
    file_path = os.path.join(save_path, csv_file)
    df = read_csv_safe(file_path)
    if df is not None:
        dataframes[csv_file] = df

# Example: Display first few rows of each loaded CSV
for filename, df in dataframes.items():
    print(f"\n🔹 {filename} (First 5 rows):")
    print(df.head())
