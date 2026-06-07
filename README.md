# for-sale

A tiny GitHub Pages + Jekyll site for selling personal items from Markdown files.

- **Live site:** https://bee-san.github.io/for-sale/
- **GitHub repo:** https://github.com/bee-san/for-sale
- **Listings live in:** `_items/*.md`
- **Photos live in:** `assets/images/`

This is a simple public listing/catalog site. It does **not** include a cart, payments, buyer accounts, or private inventory.

## Run locally

Prerequisites:

- Ruby + Bundler
- Git

Install dependencies and start a local preview:

```bash
bundle install
bundle exec jekyll serve --host 127.0.0.1 --port 4000
```

Then open:

```text
http://127.0.0.1:4000/for-sale/
```

Build without serving:

```bash
bundle exec jekyll build
```

The generated site is written to `_site/`.

## Add an item to sell

Create a new Markdown file in `_items/`, for example:

```text
_items/desk-lamp.md
```

Use this template:

```markdown
---
title: "Desk lamp"
price: "15"
currency: "£"
status: available
condition: "Good"
image: /assets/images/desk-lamp.jpg
location_note: "Public pickup note only"
---

A short description of the item.

- Add dimensions, condition notes, and anything useful to a buyer.
- Mention defects clearly.
- Keep the copy short and readable.
```

Tips:

- Use lowercase kebab-case filenames, e.g. `_items/ikea-chair.md`.
- Keep `price` in quotes so values like `10 ono`, `Free`, or `25 each` work.
- If you do not have a photo yet, leave `image:` blank or omit it.
- Replace `_items/example-item.md` once real listings are added.

## Add item photos

1. Put image files in `assets/images/`.
2. Reference them from the item front matter:

```yaml
image: /assets/images/desk-lamp.jpg
```

Keep images reasonably sized so the public page stays fast.

## Mark an item pending or sold

Edit the item's Markdown front matter:

```yaml
status: pending
```

or:

```yaml
status: sold
```

Status behavior:

- `available` — shown in the Available section.
- `pending` — shown in the Pending section.
- `sold` — shown in the Sold section, collapsed by default and visually muted.

If you omit `status`, it defaults to `available`.

## Publish changes

After editing items/photos:

```bash
git status --short
git add _items assets/images README.md
git commit -m "content: update sale listings"
git push
```

GitHub Pages is configured to deploy from the root of the `main` branch. After pushing, GitHub will rebuild the site automatically.

## Selling workflow

1. Add one Markdown file per item in `_items/`.
2. Add an image in `assets/images/` if you have one.
3. Set `status: available` and choose a public-safe `location_note`.
4. Push the change to GitHub.
5. Share the live item/site link with buyers.
6. When someone asks to buy it, change `status` to `pending`.
7. After it is gone, change `status` to `sold`.

## Privacy note

This site is public. Do not commit private phone numbers, email addresses, home addresses, exact pickup addresses, secrets, or private photos unless you explicitly want them public.

## GitHub Pages configuration

The current `_config.yml` is configured for the project URL path `/for-sale/`, matching this repo name. If the repository name changes, update `baseurl` in `_config.yml` accordingly.
