import re
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

USD_TO_IDR = 16000

def parse_price(price_tag):
    """Konversi tag harga agar jadi float USD. Mengembalikan None kalo ga valid."""
    try:
        if price_tag is None:
            return None
        text = price_tag.get_text(strip=True)
        value = float(text.replace('$', '').replace(',', '').strip())
        return value
    except (ValueError, AttributeError):
        return None

def parse_rating(rating_tag):
    """Ekstrak nilai float rating. Kembalikan None kalo formatnya ga valid."""
    try:
        if rating_tag is None:
            return None
        text  = rating_tag.get_text(strip=True)
        match = re.search(r'\d+\.\d+', text)   # wajib desimal, tolak "Invalid Rating"
        return float(match.group()) if match else None
    except (ValueError, AttributeError):
        return None

def parse_colors(colors_tag):
    """Ambil angkanya aja dari teks colors. Kembalikan None kalo ga ada angka."""
    try:
        if colors_tag is None:
            return None
        text  = colors_tag.get_text(strip=True)
        match = re.search(r'\d+', text)
        return int(match.group()) if match else None
    except (ValueError, AttributeError):
        return None

def parse_text(tag, remove_prefix):
    """Ambil teks dari tag dan buang awalan label (misal 'Size:')."""
    try:
        if tag is None:
            return None
        return tag.get_text(strip=True).replace(remove_prefix, '').strip()
    except AttributeError:
        return None

def transform(raw_data):
    """Bersihkan dan normalisasi data mentah menjadi DataFrame siap pakai."""
    logger.info('[TRANSFORM] Proses dimulai...')

    if not raw_data:
        logger.warning('[TRANSFORM] Yaahhh tidak ada data untuk di transform:(')
        return pd.DataFrame()

    try:
        cleaned = []
        for item in raw_data:
            price_usd = parse_price(item.get('Price'))

            cleaned.append({
                'title':     item['Title'].get_text(strip=True) if item.get('Title') else None,
                'price':     round(price_usd * USD_TO_IDR, 2) if price_usd else None,
                'rating':    parse_rating(item.get('Rating')),
                'colors':    parse_colors(item.get('Colors')),
                'size':      parse_text(item.get('Size'),   'Size:'),
                'gender':    parse_text(item.get('Gender'), 'Gender:'),
                'timestamp': item.get('timestamp'),
            })

        df = pd.DataFrame(cleaned)

        before = len(df)

        # Hapus semua baris yang mengandung nilai null di kolom apapun
        df.dropna(inplace=True)

        # Hapus produk dengan nama tidak valid
        df = df[df['title'] != 'Unknown Product']

        # Hapus duplikat
        df.drop_duplicates(inplace=True)

        # Pastikan tipe data benar
        df['price']  = df['price'].astype(float)
        df['rating'] = df['rating'].astype(float)
        df['colors'] = df['colors'].astype(int)
        df['size']   = df['size'].astype(str)
        df['gender'] = df['gender'].astype(str)

        df.reset_index(drop=True, inplace=True)

        logger.info(f'[TRANSFORM] Baris awal: {before} → setelah bersih(after): {len(df)} produk')
        logger.info(f'[TRANSFORM] Baris dihapus: {before - len(df)}\n')
        return df

    except Exception as e:
        logger.error(f'[TRANSFORM] Yaahhh!!! gagal melakukan transformasi: {e}')
        raise
