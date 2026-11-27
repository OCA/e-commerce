## Business Need

E-commerce websites often want to highlight customer feedback not only on individual product pages but also in centralized locations such as landing pages, category pages, or custom marketing sections. 

By default, Odoo reviews are tied to specific products and cannot be easily aggregated or reused elsewhere on the website. 


This module addresses this limitation by introducing a snippet that collects and displays multiple reviews in one place. 

For example:

- A landing page showcasing testimonials from the most popular products. 

- A category introduction page summarizing customer experiences. 

- A homepage section displaying reviews from newly launched products. 


## Approach

The module extends the existing `website_sale` and `website_rating` functionality to provide a configurable snippet. 

The snippet fetches published reviews across selected products and displays them with a configurable limit (default 20, maximum 100). 


## Useful Information

- **Dependencies:** Relies on `website_sale` and `website_rating`. 

- **Compatible modules:** Works well with marketing and promotional website features such as sliders, banners, or call-to-action snippets. 

- **Suggested setups:** Useful in multi-website or multi-company scenarios where aggregated feedback should be highlighted across different contexts. 

