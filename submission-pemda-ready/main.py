from utils.extract   import extract
from utils.transform import transform
from utils.load import load

SPREADSHEET_ID = '18W0UyYSQvbZR-bazWqKJpAZbyox0xAsk2o_D_3HQYWY'
CREDENTIALS = 'google-sheets-api.json'
PG_CONNECTION = 'postgresql://postgres:Skypiezoro@localhost:5432/fashion_db'
 
if __name__ == "__main__":
    raw_data = extract()
    df       = transform(raw_data)
    load(
        df,
        csv_path = 'products.csv',
        spreadsheet_id = SPREADSHEET_ID,
        credentials_file = CREDENTIALS,
        pg_connection = PG_CONNECTION,
    )