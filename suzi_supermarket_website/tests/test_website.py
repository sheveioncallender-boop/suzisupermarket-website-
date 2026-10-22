import json

from lxml import html
from odoo.tests import HttpCase, tagged

from ..hooks import uninstall_hook
from ..models.website import MODULE


@tagged('-at_install', 'post_install')
class TestSuziWebsite(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env.ref('website.default_website')
        cls.website.write({'domain': False, 'ecommerce_access': 'everyone', 'suzi_branding': True})
        cls.other_website = cls.env['website'].create({
            'name': 'Unrelated website', 'domain': 'https://unrelated.invalid',
            'company_id': cls.website.company_id.id,
        })
        cls.category = cls.env['product.public.category'].create({
            'name': 'Suzi test groceries', 'website_id': cls.website.id, 'sequence': -10000,
        })
        vals = {'sale_ok': True, 'is_published': True, 'list_price': 23.75,
                'website_sequence': -10000, 'website_id': cls.website.id,
                'public_categ_ids': [(6, 0, cls.category.ids)]}
        cls.product = cls.env['product.template'].create(dict(vals, name='SUZI PUBLIC ITEM'))
        cls.hidden = cls.env['product.template'].create(dict(vals, name='SUZI PRIVATE ITEM', is_published=False))
        cls.foreign = cls.env['product.template'].create(dict(vals, name='SUZI FOREIGN ITEM', website_id=cls.other_website.id))

    def get_page(self, path):
        response = self.url_open(path)
        self.assertEqual(response.status_code, 200, response.text[:500])
        return html.fromstring(response.content)

    def test_homepage_and_native_routes(self):
        page = self.get_page('/suzi-home')
        self.assertEqual(len(page.xpath('//header[@id="top"]')), 1)
        self.assertTrue(page.xpath('//header//a[@href="tel:+18683777711"]'))
        self.assertTrue(page.xpath('//header//*[contains(@class,"my_cart_quantity")]'))
        self.assertTrue(page.xpath('//header//*[@data-bs-target="#top_menu_collapse_mobile"]'))
        stylesheets = page.xpath('//link[@rel="stylesheet"]/@href')
        self.assertTrue(stylesheets)
        bundled_css = ''
        for stylesheet in stylesheets:
            if stylesheet.startswith('/web/assets/'):
                asset = self.url_open(stylesheet)
                self.assertEqual(asset.status_code, 200)
                bundled_css += asset.text
        self.assertIn('.sz-website', bundled_css)
        names = ' '.join(page.xpath('//a[@class="sz-product-name"]/text()'))
        self.assertIn(self.product.name, names)
        self.assertNotIn(self.hidden.name, names)
        self.assertNotIn(self.foreign.name, names)
        expected = '/shop/category/%s' % self.env['ir.http']._slug(self.category)
        self.assertTrue(page.xpath('//a[@href=$href]', href=expected))
        for path in ('/shop', self.product.website_url, expected, '/shop/cart', '/contactus'):
            native = self.get_page(path)
            self.assertEqual(len(native.xpath('//header[@id="top"]')), 1)
        contact = self.get_page('/contactus')
        self.assertTrue(contact.xpath('//form[@id="contactus_form"]'))
        self.assertNotIn('555-555', contact.text_content())
        self.assertNotIn('Fake Buena', contact.text_content())

    def test_login_only_catalogue_not_exposed(self):
        self.website.ecommerce_access = 'logged_in'
        page = self.get_page('/suzi-home')
        self.assertFalse(page.xpath('//article[contains(@class,"sz-product-card")]'))
        self.assertFalse(page.xpath('//a[@class="sz-category"]'))
        self.assertTrue(page.xpath('//a[@href="/web/login?redirect=/shop"]'))

    def test_branding_does_not_apply_when_disabled(self):
        self.website.suzi_branding = False
        self.assertEqual(self.url_open('/suzi-home').status_code, 404)
        page = self.get_page('/shop')
        self.assertNotIn('sz-website', page.xpath('//div[@id="wrapwrap"]')[0].get('class', ''))
        self.assertFalse(page.xpath('//*[contains(@class,"sz-topbar")]'))
        self.assertFalse(page.xpath('//*[contains(@class,"sz-newsletter")]'))

    def test_setup_is_idempotent_and_preserves_edits(self):
        menus = self.env['website.menu'].search([('website_id', '=', self.website.id)])
        categories = self.env['product.public.category'].search([])
        newsletter = self.website.suzi_newsletter_id
        self.website.write({'homepage_url': '/shop', 'name': 'Edited store title'})
        self.website._suzi_apply_setup()
        self.assertEqual(self.website.homepage_url, '/shop')
        self.assertEqual(self.website.name, 'Edited store title')
        self.assertEqual(self.env['website.menu'].search([('website_id', '=', self.website.id)]), menus)
        self.assertEqual(self.env['product.public.category'].search([]), categories)
        self.assertEqual(self.website.suzi_newsletter_id, newsletter)
        for xmlid in ('homepage', 'homepage_page', 'footer'):
            data = self.env['ir.model.data'].search([('module', '=', MODULE), ('name', '=', xmlid)])
            self.assertTrue(data.noupdate)

    def test_native_newsletter_is_configured(self):
        self.assertTrue(self.website.suzi_newsletter_id.is_public)
        page = self.get_page('/suzi-home')
        forms = page.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," js_subscribe ")]')
        self.assertEqual(len(forms), 1)
        self.assertEqual(int(forms[0].get('data-list-id')), self.website.suzi_newsletter_id.id)
        self.assertTrue(forms[0].xpath('.//input[@type="email"]'))

    def test_uninstall_restores_homepage_and_keeps_business_records(self):
        params = self.env['ir.config_parameter'].sudo()
        backup = json.loads(params.get_param(f'{MODULE}.setup.{self.website.id}'))
        newsletter = self.website.suzi_newsletter_id
        self.website.homepage_url = '/suzi-home'
        uninstall_hook(self.env)
        self.assertEqual(self.website.homepage_url, backup['homepage_url'])
        self.assertFalse(self.website.suzi_branding)
        self.assertTrue(newsletter.exists())
        self.assertTrue(self.product.exists())
        self.assertTrue(self.category.exists())
