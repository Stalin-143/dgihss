import os
import pandas as pd
import cv2
import pytesseract
import requests
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
import json
import PyPDF2
import docx

# Data directory
DATA_DIR = "data/"

# TOR Proxy (for .onion sites)
TOR_PROXIES = {
    "http": "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050"
}

def get_text_from_csv(file_path):
    """Extracts text content from a CSV file."""
    try:
        encodings = ["utf-8", "latin1", "ISO-8859-1"]
        for enc in encodings:
            try:
                df = pd.read_csv(file_path, encoding=enc)
                return " ".join(df.astype(str).values.flatten())  # Convert all values to a single string
            except Exception:
                continue
        raise ValueError("Failed to read CSV with available encodings.")
    except Exception as e:
        print(f"⚠️ Error reading CSV {file_path}: {e}")
        return ""

def get_text_from_json(file_path):
    """Extracts text content from a JSON file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return json.dumps(data, indent=2)  # Convert JSON to a readable string
    except Exception as e:
        print(f"⚠️ Error reading JSON {file_path}: {e}")
        return ""

def get_text_from_pdf(file_path):
    """Extracts text content from a PDF file."""
    try:
        text = ""
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""  # Extract text from each page
        return text.strip()
    except Exception as e:
        print(f"⚠️ Error reading PDF {file_path}: {e}")
        return ""

def get_text_from_docx(file_path):
    """Extracts text content from a DOCX file."""
    try:
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs]).strip()
    except Exception as e:
        print(f"⚠️ Error reading DOCX {file_path}: {e}")
        return ""

def get_text_from_image(file_path):
    """Extracts text from images using OCR."""
    try:
        image = cv2.imread(file_path)
        if image is None:
            raise ValueError("Invalid image file or file not found.")
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        print(f"⚠️ Error reading image {file_path}: {e}")
        return ""

def get_text_from_text_file(file_path):
    """Extracts text from .txt files."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().strip()
    except Exception as e:
        print(f"⚠️ Error reading text file {file_path}: {e}")
        return ""

def fetch_website_content(url):
    """Fetches text from a website."""
    try:
        proxies = TOR_PROXIES if ".onion" in url else None
        response = requests.get(url, proxies=proxies, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.get_text(separator=' ', strip=True)
    except requests.RequestException as e:
        print(f"❌ Error fetching {url}: {e}")
        return ""

def similarity_ratio(text1, text2):
    """Calculates similarity ratio between two text contents."""
    return SequenceMatcher(None, text1, text2).ratio()

def analyze_website(url):
    """Analyzes a website by comparing its content with individual files."""
    website_content = fetch_website_content(url)
    
    if not website_content:
        print("⚠️ Unable to fetch website content.")
        return

    if not os.path.exists(DATA_DIR):
        print(f"❌ Data directory '{DATA_DIR}' not found!")
        return

    for root, _, files in os.walk(DATA_DIR):
        for file in files:
            file_path = os.path.join(root, file)

            if file.endswith(".csv"):
                file_text = get_text_from_csv(file_path)
            elif file.endswith(".json"):
                file_text = get_text_from_json(file_path)
            elif file.endswith(".pdf"):
                file_text = get_text_from_pdf(file_path)
            elif file.endswith(".docx"):
                file_text = get_text_from_docx(file_path)
            elif file.endswith((".png", ".jpg", ".jpeg")):
                file_text = get_text_from_image(file_path)
            elif file.endswith(".txt"):
                file_text = get_text_from_text_file(file_path)
            else:
                continue  # Skip unsupported files

            if file_text:
                similarity = similarity_ratio(website_content, file_text) * 100

                if similarity == 100:
                    print(f"🚨 This website contains narcotics-related content! (Matched with {file})")
                    return
                elif similarity > 50:
                    print(f"⚠️ Warning: {similarity:.2f}% match found with {file}. Content might be suspicious.")

    print("✅ This website appears to be normal.")

def analyze_data_directory():
    """Analyzes the collected data and determines if it contains useful content."""
    if not os.path.exists(DATA_DIR):
        print(f"❌ Data directory '{DATA_DIR}' not found!")
        return

    has_data = False
    for root, _, files in os.walk(DATA_DIR):
        for file in files:
            file_path = os.path.join(root, file)

            if file.endswith(".csv"):
                file_text = get_text_from_csv(file_path)
            elif file.endswith(".json"):
                file_text = get_text_from_json(file_path)
            elif file.endswith(".pdf"):
                file_text = get_text_from_pdf(file_path)
            elif file.endswith(".docx"):
                file_text = get_text_from_docx(file_path)
            elif file.endswith((".png", ".jpg", ".jpeg")):
                file_text = get_text_from_image(file_path)
            elif file.endswith(".txt"):
                file_text = get_text_from_text_file(file_path)
            else:
                continue  # Skip unsupported files

            if file_text:
                has_data = True
                print(f"✅ Data collected from {file}")

    if not has_data:
        print("⚠️ No data found in the directory.")

def main():
    """Main function to handle user input and analyze data."""
    while True:
        print("\nChoose an option:")
        print("A) Check an OpenWeb link")
        print("B) Check an Onion (Dark Web) link")
        print("C) Analyze collected data (CSV, images, text files, PDFs, DOCX, JSON)")
        print("D) Exit")
      
        choice = input("Enter your choice (A/B/C/D): ").strip().upper()

        if choice in ("A", "B"):
            url = input("Enter the website URL: ").strip()
            analyze_website(url)
        elif choice == "C":
            analyze_data_directory()
        elif choice == "D":
            print("👋 Exiting program.")
            break
        else:
            print("❌ Invalid choice. Please enter A, B, C, or D.")

# Run program
if __name__ == "__main__":
    main()
