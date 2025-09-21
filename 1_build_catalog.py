# 1_build_catalog.py
import requests
from bs4 import BeautifulSoup
import json
import time

BASE_URL = "https://aniwatchtv.to"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
}

def get_soup(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def main():
    print("Memulai scraping seluruh katalog anime (A-Z)...")
    catalog = []
    az_list_url = f"{BASE_URL}/az-list"
    
    soup = get_soup(az_list_url)
    if not soup:
        print("Gagal membuka halaman A-Z list utama.")
        return

    az_links = soup.select('.az-list a[href*="/az-list/"]')
    
    for link in az_links:
        char_page_url = f"{BASE_URL}{link['href']}"
        char = link.text.strip()
        if len(char) > 1 and char != '0-9': continue

        print(f"\nScraping untuk karakter: '{char}'")
        
        page_num = 1
        while True:
            paginated_url = f"{char_page_url}?page={page_num}"
            print(f"  -> Mengambil halaman: {page_num}")
            
            page_soup = get_soup(paginated_url)
            if not page_soup:
                break
                
            anime_items = page_soup.select('.film_list-wrap .flw-item')
            if not anime_items:
                print(f"  -> Selesai untuk karakter '{char}'.")
                break

            for item in anime_items:
                title_el = item.find('h3', class_='film-name').find('a')
                if not title_el: continue
                
                detail_url = f"{BASE_URL}{title_el['href']}"
                anime_id = detail_url.split('/')[-1]

                catalog.append({
                    'id': anime_id,
                    'title': title_el.get('title', '').strip(),
                    'detail_url': detail_url,
                    'image_url': item.find('img', class_='film-poster-img').get('data-src')
                })

            page_num += 1
            time.sleep(0.5)

    with open('anime_catalog.json', 'w', encoding='utf-8') as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)
    print(f"\nTotal {len(catalog)} anime dari katalog berhasil disimpan di 'anime_catalog.json'")

if __name__ == "__main__":
    main()