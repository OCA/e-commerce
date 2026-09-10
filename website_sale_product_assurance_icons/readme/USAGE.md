Go to Website \> Configuration \> eCommerce \> Assurance Icons, create the
benefit items you want to show and set, for each one:

- **Benefit**: the bold text (e.g. '30-day money-back guarantee').
- **Subtitle**: an optional second line (e.g. 'No questions asked').
- **Image**: upload an icon image. When set, it is used as the card icon.
- **Icon**: alternatively, an icon name, used when no image is set:
    - a Font Awesome class shipped with Odoo (e.g. 'fa-truck', 'fa-shield');
    - or a Lucide icon name (e.g. 'shield-check', 'rotate-ccw', 'truck',
      'credit-card') if Lucide is loaded on the website.
- **URL**: an optional link (e.g. '/terms').
- **Website**: leave empty to show the item on every website.

Once at least one item is defined, it replaces the default terms block on the
product page. If no item is defined, the default terms block is kept.
