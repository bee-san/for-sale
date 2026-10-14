"""Check the generated Jekyll site, or the deployed site via SALE_BASE_URL."""
from functools import lru_cache
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, unquote, urljoin, urlparse
from urllib.request import urlopen
import os
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASE = os.environ.get('SALE_BASE_URL', '')
ITEMS = {
    'lg-smart-monitor': ('LG 32SQ780S-W', '£180', 'power supply'),
    'xbox-360-bundle': ('Xbox 360', '£60', 'region'),
    'digimon-vital-bracelet': ('Digimon Vital Bracelet', '£50', 'Black Roar'),
    'russell-hobbs-coffee-maker': ('Russell Hobbs', '£10', 'travel mug'),
    'lenovo-thinkpad-p51': ('Lenovo ThinkPad P51', '£200', 'capacity unconfirmed'),
}


@lru_cache(maxsize=None)
def get(path):
    if BASE:
        with urlopen(urljoin(BASE, path), timeout=40) as response:
            assert response.status == 200
            return response.read()
    return (ROOT / '_site' / path).read_bytes()


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.links, self.images, self.cards = [], [], []
        self.h1_count = 0
        self.text = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'a' and a.get('href'):
            self.links.append(a['href'])
        if tag == 'img':
            self.images.append(a)
        if tag == 'article' and 'item-card' in (a.get('class') or '').split():
            self.cards.append(a)
        if tag == 'h1':
            self.h1_count += 1

    def handle_data(self, data):
        self.text.append(data)


class SaleSiteTests(unittest.TestCase):
    def page(self, path):
        return Page(get(path).decode())

    def test_home_has_exactly_the_photographed_inventory(self):
        page = self.page('index.html')
        self.assertEqual(len(page.cards), len(ITEMS))
        self.assertEqual(page.h1_count, 1)
        text = ' '.join(page.text)
        self.assertIn('London', text)
        self.assertIn('Estimated', text)
        self.assertNotIn('Example draft lamp', text)
        for slug, (title, price, _) in ITEMS.items():
            with self.subTest(item=slug):
                self.assertIn('/for-sale/items/' + slug + '/', page.links)
                self.assertIn(title, text)
                self.assertIn(price, text)

    def test_all_details_have_price_photo_condition_and_real_enquiry(self):
        for slug, (title, price, detail) in ITEMS.items():
            with self.subTest(item=slug):
                page = self.page(f'items/{slug}/index.html')
                text = ' '.join(page.text)
                self.assertEqual(page.h1_count, 1)
                for expected in (title, price, 'Estimated asking price', 'London', 'confirm', detail):
                    self.assertIn(expected, text)
                self.assertTrue(page.images)
                enquiries = [url for url in page.links if url.startswith('https://github.com/bee-san/for-sale/issues/new?')]
                self.assertEqual(len(enquiries), 1)
                query = parse_qs(urlparse(enquiries[0]).query)
                self.assertIn(title, query['title'][0])
                self.assertIn('private', query['body'][0].lower())
                self.assertIn('/for-sale/', page.links)

    def test_all_local_links_and_images_resolve_under_the_project_baseurl(self):
        for path in ['index.html'] + [f'items/{slug}/index.html' for slug in ITEMS]:
            page = self.page(path)
            for image in page.images:
                self.assertTrue(image.get('alt'), (path, image))
            for link in page.links + [img['src'] for img in page.images]:
                parsed = urlparse(link)
                if parsed.scheme or link.startswith('#'):
                    continue
                self.assertTrue(parsed.path.startswith('/for-sale/'), (path, link))
                local = unquote(parsed.path.removeprefix('/for-sale/'))
                if not local or local.endswith('/'):
                    local += 'index.html'
                self.assertTrue(get(local), (path, link))

    def test_public_photos_have_no_camera_exif_metadata(self):
        home_images = self.page('index.html').images
        self.assertEqual(len(home_images), len(ITEMS))
        images = {image['src']: image for image in home_images}
        for slug in ITEMS:
            for image in self.page(f'items/{slug}/index.html').images:
                images[image['src']] = image
        for image in images.values():
            path = image['src'].removeprefix('/for-sale/')
            data = get(path)
            self.assertNotIn(b'Exif\x00\x00', data, path)

    def test_p51_does_not_turn_estimated_storage_into_confirmed_specs(self):
        page = self.page('items/lenovo-thinkpad-p51/index.html')
        text = ' '.join(' '.join(page.text).split())
        for expected in ('around 500GB', 'capacity unconfirmed', 'Japanese',
                         'RAM', 'not demonstrated', 'charger'):
            self.assertIn(expected, text)
        self.assertEqual(len(page.images), 4)
        for unsupported in ('512GB SSD', '32GB RAM', 'fully tested', '£150', '/Users/'):
            self.assertNotIn(unsupported, text)

    def test_public_copy_does_not_expose_private_contact_or_local_paths(self):
        for path in ['index.html'] + [f'items/{slug}/index.html' for slug in ITEMS]:
            text = get(path).decode()
            self.assertNotIn('/Users/', text)
            self.assertNotIn('mailto:', text)
            self.assertNotIn('tel:', text)
            self.assertNotIn('telegram:', text)


if __name__ == '__main__':
    unittest.main(verbosity=2)
