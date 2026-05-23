import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.load import load_csv, load_google_sheets, load_postgresql, load

def sample_df():
    return pd.DataFrame([{
        'title': 'Kaos Keren', 'price': 479840.0, 'rating': 4.5,
        'colors': 3, 'size': 'M', 'gender': 'Men',
        'timestamp': '2024-01-01T10:00:00'
    }])


class TestLoadCSV(unittest.TestCase):

    def setUp(self):
        self.path = r"D:\submission-pemda\tests\test_data.csv"

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_file_csv_terbuat(self):
        load_csv(sample_df(), self.path)
        self.assertTrue(os.path.exists(self.path))

    def test_jumlah_baris_sesuai(self):
        load_csv(sample_df(), self.path)
        loaded = pd.read_csv(self.path)
        self.assertEqual(len(loaded), 1)

    def test_kolom_sesuai(self):
        load_csv(sample_df(), self.path)
        loaded = pd.read_csv(self.path)
        for col in sample_df().columns:
            self.assertIn(col, loaded.columns)

    def test_dataframe_kosong_tidak_error(self):
        load_csv(pd.DataFrame(), self.path)  # tidak boleh raise

    @patch('utils.load.pd.DataFrame.to_csv', side_effect=PermissionError)
    def test_raise_permission_error(self, mock_csv):
        with self.assertRaises(PermissionError):
            load_csv(sample_df(), r"D:\submission-pemda\tests\test_data.csv")


class TestLoadGoogleSheets(unittest.TestCase):

    def test_dataframe_kosong_tidak_error(self):
        # Cek early return sebelum import gspread — tidak boleh raise
        load_google_sheets(pd.DataFrame(), 'sheet_id', 'google-sheets-api.json')

    def test_file_credentials_tidak_ada(self):
        with self.assertRaises(Exception):
            load_google_sheets(sample_df(), 'sheet_id', 'tidak_ada.json')


class TestLoadPostgreSQL(unittest.TestCase):

    def test_dataframe_kosong_tidak_error(self):
        # Cek early return sebelum import sqlalchemy — tidak boleh raise
        load_postgresql(pd.DataFrame(), 'postgresql://localhost/db')

    def test_connection_string_invalid(self):
        with self.assertRaises(Exception):
            load_postgresql(sample_df(), 'postgresql://invalid:invalid@localhost/db')


class TestLoad(unittest.TestCase):

    def setUp(self):
        self.path = r"D:\submission-pemda\tests\test_data.csv"

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_load_csv_saja(self):
        load(sample_df(), csv_path=self.path)
        self.assertTrue(os.path.exists(self.path))

    def test_load_tanpa_sheets_dan_pg(self):
        load(sample_df(), csv_path=self.path, spreadsheet_id=None, pg_connection=None)
        self.assertTrue(os.path.exists(self.path))

    @patch('utils.load.load_google_sheets')
    def test_sheets_dipanggil_jika_ada_id(self, mock_sheets):
        load(sample_df(), csv_path=self.path, spreadsheet_id='abc123')
        mock_sheets.assert_called_once()

    @patch('utils.load.load_postgresql')
    def test_pg_dipanggil_jika_ada_connection(self, mock_pg):
        load(sample_df(), csv_path=self.path, pg_connection='postgresql://localhost/db')
        mock_pg.assert_called_once()


if __name__ == '__main__':
    unittest.main(verbosity=2)
