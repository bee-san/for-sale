---
layout: default
title: "For sale · London"
description: "An LG 4K monitor, Xbox 360 bundle, Digimon collectibles and a Russell Hobbs coffee maker. Personal sale listings in London, with estimated GBP prices."
---
{% assign available_items = site.items | where: "status", "available" | sort: "order" %}
{% assign pending_items = site.items | where: "status", "pending" | sort: "order" %}
{% assign sold_items = site.items | where: "status", "sold" | sort: "order" %}

<section class="sale-intro" aria-labelledby="intro-title">
  <p class="eyebrow">A personal clear-out · London</p>
  <h1 id="intro-title">Bee's London<br>clear-out<span class="accent-dot">.</span></h1>
  <p class="sale-intro__copy">Desk gear, Japanese games, Digimon and coffee. A few things looking for a new home.</p>
  <div class="sale-intro__facts"><span>Collection by arrangement</span><span>Prices in GBP</span><span>Offers welcome</span></div>
</section>

<aside class="sale-note" aria-label="Price and condition note"><strong>Estimated prices, not fixed quotes.</strong> These listings are based on the photos. Working condition and complete contents still need confirming. Please check the item notes and ask before agreeing a purchase.</aside>

<div class="section-heading"><h2>Available</h2><span>{{ available_items.size }} listings</span></div>
{% if available_items.size > 0 %}
<div class="item-grid">
{% for item in available_items %}{% include item-card.html item=item %}{% endfor %}
</div>
{% else %}<p>No available items right now.</p>{% endif %}

{% if pending_items.size > 0 %}
<h2>Pending</h2>
<div class="item-grid">{% for item in pending_items %}{% include item-card.html item=item %}{% endfor %}</div>
{% endif %}
{% if sold_items.size > 0 %}
<details class="sold-items"><summary>Sold items ({{ sold_items.size }})</summary><div class="item-grid item-grid--sold">{% for item in sold_items %}{% include item-card.html item=item %}{% endfor %}</div></details>
{% endif %}

<section class="how-to-buy" id="how-to-buy" aria-labelledby="buy-title">
  <p class="eyebrow">Interested in something?</p>
  <h2 id="buy-title">Have a look. Ask a question.</h2>
  <p>Open a listing for its photos, description and estimated price. If you already know Bee, message her where you found this link. Otherwise, use the listing's GitHub enquiry button (a GitHub account is required).</p>
  <p>Collection is in London, by arrangement. Confirm the condition, contents and price first. There is no checkout or payment collection on this site.</p>
  <p class="privacy-note">GitHub enquiries are public. Do not post your phone number, email, address or collection details. Arrange those through an existing private contact.</p>
</section>
