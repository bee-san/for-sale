# Bee's London clear-out

A small, static GitHub Pages + Jekyll site for personal sale listings.

- **Live site:** https://bee-san.github.io/for-sale/
- **Repository:** https://github.com/bee-san/for-sale
- **Content:** `_items/*.md`
- **Photos:** `assets/images/`

The site contains photographed electronics, home items, books and Japanese publications. Prices are provisional GBP estimates. Condition, contents and testing limits are described in each listing. The P51's i7-7820HQ and 32GB RAM are photo-confirmed. An SSD is included; Windows shows 237GB and 447GB volumes, but physical drive specifications remain unconfirmed. See [pricing evidence and limitations](PRICING.md).

## Vinted copy-and-paste page

Open **https://bee-san.github.io/for-sale/vinted/** for a title, description and current GBP asking price for every item. Each field has its own Copy button and a selectable-text fallback when clipboard access is blocked. Nothing is posted to Vinted automatically.

Each item also has a **Download images** ZIP button and individual photo download links; the page has an all-photos ZIP with a folder for each item. Unzip bundles before selecting images in Vinted. Only the already-public, privacy-cleaned photos are included.

After adding or changing listing photos, regenerate the committed bundles and manifest:

```sh
python3 scripts/build_photo_downloads.py
python3 scripts/build_photo_downloads.py --check
```

CI verifies archive contents against the exact current public photo bytes and rejects stale downloads. Do not feed private originals into the generator.

Draft wording and seller-only checks are in `_data/vinted_drafts.json`. Prices are read from `_items/*.md`, so do not put prices in the draft data. `ready`, `check` and `other` control the workspace groups. Known faults and testing uncertainty stay in buyer descriptions; preparation, packing and policy checks stay outside the copied fields. A draft is not a guarantee of Vinted eligibility.

Asking prices were raised modestly from the bargain-clear-out amounts after review. The newly photographed Flesh and Blood playmat is included; repeated photos are not extra stock. Old pricing research below the current summary in `PRICING.md` is historical, not the current asking price.

## Run locally

Use Ruby 3.3, Bundler and Python 3. Modern Ruby is required; macOS's system Ruby 2.6 is not supported by this lockfile. CI uses Ruby 3.3.

```sh
bundle install
bundle exec jekyll serve --host 127.0.0.1 --port 4000
```

Open http://127.0.0.1:4000/for-sale/.

To build and check without serving:

```sh
bundle exec jekyll build
python3 -m unittest discover -s tests -v
```

CI runs the same build and checks. The tests pin the photographed inventory and estimated prices; update `ITEMS` in `tests/test_site.py` when changing it. They also check every linked listing photo for camera EXIF and keep the P51's unconfirmed specifications explicit.

## Add an item to sell

Create `_items/desk-lamp.md` with front matter and a Markdown description:

```yaml
---
title: "Desk lamp"
price: "15"
currency: "£"
estimated: true
order: 5
status: available
category: "Home"
condition: "Used; describe actual condition here."
location_note: "London, by arrangement."
image: /assets/images/desk-lamp.jpg
image_alt: "Describe the actual photo for someone who cannot see it."
summary: "A short description for the listing card."
description: "Short description for link previews and search results."
---
```

Below the front matter, describe the item, what is included, known defects and any uncertainties. Do not describe something as tested, sealed or complete unless it has been checked. Use `estimated: false` only after choosing a firm asking price. Keep `price` quoted. `order` controls card order.

## Add item photos

Use your own photographs, rotate them upright and resize sensibly. Strip EXIF, especially GPS data, before adding images. Check backgrounds, labels, serial numbers, MAC addresses, barcodes and reflections. Public label photos have unique identifiers covered, including the LG, WD hard drive, Kensington dock and Wii U GamePad. Unredacted originals are not in this repository. Duplicate attachments and extra views of the same hardware are not additional units or listings.

Add photos to `assets/images/` and reference them using a path beginning `/assets/images/`. For extra photos inside a description, apply Jekyll's `relative_url` filter so the `/for-sale/` project path is preserved.

## Mark an item pending or sold

Change its front matter:

```yaml
status: pending
```

or `status: sold`. Available items come first, then pending items. Sold listings are collapsed on the homepage, and their detail page no longer offers an enquiry button.

## Enquiries and selling workflow

1. Share the live homepage or an individual listing link.
2. Buyers who know Bee can message her through their existing private contact.
3. Other buyers can use **Enquire on GitHub**, which opens a prefilled issue. They need a GitHub account. The site does not automatically post anything.
4. Confirm availability, operation, accessories and price before agreeing a purchase. Set the item to `pending` when reserved.
5. Arrange contact and collection details privately, not in public issues. Do not post addresses or phone numbers.
6. Mark an item `sold` once it has gone.

This is a catalogue, not a shop checkout. It does not take payments, collect form submissions, hold buyer accounts or add analytics. No private contact details are published.

## Publish changes

```sh
git status --short
git diff --check
git add _items assets/images README.md tests
git commit -m "content: update sale listings"
git push
```

GitHub Pages builds from the root of `main`. Check the **pages build and deployment** and **Verify sale site** workflows after pushing. Open the live site to confirm the update before sharing it.

## Privacy note

Everything committed here is public, including Git history. Never commit private addresses, contact details, credentials or unredacted photos. Deleting a file later does not remove it from history. README, pricing notes and tests are excluded from the generated Pages site but remain public in the repository.

## GitHub Pages configuration

The project base path is `/for-sale/` in `_config.yml`. The `github_repo` field controls the enquiry destination. If renaming or moving the repository, update `url`, `baseurl` and `github_repo` together.
