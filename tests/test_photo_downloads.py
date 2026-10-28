"""Download buttons must deliver every public photo, never private originals."""
from html.parser import HTMLParser
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
import zipfile
from test_site import Page, get

ROOT = Path(__file__).resolve().parents[1]


def expected_photos():
    return {path.stem: list(dict.fromkeys(re.findall(r'/assets/images/[A-Za-z0-9._-]+', path.read_text())))
            for path in sorted((ROOT / '_items').glob('*.md'))}


class PhotoDownloadSourceTests(unittest.TestCase):
    def manifest(self):
        path = ROOT / '_data/photo_downloads.json'
        self.assertTrue(path.is_file(), 'Per-item photo download bundles have not been implemented')
        return json.loads(path.read_text())

    def builder(self):
        path = ROOT / 'scripts/build_photo_downloads.py'
        self.assertTrue(path.is_file(), 'The deterministic public-photo bundle builder is missing')
        spec = importlib.util.spec_from_file_location('photo_builder', path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_each_item_bundle_contains_exact_public_photo_bytes(self):
        data = self.manifest()
        expected = expected_photos()
        self.assertEqual(set(data['items']), set(expected))
        self.assertEqual(data['item_count'], len(expected))
        for slug, photos in expected.items():
            with self.subTest(item=slug):
                row = data['items'][slug]
                self.assertEqual(row['photos'], photos)
                self.assertEqual(row['count'], len(photos))
                archive_path = ROOT / row['archive'].lstrip('/')
                self.assertTrue(archive_path.is_file())
                with zipfile.ZipFile(archive_path) as archive:
                    self.assertIsNone(archive.testzip())
                    names = archive.namelist()
                    self.assertEqual(len(names), len(photos))
                    self.assertEqual(len(names), len(set(names)))
                    for index, (name, photo) in enumerate(zip(names, photos), start=1):
                        self.assertEqual(name, f'{index:02d}-' + Path(photo).name)
                        self.assertNotIn('/', name)
                        image = archive.read(name)
                        self.assertEqual(image, (ROOT / photo.lstrip('/')).read_bytes())
                        self.assertNotIn(b'Exif\x00\x00', image)

    def test_all_photos_bundle_is_grouped_by_listing(self):
        data = self.manifest()
        expected = expected_photos()
        self.assertEqual(data['photo_count'], sum(map(len, expected.values())))
        with zipfile.ZipFile(ROOT / data['all_archive'].lstrip('/')) as archive:
            self.assertIsNone(archive.testzip())
            names = archive.namelist()
            self.assertEqual(len(names), data['photo_count'])
            for slug, photos in expected.items():
                for index, photo in enumerate(photos, start=1):
                    name = f'{slug}/{index:02d}-' + Path(photo).name
                    self.assertIn(name, names)
                    self.assertEqual(archive.read(name), (ROOT / photo.lstrip('/')).read_bytes())

    def test_bundles_are_current_and_deterministic(self):
        self.builder()
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/build_photo_downloads.py'), '--check'],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_builder_preserves_photo_order_and_removes_repeat_references(self):
        module = self.builder()
        with tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR')) as directory:
            root = Path(directory)
            (root / '_items').mkdir()
            images = root / 'assets/images'
            images.mkdir(parents=True)
            (images / 'front.jpg').write_bytes(b'test front image')
            (images / 'rear.jpg').write_bytes(b'test rear image')
            (root / '_items/example.md').write_text('---\nimage: /assets/images/front.jpg\n---\n/assets/images/rear.jpg\n/assets/images/front.jpg\n')
            self.assertEqual(module.collect_photos(root), {'example': ['/assets/images/front.jpg', '/assets/images/rear.jpg']})

    def test_builder_rejects_symlink_to_private_original(self):
        module = self.builder()
        with tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR')) as directory:
            root = Path(directory)
            (root / '_items').mkdir()
            (root / 'assets/images').mkdir(parents=True)
            private = root / 'private-original.jpg'
            private.write_bytes(b'private test fixture')
            (root / 'assets/images/leak.jpg').symlink_to(private)
            (root / '_items/example.md').write_text('---\nimage: /assets/images/leak.jpg\n---\n')
            with self.assertRaises(ValueError):
                module.collect_photos(root)


class DownloadPage(Page):
    def __init__(self, source):
        self.downloads = []
        self.previews = []
        self.photo_images = []
        self.current_preview = None
        self.current_item = None
        super().__init__(source)

    def handle_starttag(self, tag, attrs):
        super().handle_starttag(tag, attrs)
        values = dict(attrs)
        if tag == 'details' and values.get('id', '').startswith('draft-'):
            self.current_item = values['id'].removeprefix('draft-')
        if tag == 'a' and 'download' in values:
            self.downloads.append((self.current_item, values))
        if tag == 'a' and 'data-photo-preview' in values:
            self.current_preview = values
            self.previews.append((self.current_item, values))
        if tag == 'img' and self.current_item:
            self.photo_images.append((self.current_item, self.current_preview, values))

    def handle_endtag(self, tag):
        if tag == 'a':
            self.current_preview = None
        if tag == 'details':
            self.current_item = None


class PhotoDownloadRenderedTests(unittest.TestCase):
    def test_every_draft_shows_native_images_for_android_long_press(self):
        expected = expected_photos()
        page = DownloadPage(get('vinted/index.html').decode())
        self.assertEqual(len(page.photo_images), sum(map(len, expected.values())))
        self.assertEqual(len(page.previews), len(page.photo_images))
        for slug, photos in expected.items():
            with self.subTest(item=slug):
                images = [(anchor, image) for owner, anchor, image in page.photo_images if owner == slug]
                self.assertEqual([image['src'] for _, image in images], ['/for-sale' + p for p in photos])
                for anchor, image in images:
                    self.assertIsNotNone(anchor, 'Photo must open the original image without a ZIP')
                    self.assertEqual(anchor['href'], image['src'])
                    self.assertNotIn('download', anchor, 'Opening full size must not force a download')
                    self.assertTrue(image.get('alt'))
                    self.assertEqual(image.get('loading'), 'lazy')
                    for attrs in (anchor, image):
                        self.assertNotIn('oncontextmenu', attrs)
                        self.assertNotIn('ontouchstart', attrs)
                        self.assertNotIn('onclick', attrs)
                    self.assertNotEqual(image.get('draggable'), 'false')
                singles = [attrs for owner, attrs in page.downloads if owner == slug and 'data-photo-file' in attrs]
                self.assertEqual([a['href'] for a in singles], ['/for-sale' + p for p in photos])
        text = ' '.join(' '.join(page.text).split()).lower()
        for instruction in ('android', 'touch and hold', 'download photo', 'no zip needed'):
            self.assertIn(instruction, text)

    def test_every_vinted_item_has_its_own_zip_and_individual_photo_downloads(self):
        expected = expected_photos()
        page = DownloadPage(get('vinted/index.html').decode())
        all_links = [attrs for _, attrs in page.downloads if 'data-all-photos' in attrs]
        self.assertEqual(len(all_links), 1)
        self.assertTrue(zipfile.is_zipfile(io.BytesIO(get(all_links[0]['href'].removeprefix('/for-sale/')))))
        for slug, photos in expected.items():
            with self.subTest(item=slug):
                links = [attrs for owner, attrs in page.downloads if owner == slug]
                archives = [a for a in links if 'data-photo-archive' in a]
                self.assertEqual(len(archives), 1)
                self.assertEqual(archives[0]['download'], slug + '-photos.zip')
                self.assertEqual(archives[0]['href'], '/for-sale/assets/downloads/' + slug + '-photos.zip')
                with zipfile.ZipFile(io.BytesIO(get(archives[0]['href'].removeprefix('/for-sale/')))) as archive:
                    self.assertEqual(len(archive.namelist()), len(photos))
                singles = [a for a in links if 'data-photo-file' in a]
                self.assertEqual([a['href'] for a in singles], ['/for-sale' + p for p in photos])
                self.assertEqual([a['download'] for a in singles], [f'{slug}-{i:02d}' + Path(photo).suffix for i, photo in enumerate(photos, start=1)])
        self.assertIn('unzip', ' '.join(page.text).lower())


if __name__ == '__main__':
    unittest.main(verbosity=2)
