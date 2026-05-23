import requests
import logging
from datetime import datetime
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = 'https://fashion-studio.dicoding.dev'
HEADERS  = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        'Chrome/91.0.4472.124 Safari/537.36'
    )
}

def get_page(url):
    """Ambil satu halaman, kembalikan BeautifulSoup. Raise exception jika gagal."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.Timeout:
        logger.error(f'[EXTRACT] Timeout {url}')
        raise
    except requests.exceptions.ConnectionError:
        logger.error(f'[EXTRACT] KONEKSI GAGAL KE {url} !')
        raise
    except requests.exceptions.HTTPError as e:
        logger.error(f'[EXTRACT] HTTP ERROR {e.response.status_code} pada {url} !')
        raise

def scrape_page(soup, page_url):
    """Melakukan ekstraksi pada semua product card di satu halaman."""
    product_cards = soup.find_all('div', class_='collection-card')
    if not product_cards:
        return []

    results = []
    timestamp = datetime.now().isoformat()
    for card in product_cards:
        results.append({
            'Title':     card.find('h3', class_='product-title'),
            'Price':     card.find('span', class_='price'),
            'Colors':    card.find('p', string=lambda t: t and 'Colors' in t),
            'Size':      card.find('p', string=lambda t: t and 'Size' in t),
            'Gender':    card.find('p', string=lambda t: t and 'Gender' in t),
            'Rating':    card.find('p', string=lambda t: t and 'Rating' in t),
            'timestamp': timestamp,
        })
    return results

def extract():
    """Melakukan scraping semua produk di halam website."""
    raw_data = []
    page     = 1

    logger.info('[EXTRACT] Proses scraping dimulai ...')

    while True:
        url = BASE_URL if page == 1 else f'{BASE_URL}/page{page}'
        logger.info(f'[EXTRACT] Scraping pada {url}:{page}')

        try:
            soup = get_page(url)
        except requests.exceptions.HTTPError:
            logger.info(f'[EXTRACT] Pada halaman {page} TIDAK DITEMUKAN. Scraping selesai!')
            break
        except Exception as e:
            logger.error(f'[EXTRACT] GAGAL mengambil halaman {page}: {e}. Melewati halaman ini.')
            break

        products = scrape_page(soup, url)
        if not products:
            logger.info(f'[EXTRACT] TIDAK ADA produk di halaman {page}. Scraping selesai.')
            break

        raw_data.extend(products)
        logger.info(f'[EXTRACT] {len(products)} yeay!! produk ditemukan di halaman {page}.')
        page += 1

    logger.info(f'[EXTRACT] Total produk (masih mentah): {len(raw_data)}\n')
    return raw_data
