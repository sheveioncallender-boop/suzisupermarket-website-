import base64
import hashlib
import json
import logging

from odoo import api, fields, models
from odoo.tools import file_open

_logger = logging.getLogger(__name__)
MODULE = 'suzi_supermarket_website'


def asset(name):
    with file_open(f'{MODULE}/static/src/img/{name}', 'rb') as stream:
        return base64.b64encode(stream.read())


def digest(value):
    return hashlib.sha256(value or b'').hexdigest()


class Website(models.Model):
    _inherit = 'website'

    suzi_branding = fields.Boolean(string="Suzi's branding", copy=False)
    suzi_newsletter_id = fields.Many2one('mailing.list', string="Suzi's newsletter", copy=False)

    @api.model
    def _suzi_setup(self):
        """Apply once to an explicitly selected or unambiguous website."""
        sites = self.search([])
        targets = sites.filtered(lambda site: site.suzi_branding
                                 or site.homepage_url == '/suzi-home'
                                 or 'suzi' in site.name.casefold())
        if not targets and len(sites) == 1:
            targets = sites
        if not targets:
            _logger.warning("Suzi's: choose the intended website in Website Settings and apply Suzi's setup.")
        targets._suzi_apply_setup()

    def _suzi_apply_setup(self):
        Parameters = self.env['ir.config_parameter'].sudo()
        Menu = self.env['website.menu']
        for website in self:
            key = f'{MODULE}.setup.{website.id}'
            if Parameters.get_param(key):
                continue
            logo, favicon = asset('suzi-logo.png'), asset('favicon.png')
            backup = {
                'homepage_url': website.homepage_url or False,
                'name': website.name,
                'logo': (website.logo or b'').decode(),
                'favicon': (website.favicon or b'').decode(),
                'installed_logo_digest': digest(logo),
                'installed_favicon_digest': digest(favicon),
            }
            Parameters.set_param(key, json.dumps(backup))
            website.write({
                'suzi_branding': True, 'name': "Suzi's Supermarket",
                'homepage_url': '/suzi-home', 'logo': logo, 'favicon': favicon,
            })
            if not website.menu_id:
                root = Menu.create({'name': "Suzi's Menu", 'website_id': website.id})
                self._suzi_own_record(root, f'menu_root_{website.id}')
                website.invalidate_recordset(['menu_id'])
            root = website.menu_id
            existing = Menu.search([('website_id', '=', website.id), ('parent_id', '=', root.id)])
            links = (
                ('Home', '/', ('/', '/suzi-home')),
                ('Shop', '/shop', ('/shop',)),
                ('Categories', '/suzi-home#sz-categories', ()),
                ('Promotions', '/suzi-home#sz-promotions', ()),
                ('About Us', '/suzi-home#sz-about', ()),
                ('Contact', '/contactus', ('/contactus',)),
            )
            for index, (name, url, aliases) in enumerate(links, start=1):
                if not existing.filtered(lambda item: item.url in (aliases or (url,))
                                         or item.name.casefold() == name.casefold()):
                    record = Menu.create({'name': name, 'url': url, 'sequence': index * 10,
                                          'website_id': website.id, 'parent_id': root.id})
                    self._suzi_own_record(record, f'menu_{website.id}_{index}')

            # Seed merchandising categories only on a new catalogue. Existing
            # categories, products, taxes, currency and company data are untouched.
            Category = self.env['product.public.category']
            if not Category.search_count(website.website_domain()):
                for sequence, (name, photo) in enumerate((
                    ('Fresh Produce', 'promo_savings_hd.webp'),
                    ('Groceries & Pantry', 'cat_pantry_hd.webp'),
                    ('Beverages', 'cat_beverages_hd.webp'),
                    ('Snacks & Sweets', 'cat_snacks_hd.webp'),
                    ('Personal Care', 'cat_personal_hd.webp'),
                    ('Household', 'cat_household_hd.webp'),
                ), start=1):
                    Category.create({'name': name, 'sequence': sequence * 10,
                                     'website_id': website.id, 'image_1920': asset(photo)})
            if not website.suzi_newsletter_id:
                newsletter = self.env['mailing.list'].search([
                    ('name', '=', "Suzi's Supermarket — News & Offers"),
                ], limit=1) or self.env['mailing.list'].create({
                    'name': "Suzi's Supermarket — News & Offers", 'is_public': True,
                })
                website.suzi_newsletter_id = newsletter
            # Categories and the mailing list become native business records:
            # keep them on uninstall so products/subscribers are not destroyed.

    @api.model
    def _suzi_own_record(self, record, name):
        self.env['ir.model.data'].create({
            'module': MODULE, 'name': name, 'model': record._name,
            'res_id': record.id, 'noupdate': True,
        })
