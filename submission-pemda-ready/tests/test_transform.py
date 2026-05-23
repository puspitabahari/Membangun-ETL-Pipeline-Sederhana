import unittest
from bs4 import BeautifulSoup
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.transform import transform, parse_price, parse_rating, parse_colors, parse_text

def make_tag(html):
    return BeautifulSoup(html, 'html.parser').find()

def make_raw(title='Kaos Keren', price='$29.99', colors='Colors: 3',
             size='Size: M', gender='Gender: Men', rating='⭐ 4.5 / 5',
             timestamp='2024-01-01T10:00:00'):
    html = f"""<div>
        <h3 class="product-title">{title}</h3>
        <span class="price">{price}</span>
        <p>{colors}</p><p>{size}</p><p>{gender}</p><p>{rating}</p>
    </div>"""
    card = BeautifulSoup(html, 'html.parser').find('div')
    return {
        'Title':     card.find('h3'),
        'Price':     card.find('span'),
        'Colors':    card.find('p', string=lambda t: t and 'Colors' in t),
        'Size':      card.find('p', string=lambda t: t and 'Size' in t),
        'Gender':    card.find('p', string=lambda t: t and 'Gender' in t),
        'Rating':    card.find('p', string=lambda t: t and ('Rating' in t or '⭐' in t)),
        'timestamp': timestamp,
    }


class TestParsePrice(unittest.TestCase):
    def test_harga_normal(self):
        self.assertEqual(parse_price(make_tag('<span>$29.99</span>')), 29.99)

    def test_harga_tanpa_desimal(self):
        self.assertEqual(parse_price(make_tag('<span>$30</span>')), 30.0)

    def test_price_unavailable(self):
        self.assertIsNone(parse_price(make_tag('<span>Price Unavailable</span>')))

    def test_tag_none(self):
        self.assertIsNone(parse_price(None))


class TestParseRating(unittest.TestCase):
    def test_format_bintang(self):
        self.assertEqual(parse_rating(make_tag('<p>⭐ 4.5 / 5</p>')), 4.5)

    def test_invalid_rating(self):
        self.assertIsNone(parse_rating(make_tag('<p>Invalid Rating</p>')))

    def test_tag_none(self):
        self.assertIsNone(parse_rating(None))

    def test_rating_integer_saja(self):
        # "Rating: 4" tanpa desimal harus None (wajib format x.x)
        self.assertIsNone(parse_rating(make_tag('<p>Rating: 4</p>')))


class TestParseColors(unittest.TestCase):
    def test_format_colors(self):
        self.assertEqual(parse_colors(make_tag('<p>3 Colors</p>')), 3)

    def test_format_dengan_titik_dua(self):
        self.assertEqual(parse_colors(make_tag('<p>Colors: 5</p>')), 5)

    def test_tag_none(self):
        self.assertIsNone(parse_colors(None))

    def test_hasilnya_integer(self):
        result = parse_colors(make_tag('<p>Colors: 3</p>'))
        self.assertIsInstance(result, int)


class TestTransform(unittest.TestCase):

    def test_price_dikonversi_ke_idr(self):
        df = transform([make_raw(price='$10.00')])
        self.assertEqual(df['price'][0], 160000.0)

    def test_rating_berupa_float(self):
        df = transform([make_raw(rating='⭐ 3.9 / 5')])
        self.assertEqual(df['rating'][0], 3.9)

    def test_colors_berupa_integer(self):
        df = transform([make_raw(colors='Colors: 3')])
        self.assertTrue(isinstance(df['colors'][0], (int, __builtins__['int'])) or str(type(df['colors'][0])).__contains__('int'))
        self.assertEqual(df['colors'][0], 3)

    def test_size_tanpa_prefix(self):
        df = transform([make_raw(size='Size: L')])
        self.assertEqual(df['size'][0], 'L')

    def test_gender_tanpa_prefix(self):
        df = transform([make_raw(gender='Gender: Women')])
        self.assertEqual(df['gender'][0], 'Women')

    def test_kolom_timestamp_ada(self):
        df = transform([make_raw()])
        self.assertIn('timestamp', df.columns)

    def test_kolom_lengkap(self):
        df = transform([make_raw()])
        for col in ['title', 'price', 'rating', 'colors', 'size', 'gender', 'timestamp']:
            self.assertIn(col, df.columns)

    def test_baris_price_invalid_dihapus(self):
        raw = [make_raw(), make_raw(price='Price Unavailable')]
        df  = transform(raw)
        self.assertEqual(len(df), 1)

    def test_baris_rating_invalid_dihapus(self):
        raw = [make_raw(), make_raw(rating='Invalid Rating')]
        df  = transform(raw)
        self.assertEqual(len(df), 1)

    def test_unknown_product_dihapus(self):
        df = transform([make_raw(title='Unknown Product')])
        self.assertTrue(df.empty)

    def test_duplikat_dihapus(self):
        raw = [make_raw(), make_raw()]
        df  = transform(raw)
        self.assertEqual(len(df), 1)

    def test_tidak_ada_null(self):
        df = transform([make_raw()])
        self.assertEqual(df.isnull().sum().sum(), 0)

    def test_input_kosong(self):
        df = transform([])
        self.assertTrue(df.empty)

    def test_tipe_data_price_float(self):
        df = transform([make_raw()])
        self.assertEqual(df['price'].dtype, float)

    def test_tipe_data_rating_float(self):
        df = transform([make_raw()])
        self.assertEqual(df['rating'].dtype, float)


if __name__ == '__main__':
    unittest.main(verbosity=2)
