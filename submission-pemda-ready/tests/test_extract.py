import unittest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.extract import extract, get_page, scrape_page

def html_page(title='Kaos Keren', price='$29.99', colors='Colors: 3',
              size='Size: M', gender='Gender: Men', rating='Rating: ⭐4.5 / 5'):
    return f"""<html><body>
    <div class="collection-card">
        <h3 class="product-title">{title}</h3>
        <span class="price">{price}</span>
        <p>{colors}</p><p>{size}</p><p>{gender}</p><p>{rating}</p>
    </div>
    </body></html>"""

class TestGetPage(unittest.TestCase):

    @patch('utils.extract.requests.get')
    def test_berhasil_mengembalikan_soup(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200, text='<html></html>')
        mock_get.return_value.raise_for_status = MagicMock()
        result = get_page('https://fashion-studio.dicoding.dev')
        self.assertIsNotNone(result)

    @patch('utils.extract.requests.get')
    def test_raise_http_error(self, mock_get):
        import requests
        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=MagicMock(status_code=404))
        mock_get.return_value = mock_resp
        with self.assertRaises(requests.exceptions.HTTPError):
            get_page('https://fashion-studio.dicoding.dev/page999')

    @patch('utils.extract.requests.get')
    def test_raise_timeout(self, mock_get):
        import requests
        mock_get.side_effect = requests.exceptions.Timeout
        with self.assertRaises(requests.exceptions.Timeout):
            get_page('https://fashion-studio.dicoding.dev')

    @patch('utils.extract.requests.get')
    def test_raise_connection_error(self, mock_get):
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError
        with self.assertRaises(requests.exceptions.ConnectionError):
            get_page('https://fashion-studio.dicoding.dev')


class TestScrapePage(unittest.TestCase):

    def test_ekstrak_satu_produk(self):
        soup = BeautifulSoup(html_page(), 'html.parser')
        result = scrape_page(soup, 'https://fashion-studio.dicoding.dev')
        self.assertEqual(len(result), 1)

    def test_semua_field_ada(self):
        soup   = BeautifulSoup(html_page(), 'html.parser')
        result = scrape_page(soup, 'https://fashion-studio.dicoding.dev')
        for field in ['Title', 'Price', 'Colors', 'Size', 'Gender', 'Rating', 'timestamp']:
            self.assertIn(field, result[0])

    def test_timestamp_tidak_none(self):
        soup   = BeautifulSoup(html_page(), 'html.parser')
        result = scrape_page(soup, 'https://fashion-studio.dicoding.dev')
        self.assertIsNotNone(result[0]['timestamp'])

    def test_halaman_kosong_kembalikan_list_kosong(self):
        soup   = BeautifulSoup('<html><body></body></html>', 'html.parser')
        result = scrape_page(soup, 'https://fashion-studio.dicoding.dev')
        self.assertEqual(result, [])


class TestExtract(unittest.TestCase):

    @patch('utils.extract.requests.get')
    def test_scraping_satu_halaman(self, mock_get):
        resp_ok  = MagicMock(status_code=200, text=html_page())
        resp_ok.raise_for_status = MagicMock()
        import requests
        mock_resp_404 = MagicMock()
        mock_resp_404.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=MagicMock(status_code=404))
        mock_get.side_effect = [resp_ok, mock_resp_404]
        result = extract()
        self.assertEqual(len(result), 1)

    @patch('utils.extract.requests.get')
    def test_berhenti_jika_tidak_ada_produk(self, mock_get):
        resp = MagicMock(status_code=200, text='<html><body></body></html>')
        resp.raise_for_status = MagicMock()
        mock_get.return_value = resp
        result = extract()
        self.assertEqual(result, [])

    @patch('utils.extract.requests.get')
    def test_scraping_dua_halaman(self, mock_get):
        resp_ok = MagicMock(status_code=200, text=html_page())
        resp_ok.raise_for_status = MagicMock()
        import requests
        resp_404 = MagicMock()
        resp_404.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=MagicMock(status_code=404))
        mock_get.side_effect = [resp_ok, resp_ok, resp_404]
        result = extract()
        self.assertEqual(len(result), 2)

    @patch('utils.extract.requests.get')
    def test_produk_memiliki_timestamp(self, mock_get):
        resp_ok = MagicMock(status_code=200, text=html_page())
        resp_ok.raise_for_status = MagicMock()
        import requests
        resp_404 = MagicMock()
        resp_404.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=MagicMock(status_code=404))
        mock_get.side_effect = [resp_ok, resp_404]
        result = extract()
        self.assertIn('timestamp', result[0])
        self.assertIsNotNone(result[0]['timestamp'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
