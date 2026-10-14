# Bee's London clear-out

A small, static GitHub Pages + Jekyll site for personal sale listings.

- **Live site:** https://bee-san.github.io/for-sale/
- **Repository:** https://github.com/bee-san/for-sale
- **Content:** `_items/*.md`
- **Photos:** `assets/images/`

The site has five photographed listings: an LG monitor, Xbox bundle, Digimon bundle, Russell Hobbs coffee maker and Lenovo ThinkPad P51. Prices are provisional GBP estimates. Working condition and complete contents have not been verified. The P51's SSD is included, but its capacity is an unconfirmed estimate. See [pricing evidence and limitations](PRICING.md).

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

Use your own photographs, rotate them upright and resize sensibly. Strip EXIF, especially GPS data, before adding images. Check backgrounds, labels, serial numbers, barcodes and reflections. The public LG label copy has its serial and barcode covered; unredacted originals are not in this repository.

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
