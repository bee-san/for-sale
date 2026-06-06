---
layout: default
title: For Sale
description: Markdown sale items are grouped by status. Example listings are clearly labeled as drafts.
---

# For Sale

Markdown sale items are grouped by status below. Use the seller's public contact method if you want more details or photos.

{% assign available_items = site.items | where: "status", "available" | sort: "title" %}
{% assign pending_items = site.items | where: "status", "pending" | sort: "title" %}
{% assign sold_items = site.items | where: "status", "sold" | sort: "title" %}

## Available

{% if available_items.size > 0 %}
<div class="item-grid">
  {% for item in available_items %}
    {% include item-card.html item=item %}
  {% endfor %}
</div>
{% else %}
<p>No available items right now.</p>
{% endif %}

{% if pending_items.size > 0 %}
## Pending

<div class="item-grid">
  {% for item in pending_items %}
    {% include item-card.html item=item %}
  {% endfor %}
</div>
{% endif %}

{% if sold_items.size > 0 %}
<details>
  <summary>Sold items</summary>
  <div class="item-grid">
    {% for item in sold_items %}
      {% include item-card.html item=item %}
    {% endfor %}
  </div>
</details>
{% endif %}
