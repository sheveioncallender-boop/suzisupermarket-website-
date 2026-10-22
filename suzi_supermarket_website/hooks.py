import json
from .models.website import MODULE, digest


def uninstall_hook(env):
    """Restore only values still set to this add-on's defaults."""
    Parameters = env['ir.config_parameter'].sudo()
    for website in env['website'].search([]):
        key = f'{MODULE}.setup.{website.id}'
        data = Parameters.get_param(key)
        if not data:
            continue
        backup = json.loads(data)
        values = {'suzi_branding': False, 'suzi_newsletter_id': False}
        if website.homepage_url == '/suzi-home':
            values['homepage_url'] = backup['homepage_url']
        if website.name == "Suzi's Supermarket":
            values['name'] = backup['name']
        for field in ('logo', 'favicon'):
            if digest(website[field]) == backup[f'installed_{field}_digest']:
                values[field] = backup[field] or False
        website.write(values)
        Parameters.search([('key', '=', key)]).unlink()
