# 2_enrich_details.py
import requests
from bs4 import BeautifulSoup
import json
import time
import os

BASE_URL = "https://aniwatchtv.to"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}

def get_soup(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"  -> Gagal mengambil halaman detail: {e}")
        return None

def scrape_anime_details(detail_url):
    print(f"  -> Mengambil detail dari: {detail_url}")
    soup = get_soup(detail_url)
    if not soup: return None

    synopsis_el = soup.select_one('.anisc-detail .film-description .text')
    synopsis = synopsis_el.text.strip().replace('... + More', '...').strip() if synopsis_el else "No synopsis available."

    genres = [a.text for a in soup.select('.anisc-info .item-list a[href*="/genre/"]')]

    episodes = []
    episode_items = soup.select('.ss-list .ssl-item.ep-item')
    for ep_item in episode_items:
        episodes.append({
            'episode_num': ep_item.get('data-number', 'N/A'),
            'title': ep_item.select_one('.ep-name').text.strip(),
            'episode_id': ep_item.get('data-id', None) # <-- MENGAMBIL ID EPISODE
        })

    return {
        'synopsis': synopsis,
        'genres': genres,
        'episodes': episodes
    }

def main():
    try:
        with open('anime_catalog.json', 'r', encoding='utf-8') as f:
            catalog = json.load(f)
    except FileNotFoundError:
        print("File 'anime_catalog.json' tidak ditemukan. Jalankan '1_build_catalog.py' terlebih dahulu.")
        return

    details_file = 'anime_details.json'
    enriched_details = {}
    if os.path.exists(details_file):
        with open(details_file, 'r', encoding='utf-8') as f:
            enriched_details = json.load(f)

    print(f"Memulai proses melengkapi detail. {len(enriched_details)}/{len(catalog)} sudah selesai.")

    for i, anime in enumerate(catalog):
        anime_id = anime['id']
        if anime_id in enriched_details:
            continue

        print(f"Memproses {i+1}/{len(catalog)}: {anime['title']}")
        details = scrape_anime_details(anime['detail_url'])
        
        if details:
            enriched_details[anime_id] = {
                'title': anime['title'],
                'image_url': anime['image_url'],
                **details
            }
            with open(details_file, 'w', encoding='utf-8') as f:
                json.dump(enriched_details, f, ensure_ascii=False, indent=2)
        
        time.sleep(1)

    print("\nProses melengkapi detail selesai.")

if __name__ == "__main__":
    main()