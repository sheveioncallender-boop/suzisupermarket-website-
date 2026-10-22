from odoo import fields, models, _
from odoo.exceptions import AccessError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    suzi_branding = fields.Boolean(related='website_id.suzi_branding', readonly=False)
    suzi_newsletter_id = fields.Many2one(related='website_id.suzi_newsletter_id', readonly=False)

    def action_suzi_setup(self):
        self.ensure_one()
        if not self.env.user.has_group('website.group_website_designer'):
            raise AccessError(_('Only website designers can apply this setup.'))
        self.website_id.sudo()._suzi_apply_setup()
        return {'type': 'ir.actions.client', 'tag': 'reload'}
