"""Offline repository checks; runtime integration is exercised in Odoo CI."""
import ast
import re
import xml.etree.ElementTree as ET
from pathlib import Path

root = Path(__file__).resolve().parents[1]
module = root / 'suzi_supermarket_website'
manifest = ast.literal_eval((module / '__manifest__.py').read_text())
assert manifest['version'].startswith('19.0.')
assert manifest['installable']
for file in module.rglob('*.py'):
    ast.parse(file.read_text(), filename=str(file))
for file in module.rglob('*.xml'):
    ET.parse(file)
    for asset in re.findall(r'/suzi_supermarket_website/static/[^\s\x22\x27<>]+', file.read_text()):
        assert (root / asset.lstrip('/')).is_file(), (file, asset)
for file in manifest['data']:
    assert (module / file).is_file(), file
for assets in manifest['assets'].values():
    for file in assets:
        assert (root / file).is_file(), file
home = (module / 'views/homepage.xml').read_text()
layout = (module / 'views/layout.xml').read_text()
assert 'tel:+18683777711' in layout
assert '<odoo noupdate="1">' in home
assert 'website.layout' in home
for file in module.rglob('*'):
    if file.is_file() and file.suffix in ('.png', '.webp', '.svg'):
        assert file.stat().st_size > 100, f'Empty or incomplete image: {file}'
    if file.suffix in ('.xml', '.css', '.js', '.py'):
        assert 'value_seekers_website' not in file.read_text(), file
print('PASS: Python, XML, manifest, bundled assets, branding and editor-preservation checks.')
