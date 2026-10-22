from odoo import http
from odoo.fields import Domain
from odoo.http import request


class SuziWebsite(http.Controller):
    @http.route('/suzi-home', type='http', auth='public', website=True, sitemap=True)
    def home(self, **kwargs):
        website = request.website
        if not website.suzi_branding:
            return request.not_found()
        Product = request.env['product.template']
        Category = request.env['product.public.category']
        can_shop = website.has_ecommerce_access()
        products = Product.search(
            Domain(website.sale_product_domain()) & Domain('is_published', '=', True),
            order='website_sequence, name, id', limit=12,
        ) if can_shop else Product
        categories = Category.search(
            Domain(website.website_domain()) & Domain('parent_id', '=', False),
            order='sequence, name, id', limit=6,
        ) if can_shop else Category
        return request.render('suzi_supermarket_website.homepage', {
            'main_object': request.env.ref('suzi_supermarket_website.homepage_page'),
            'products': products,
            'product_prices': products._get_sales_prices(website) if products else {},
            'categories': categories,
            'can_shop': can_shop,
            'website': website,
        })
