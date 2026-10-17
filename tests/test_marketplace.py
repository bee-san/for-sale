"""Bargain pricing and a copy-only Vinted workspace, not automatic posting."""
import json
import re
import subprocess
import unittest
from pathlib import Path
from test_site import Page, get

ROOT = Path(__file__).resolve().parents[1]
BARGAINS = {
    'lg-smart-monitor': 100, 'xbox-360-bundle': 20,
    'digimon-vital-bracelet': 20, 'russell-hobbs-coffee-maker': 5,
    'lenovo-thinkpad-p51': 100, 'jurassic-park': 1, 'emperor-of-rome': 5,
    'short-stories-japanese-intermediate': 2, 'dandadan-vol-1-japanese': 1,
    'demon-slayer-rengoku-zero': 3, 'the-secret-history': 1,
    'japanese-keigo-handbook': 1, 'tapo-doorbell': 10,
    'thinkpad-x1-carbon-gen5': 20, 'famitsu-steins-gate-reboot': 2,
    'the-secret-of-secrets': 2, 'lumie-bodyclock-shine-300': 25,
    'renpho-smart-tape-measure': 3, 'wd-red-3tb': 8, 'kensington-sd5700t': 25,
    'corsair-desktop-ram-pair': 3, 'wii-u-mario-maker-bundle': 30,
    'ugreen-steam-deck-dock': 7, 'pro-breeze-pb03': 5,
    'honeywell-ht900e': 4, 'sony-dualshock-4-white': 5,
    'yarn-bundle': 2, 'needle-felting-tools-bundle': 3,
    'flesh-and-blood-playmat': 5,
}


class MarketplaceSourceTests(unittest.TestCase):
    def data(self):
        path = ROOT / '_data/vinted_drafts.json'
        self.assertTrue(path.is_file(), 'The Vinted copy workspace data is missing')
        return json.loads(path.read_text())

    def test_every_inventory_item_has_one_draft(self):
        rows = self.data()
        slugs = [row['slug'] for row in rows]
        self.assertEqual(len(slugs), len(set(slugs)))
        self.assertEqual(set(slugs), set(BARGAINS))
        self.assertEqual({p.stem for p in (ROOT / '_items').glob('*.md')}, set(BARGAINS))

    def test_all_catalogue_prices_match_bargain_targets(self):
        for slug, price in BARGAINS.items():
            with self.subTest(item=slug):
                path = ROOT / '_items' / (slug + '.md')
                self.assertTrue(path.is_file(), 'Missing photographed item: ' + slug)
                text = path.read_text()
                actual = re.search(r'^price: "(\d+)"$', text, re.M)
                self.assertIsNotNone(actual)
                assert actual is not None
                self.assertEqual(int(actual[1]), price)
                # Model numbers/capacities and research comparables are not asking prices.
                asks = re.findall(r'£(\d+)\b', text)
                self.assertTrue(asks)
                self.assertEqual(set(asks), {str(price)})

    def test_buyer_copy_is_plain_truthful_and_separate_from_seller_checks(self):
        for row in self.data():
            with self.subTest(item=row['slug']):
                self.assertIn(row['readiness'], ('ready', 'check', 'other'))
                self.assertTrue(row['reason'])
                self.assertTrue(row['checks'])
                self.assertTrue(row['packing'])
                self.assertLessEqual(len(row['title']), 100)
                self.assertLessEqual(len(row['description']), 2000)
                for field in ('title', 'description'):
                    value = row[field]
                    self.assertTrue(value.strip())
                    self.assertNotRegex(value, r'https?://|mailto:|tel:|/Users/|TODO|INSERT|[—–]')
                    self.assertNotIn('London collection', value)
                    self.assertNotIn('Before publishing', value)
                self.assertNotIn('price', row, 'Price must come from the listing, not a second editable copy')
                if row['readiness'] == 'ready':
                    self.assertNotIn(row['slug'], ('thinkpad-x1-carbon-gen5', 'wii-u-mario-maker-bundle'))

    def test_copy_buttons_and_manual_fallback_execute(self):
        result = subprocess.run(['node', '--test', str(ROOT / 'tests/test_copy.js')],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_material_faults_and_import_limits_are_preserved(self):
        rows = {row['slug']: row for row in self.data()}
        self.assertIn('broken screen', rows['thinkpad-x1-carbon-gen5']['description'].lower())
        self.assertEqual(rows['thinkpad-x1-carbon-gen5']['readiness'], 'other')
        self.assertIn('Japanese', rows['wii-u-mario-maker-bundle']['description'])
        self.assertIn('EEA', ' '.join(rows['wii-u-mario-maker-bundle']['checks']))
        self.assertIn('signed', rows['emperor-of-rome']['description'].lower())
        self.assertIn('stained', rows['japanese-keigo-handbook']['description'].lower())
        self.assertIn('scratches', rows['tapo-doorbell']['description'].lower())
        self.assertIn('missing', rows['tapo-doorbell']['description'].lower())
        self.assertEqual(rows['tapo-doorbell']['readiness'], 'check')
        self.assertNotIn('512GB', rows['lenovo-thinkpad-p51']['description'])
        self.assertNotIn('16GB', rows['corsair-desktop-ram-pair']['description'])


class CopyPage(Page):
    def __init__(self, html):
        self.fields, self.targets, self.labels = {}, [], {}
        self.current = None
        super().__init__(html)

    def handle_starttag(self, tag, attrs):
        super().handle_starttag(tag, attrs)
        values = dict(attrs)
        if tag == 'textarea':
            self.current = values['id']
            self.fields[self.current] = ''
        if tag == 'button' and values.get('data-copy-target'):
            self.targets.append(values['data-copy-target'])
        if tag == 'label' and values.get('for'):
            self.labels[values['for']] = True

    def handle_endtag(self, tag):
        if tag == 'textarea':
            self.current = None

    def handle_data(self, data):
        super().handle_data(data)
        if self.current:
            self.fields[self.current] += data


class MarketplaceRenderedTests(unittest.TestCase):
    def test_copy_page_contains_all_titles_descriptions_and_current_prices(self):
        page = CopyPage(get('vinted/index.html').decode())
        manifest = json.loads(get('vinted/manifest.json'))
        self.assertEqual(page.h1_count, 1)
        self.assertEqual({row['slug'] for row in manifest}, set(BARGAINS))
        self.assertEqual(len(page.targets), len(BARGAINS) * 3)
        self.assertEqual(len(page.targets), len(set(page.targets)))
        for row in manifest:
            slug = row['slug']
            self.assertEqual(str(row['price']), str(BARGAINS[slug]))
            for name in ('title', 'description', 'price'):
                key = name + '-' + slug
                self.assertIn(key, page.targets)
                self.assertIn(key, page.labels)
                self.assertEqual(page.fields[key], str(row[name]))
        text = ' '.join(page.text)
        for value in ('Before publishing', 'Nothing is posted automatically', 'Check before listing', 'Use another marketplace'):
            self.assertIn(value, text)

    def test_workspace_navigation_assets_and_manual_fallback_exist(self):
        page = Page(get('vinted/index.html').decode())
        self.assertIn('/for-sale/', page.links)
        self.assertIn('/for-sale/vinted/', Page(get('index.html').decode()).links)
        self.assertTrue(get('assets/js/vinted-copy.js'))
        script = get('assets/js/vinted-copy.js').decode()
        self.assertIn('navigator.clipboard.writeText', script)
        self.assertIn('.select()', script)
        self.assertIn('Copy manually', script)
        self.assertNotIn('fetch(', script)
        for image in page.images:
            self.assertTrue(image.get('alt'))
            self.assertTrue(get(image['src'].removeprefix('/for-sale/')))
        for url in page.links:
            if '://' in url or url.startswith('#'):
                continue
            path = url.split('#')[0].removeprefix('/for-sale/')
            if not path or path.endswith('/'):
                path += 'index.html'
            self.assertTrue(get(path), url)


if __name__ == '__main__':
    unittest.main(verbosity=2)
