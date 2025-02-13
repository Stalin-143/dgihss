import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
from urllib.parse import urljoin, urlparse

# User inputs multiple URLs (clearnet websites)
urls = input("Enter website URLs separated by commas: ").split(",")

# Keywords to detect payment information
payment_keywords = ["bitcoin", "btc", "monero", "xmr", "ethereum", "eth", "wallet", "crypto", "address", "paypal"]

for url in urls:
    url = url.strip()
    if not url:
        continue

    print(f"\n🔍 Scraping: {url}")

    try:
        response = requests.get(url, timeout=30)  # No Tor proxy needed
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        domain = urlparse(url).netloc.replace(".", "_")

        # Create a folder for the website data
        os.makedirs(domain, exist_ok=True)

        ### Extract Text ###
        text_data = [{"Tag": tag.name, "Content": tag.text.strip()} for tag in soup.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6", "li"])]

        ### Extract Links ###
        links_data = [{"Link Text": a.text.strip(), "URL": urljoin(url, a["href"])} for a in soup.find_all("a", href=True)]

        ### Extract Images & Download ###
        images_data = []
        os.makedirs(f"{domain}/images", exist_ok=True)
        for img in tqdm(soup.find_all("img", src=True), desc="Downloading Images"):
            img_url = urljoin(url, img["src"])
            img_name = os.path.join(f"{domain}/images", os.path.basename(img_url))

            try:
                img_data = requests.get(img_url, timeout=10).content
                with open(img_name, "wb") as img_file:
                    img_file.write(img_data)
                images_data.append({"Image URL": img_url, "Alt Text": img.get("alt", "N/A"), "Saved Path": img_name})
            except:
                images_data.append({"Image URL": img_url, "Alt Text": img.get("alt", "N/A"), "Saved Path": "Download Failed"})

        ### Extract Videos & Download ###
        videos_data = []
        os.makedirs(f"{domain}/videos", exist_ok=True)
        for video in tqdm(soup.find_all("video", src=True), desc="Downloading Videos"):
            video_url = urljoin(url, video["src"])
            video_name = os.path.join(f"{domain}/videos", os.path.basename(video_url))

            try:
                video_data = requests.get(video_url, timeout=20).content
                with open(video_name, "wb") as vid_file:
                    vid_file.write(video_data)
                videos_data.append({"Video URL": video_url, "Saved Path": video_name})
            except:
                videos_data.append({"Video URL": video_url, "Saved Path": "Download Failed"})

        ### Extract Tables ###
        tables = []
        for idx, table in enumerate(soup.find_all("table")):
            rows = []
            headers = [th.text.strip() for th in table.find_all("th")]

            for row in table.find_all("tr")[1:]:  # Skip header row
                cells = [td.text.strip() for td in row.find_all("td")]
                rows.append(cells)

            df_table = pd.DataFrame(rows, columns=headers) if headers else pd.DataFrame(rows)
            table_file = f"{domain}/table_{idx+1}.csv"
            df_table.to_csv(table_file, index=False, encoding="utf-8")
            tables.append(table_file)

        ### Detect Payment Information ###
        payment_data = []
        for tag in soup.find_all(["p", "span", "div"]):
            content = tag.text.strip().lower()
            if any(keyword in content for keyword in payment_keywords):
                payment_data.append({"Content": tag.text.strip()})

        ### Save Data to CSV ###
        pd.DataFrame(text_data).to_csv(f"{domain}/text.csv", index=False, encoding="utf-8")
        pd.DataFrame(links_data).to_csv(f"{domain}/links.csv", index=False, encoding="utf-8")
        pd.DataFrame(images_data).to_csv(f"{domain}/images.csv", index=False, encoding="utf-8")
        pd.DataFrame(videos_data).to_csv(f"{domain}/videos.csv", index=False, encoding="utf-8")
        pd.DataFrame(payment_data).to_csv(f"{domain}/payments.csv", index=False, encoding="utf-8")

        print(f"✅ Scraping complete for {url}!")
        print(f"📂 Data saved in: {domain}/")

    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
