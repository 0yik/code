
from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    student_type = fields.Selection([('corporate', 'Corporate'), ('individual', 'Individual')], string="Partner Type", default="individual")
    company_address = fields.Text('Company Address')
    fax_no = fields.Char('Fax No')
    uen_no_company_number = fields.Char('UEN No/Company Number')

class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.multi
    def write(self, values):
        self.clear_caches()
        if self.partner_id.student_type == 'corporate' and 'active' in values and values['active']:
            template = self.env.ref('theme_atts.atts_welcome_email')
            template.send_mail(self.id, force_send=True)
        return super(ResUsers, self).write(values)
