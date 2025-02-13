import os
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from urllib.parse import urljoin, urlparse

# Tor proxy settings
proxies = {
    "http": "socks5h://127.0.0.1:9150",
    "https": "socks5h://127.0.0.1:9150",
}

# Create main data directory
base_dir = "data"
os.makedirs(base_dir, exist_ok=True)

# Ask user for multiple URLs
urls = input("Enter .onion URLs separated by commas: ").split(",")

for url in urls:
    url = url.strip()
    if not url:
        continue

    print(f"\n🔍 Scraping: {url}")

    try:
        response = requests.get(url, proxies=proxies, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        domain = urlparse(url).netloc.replace(".", "_")
        save_path = os.path.join(base_dir, domain)

        # Create a folder for the website data inside 'data/'
        os.makedirs(save_path, exist_ok=True)

        ### Extract All Data (Including Hidden Elements) ###
        all_text = soup.get_text(separator=" ").strip()
        images = [urljoin(url, img["src"]) for img in soup.find_all("img", src=True)]
        videos = [urljoin(url, video["src"]) for video in soup.find_all("video", src=True)]

        page_data = {
            "title": soup.title.string if soup.title else "",
            "meta": {meta.get("name", ""): meta.get("content", "") for meta in soup.find_all("meta")},
            "scripts": [script.string for script in soup.find_all("script") if script.string],
            "styles": [style.string for style in soup.find_all("style") if style.string],
            "images": images,
            "videos": videos,
            "links": [{"Link Text": a.text.strip(), "URL": urljoin(url, a["href"])} for a in soup.find_all("a", href=True)],
            "hidden_elements": [hidden.text.strip() for hidden in soup.find_all(style=lambda value: value and "display:none" in value)],
            "text": all_text
        }

        ### Save Data to JSON ###
        json_path = os.path.join(save_path, "data.json")
        with open(json_path, "w", encoding="utf-8") as json_file:
            json.dump(page_data, json_file, indent=4, ensure_ascii=False)
        
        ### Save Text Data to TXT ###
        text_path = os.path.join(save_path, "data.txt")
        with open(text_path, "w", encoding="utf-8") as text_file:
            text_file.write(all_text)
        
        ### Save Data to CSV ###
        csv_path = os.path.join(save_path, "data.csv")
        df = pd.DataFrame([{key: value for key, value in page_data.items() if isinstance(value, str)}])
        df.to_csv(csv_path, index=False, encoding="utf-8")
        
        ### Download and Save Images and Videos ###
        def download_files(file_urls, folder, file_type):
            os.makedirs(folder, exist_ok=True)
            for file_url in file_urls:
                try:
                    file_name = os.path.join(folder, os.path.basename(file_url))
                    file_response = requests.get(file_url, proxies=proxies, timeout=30, stream=True)
                    file_response.raise_for_status()
                    with open(file_name, "wb") as f:
                        for chunk in file_response.iter_content(chunk_size=1024):
                            f.write(chunk)
                    print(f"📥 {file_type} saved: {file_name}")
                except Exception as e:
                    print(f"⚠️ Failed to download {file_url}: {e}")
        
        download_files(images, os.path.join(save_path, "images"), "Image")
        download_files(videos, os.path.join(save_path, "videos"), "Video")
        
        print(f"✅ Scraping complete for {url}!")
        print(f"📂 Data saved in: {save_path}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Network error scraping {url}: {e}")
    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
