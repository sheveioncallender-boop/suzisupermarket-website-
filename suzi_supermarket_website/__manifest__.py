{
    'name': "Suzi's Supermarket Website",
    'version': '19.0.1.0.0',
    'category': 'Website/Theme',
    'summary': "Suzi's Valsayn branding with native Odoo navigation and eCommerce",
    'author': 'Spxcorp Limited',
    'license': 'LGPL-3',
    'depends': ['website_sale', 'website_mass_mailing'],
    'data': [
        'views/settings.xml',
        'views/layout.xml',
        'views/homepage.xml',
        'views/footer.xml',
        'data/setup.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'suzi_supermarket_website/static/src/css/suzi.css',
            'suzi_supermarket_website/static/src/js/carousels.js',
        ],
    },
    'uninstall_hook': 'uninstall_hook',
    'application': True,
    'installable': True,
}
