# 3_update_latest.py
import requests
from bs4 import BeautifulSoup
import json
import time
import random

BASE_URL = "https://aniwatchtv.to"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Referer': 'https://aniwatchtv.to/',
    'X-Requested-With': 'XMLHttpRequest'
}

def get_soup(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def get_stream_url_from_ajax(episode_id):
    if not episode_id:
        print("    -> Gagal: Tidak ada ID episode.")
        return None
    
    ajax_url = f"{BASE_URL}/ajax/v2/episode/sources?id={episode_id}"
    print(f"  -> Memanggil AJAX API: {ajax_url}")
    
    try:
        response = requests.get(ajax_url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if data and 'link' in data:
            # --- [LOGIKA BARU ANDA DITERAPKAN DI SINI] ---
            base_link = data['link']
            final_stream_url = f"{base_link}&autoPlay=1&oa=0&asi=1"
            print(f"    -> Ditemukan dan dimodifikasi: {final_stream_url[:70]}...")
            return final_stream_url
            # ----------------------------------------------
        else:
            print("    -> Gagal: Respons JSON tidak valid.")
            return None
    except Exception as e:
        print(f"    -> Gagal memanggil AJAX API: {e}")
        return None

def scrape_homepage_sections(soup):
    data = {'spotlight': [], 'latest_episodes': []}
    if not soup: return data
    # Spotlight
    slider = soup.find('div', id='slider')
    if slider:
        for item in slider.find_all('div', class_='deslide-item'):
            title_el = item.find('div', class_='desi-head-title')
            watch_now_el = item.find('a', class_='btn-primary')
            if not title_el or not watch_now_el: continue
            data['spotlight'].append({
                'title': title_el.text.strip(),
                'series_watch_url': f"{BASE_URL}{watch_now_el['href']}",
                'image_url': item.find('img', class_='film-poster-img').get('data-src'),
            })
    # Latest Episodes
    section = soup.find('section', class_='block_area_home')
    if section:
        for item in section.find_all('div', class_='flw-item'):
            link_el = item.find('a', class_='film-poster-ahref')
            title_el = item.find('h3', class_='film-name a')
            if not link_el or not link_el.has_attr('href') or not link_el.has_attr('data-id'):
                continue
            data['latest_episodes'].append({
                'title': title_el.get('title', '').strip() if title_el else link_el.get('oldtitle', ''),
                'episode_id': link_el['data-id'],
                'image_url': item.find('img', class_='film-poster-img').get('data-src'),
            })
    return data

def main():
    print("Memulai scraper update terbaru (Metode AJAX Cepat)...")
    home_soup = get_soup(f"{BASE_URL}/home")
    homepage_data = scrape_homepage_sections(home_soup)

    if not homepage_data['spotlight'] and not homepage_data['latest_episodes']:
        print("Gagal mengambil data dari halaman utama. Proses dihentikan.")
        return

    print("\n--- Memproses Spotlight ---")
    for anime in homepage_data['spotlight']:
        series_soup = get_soup(anime['series_watch_url'])
        first_ep_id = None
        if series_soup:
            first_ep_el = series_soup.select_one('.ss-list .ssl-item.ep-item')
            if first_ep_el and first_ep_el.has_attr('data-id'):
                first_ep_id = first_ep_el['data-id']
        anime['stream_url'] = get_stream_url_from_ajax(first_ep_id)
        time.sleep(random.uniform(0.5, 1))
    
    print("\n--- Memproses Latest Episodes ---")
    for anime in homepage_data['latest_episodes']:
        anime['stream_url'] = get_stream_url_from_ajax(anime.get('episode_id'))
        time.sleep(random.uniform(0.5, 1))
        
    with open('anime_homepage.json', 'w', encoding='utf-8') as f:
        json.dump(homepage_data, f, ensure_ascii=False, indent=2)
    print("\nData halaman utama berhasil diperbarui di 'anime_homepage.json'")

if __name__ == "__main__":
    main()