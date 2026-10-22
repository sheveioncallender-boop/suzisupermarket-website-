# Suzi's Supermarket — Odoo 19 Community

Installable website add-on for **Suzi's Supermarket, Valsayn, Trinidad & Tobago**.
Phone: **377-7711** (`tel:+18683777711`).

Based on the agreed Value Seekers scope: branded homepage, photographic banners,
promotional panels, service highlights, live product shelf, category tiles, About
section, newsletter and footer. The supplied Suzi's logo is retained.

## Install with Cloudpepper

1. Add this repository to the Odoo 19 Community instance using branch **main**:
   `https://github.com/sheveioncallender-boop/suzisupermarket-website-.git`.
2. Rebuild/update the instance's code in Cloudpepper.
3. In Odoo, enable developer mode, open **Apps**, and **Update Apps List**.
4. Search **Suzi's Supermarket Website** and install it.
5. Open Website. The homepage is `/suzi-home`; setup makes it the site's homepage.

Technical module: `suzi_supermarket_website`. The repository root is an add-ons
directory; the module folder is one level below it. Dependencies are standard
Odoo Community modules: Website/eCommerce and Newsletter Subscribe Button
(`website_sale`, `website_mass_mailing`, including Email Marketing).

With one website, setup is automatic. With multiple websites, the add-on selects
only websites already branded/named for Suzi's. If no site is identifiable, open
**Website → Configuration → Settings**, select the correct website, and click
**Apply initial Suzi's setup** in the Suzi's Supermarket block. Branding is scoped
to that site; unrelated websites keep their layout and colours.

## Native Odoo behaviour

- Odoo owns the desktop/mobile header, menus, search, account, cart, product
  variants, pricing, stock rules, taxes, payment and checkout.
- The homepage reads up to 12 published, saleable, website-eligible product
  templates in native website sequence. Prices use the current website pricelist,
  currency and fiscal position, including Odoo's displayed discounts.
- Product cards open the native product page so variants and purchase conditions
  are handled by Odoo. No duplicate cart or custom checkout is implemented.
- Login-only catalogue settings apply to both the shop and homepage.
- The native category model supplies up to six root categories. If the catalogue
  has no categories at installation, six starter categories with photographs are
  added. Odoo's public category visibility rules still apply.
- Newsletter signup uses Odoo's `website_mass_mailing` interaction and public
  mailing list. Installing the module does not send emails or campaigns.
- Contact enquiries use the native `/contactus` form and its configured recipient.
  Suzi's phone/location replace Odoo's sample contact text on the contact page.

## Content and shop setup

Use Odoo's **Edit** button to change headings, copy, banners, promotion panels,
links and footer text. The homepage is also listed in Website's pages. The three
banner slides use Odoo's native carousel, with arrows and working indicators;
rotation is manual by default. Editors can change images and carousel options.

Create/import products, set their images and prices, assign eCommerce categories,
and publish them on the website. Product and category data is managed in Odoo,
not by editing the homepage cards. Product images/prices shown in the homepage
are the same records used in the shop. No fictitious product prices, discounts,
opening hours, delivery promises, social links or payment providers are seeded.

Before accepting real orders, configure the instance's company/contact email,
currency, taxes, inventory policies, delivery/pickup options, payment providers
and transactional email as appropriate. This module does not change those
business settings. The newsletter list can be selected in Website Settings and
managed in Email Marketing. No unverified street address is included.

## Updates and uninstall

Rebuild in Cloudpepper, then **Upgrade** the installed module in Odoo.
Initial setup is idempotent. Homepage/footer records are `noupdate` so module
upgrades preserve website-editor changes, custom logo/homepage choices and menus.
Code, styling and inherited compatibility views update normally.

On uninstall, the original homepage/name/logo/favicon are restored only where
they still match this add-on's defaults. Module-created navigation entries and
views are removed by Odoo. Existing products, orders, stock, accounting data,
categories, mailing lists and subscribers are retained. Reinstalling reuses the
existing Suzi's newsletter list.

## Validation

Run `python3 scripts/check_module.py` for offline Python/XML/asset checks.
The GitHub Actions workflow installs this add-on on official **Odoo 19 Community**
with PostgreSQL, exercises native routes, publication isolation, login-only
catalogues, newsletter wiring, setup idempotence and uninstall restoration, then
upgrades and reruns the regressions.

The test suite creates temporary fixture products inside Odoo's rolled-back test
transactions; they are not production demo data. See the repository's Actions tab
for the current run result.

## Assets

Images are bundled locally as WebP; the deployed site has no stock-photo CDN
dependency. See [PHOTO_CREDITS.md](PHOTO_CREDITS.md). The main banner is generated
commercial-style grocery photography. Illustrative photos are not claims about
the actual premises, brands stocked, or product availability.
