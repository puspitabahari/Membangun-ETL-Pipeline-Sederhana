import logging
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def load_csv(df, filepath='products.csv'):
    """Simpan DataFrame ke file CSV."""
    try:
        if df.empty:
            logger.warning('[LOAD] YAAHH!!! DataFrame kosong, ga ada data yang disimpan ke CSV.')
            return
        df.to_csv(filepath, index=False)
        logger.info(f'[LOAD] [YEAY SUCCESS] CSV   → {filepath} ({len(df)} produk)')
    except PermissionError:
        logger.error(f'[LOAD] NOOOO!!! Ga ada izin menulis ke {filepath}')
        raise
    except Exception as e:
        logger.error(f'[LOAD] YAAAAHH!!! gagal menyimpan CSV: {e}')
        raise

def load_google_sheets(df, spreadsheet_id, credentials_file='google-sheets-api.json'):
    """Simpan DataFrame ke Google Sheets."""
    if df.empty:
        logger.warning('[LOAD] NOO!! DataFrame kosong. Jadi ga ada file yang disimpan ke google sheet')
        return
    try:
        import gspread
        from google.oauth2.service_account import Credentials

        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive',
        ]
        creds  = Credentials.from_service_account_file(credentials_file, scopes=scopes)
        client = gspread.authorize(creds)
        sheet  = client.open_by_key(spreadsheet_id).sheet1
        sheet.clear()
        data = [df.columns.tolist()] + df.astype(str).values.tolist()
        sheet.update(data)
        logger.info(f'[LOAD] [YEAY SUCCESS] Google Sheets ke spreadsheet_id={spreadsheet_id} ({len(df)} produk)')
    except FileNotFoundError:
        logger.error(f'[LOAD] YAAHH!! Ga ada ditemukan apa-apa: {credentials_file}')
        raise
    except Exception as e:
        logger.error(f'[LOAD] YAAH!! Gagal menyimpan ke Google Sheets: {e}')
        raise

def load_postgresql(df, connection_string):
    """Simpan DataFrame ke PostgreSQL."""
    if df.empty:
        logger.warning('[LOAD] NOOOO!! DataFrame kosong, tidak ada data yang disimpan ke PostgreSQL.')
        return
    try:
        from sqlalchemy import create_engine
        engine = create_engine(connection_string)
        df.to_sql('products', engine, if_exists='replace', index=False)
        logger.info(f'[LOAD] [YEAY SUCCESS] PostgreSQL ke tabel "products" ({len(df)} produk)')
    except Exception as e:
        logger.error(f'[LOAD] NOO!! Gagal menyimpan ke PostgreSQL: {e}')
        raise

def load(df, csv_path='products.csv', spreadsheet_id=None,
         credentials_file='google-sheets-api.json', pg_connection=None):
    """
    Titik masuk utama Load — simpan ke semua repositori yang dikonfigurasi.
      - CSV          : selalu aktif
      - Google Sheets: aktif jika spreadsheet_id diisi
      - PostgreSQL   : aktif jika pg_connection diisi
    """
    logger.info('[LOAD] tungguu sedang loading yaa...')
    load_csv(df, csv_path)
    if spreadsheet_id:
        load_google_sheets(df, spreadsheet_id, credentials_file)
    if pg_connection:
        load_postgresql(df, pg_connection)
    logger.info('[LOAD] Terimakasih telah menunggu, proses selesai.\n')
