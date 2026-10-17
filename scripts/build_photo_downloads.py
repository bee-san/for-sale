#!/usr/bin/env python3
"""Build deterministic download ZIPs from already-public listing photos only."""
import argparse
import io
import json
from pathlib import Path
import re
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PHOTO_PATTERN = re.compile(r'/assets/images/[A-Za-z0-9._-]+')


def collect_photos(root):
    root = Path(root)
    public = (root / 'assets/images').resolve()
    items = {}
    for item in sorted((root / '_items').glob('*.md')):
        if not re.fullmatch(r'[a-z0-9-]+', item.stem):
            raise ValueError('Unsafe item slug: ' + item.stem)
        photos = list(dict.fromkeys(PHOTO_PATTERN.findall(item.read_text())))
        if not photos:
            raise ValueError('No public photos for ' + item.stem)
        for photo in photos:
            source = (root / photo.lstrip('/')).resolve()
            if not source.is_relative_to(public) or not source.is_file():
                raise ValueError('Photo must be a file inside assets/images: ' + photo)
            if source.suffix.lower() not in ('.jpg', '.jpeg', '.png', '.webp', '.gif'):
                raise ValueError('Unsupported photo type: ' + photo)
        items[item.stem] = photos
    if not items:
        raise ValueError('No listing photos found')
    return items


def archive_bytes(root, entries):
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name, photo in entries:
            data = (root / photo.lstrip('/')).read_bytes()
            if b'Exif\x00\x00' in data:
                raise ValueError('Strip camera metadata before publishing: ' + photo)
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)
    return output.getvalue()


def build_downloads(root=ROOT, check=False):
    root = Path(root)
    items = collect_photos(root)
    all_entries = []
    outputs = {}
    manifest = {'items': {}, 'all_archive': '/assets/downloads/all-listing-photos.zip',
                'item_count': len(items), 'photo_count': sum(map(len, items.values()))}
    for slug, photos in items.items():
        entries = [(f'{index:02d}-' + Path(photo).name, photo)
                   for index, photo in enumerate(photos, start=1)]
        archive_path = '/assets/downloads/' + slug + '-photos.zip'
        outputs[archive_path.lstrip('/')] = archive_bytes(root, entries)
        all_entries.extend((slug + '/' + name, photo) for name, photo in entries)
        manifest['items'][slug] = {'archive': archive_path, 'photos': photos, 'count': len(photos)}
    outputs[manifest['all_archive'].lstrip('/')] = archive_bytes(root, all_entries)
    outputs['_data/photo_downloads.json'] = (json.dumps(manifest, indent=2, sort_keys=True) + '\n').encode()
    stale = [name for name, data in outputs.items()
             if not (root / name).is_file() or (root / name).read_bytes() != data]
    if check:
        if stale:
            print('Photo downloads are missing or stale. Run python3 scripts/build_photo_downloads.py:', file=sys.stderr)
            print('\n'.join(stale), file=sys.stderr)
            return 1
    else:
        for name, data in outputs.items():
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    print(f"{'Verified' if check else 'Built'} {len(items)} item ZIPs and one all-photos ZIP "
          f"from {manifest['photo_count']} public photos")
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Fail if committed bundles differ from current public photos')
    sys.exit(build_downloads(check=parser.parse_args().check))
