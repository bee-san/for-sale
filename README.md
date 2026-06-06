# for-sale

A GitHub Pages Jekyll site for Markdown sale listings.

## Editing a sale item

1. Create a new Markdown file in `_items/`, for example `_items/desk-lamp.md`.
2. Add front matter at the top of the file.
3. Write the item description below the front matter in Markdown.

Example:

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
- Keep the copy short and readable.
```

Status values:

- `available` — shown in the Available section
- `pending` — shown in the Pending section
- `sold` — shown in the sold section, collapsed by default and visually muted

If you omit `status`, it defaults to `available`.

## Adding images

- Put image files in `assets/images/`.
- Reference them from the item front matter, for example `image: /assets/images/desk-lamp.jpg`.
- Keep images reasonably sized so the public page stays fast.
- Anything committed to this repo is public if the GitHub Pages site is public.

## Privacy note

Do not commit private phone numbers, email addresses, home addresses, or other personal details unless Bee explicitly wants them public.

## Local preview and build

This repo is set up for local Jekyll validation with the GitHub Pages gem.

```bash
bundle install
bundle exec jekyll serve
bundle exec jekyll build
```

The generated site is written to `_site/`.

## GitHub Pages deployment

Push the `main` branch to GitHub and enable GitHub Pages to build from the root of the `main` branch.

The current `_config.yml` is configured for the project URL path `/for-sale/`, which matches a repository named `for-sale`. If the repository name changes, update `baseurl` accordingly.
