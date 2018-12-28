from odoo import models, api, fields

class res_partner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, vals):
        if vals['customer']:
            vals['customer_id'] = self.env['ir.sequence'].next_by_code('res.partner.company') or ''
        else:
            vals['supplier_id'] = self.env['ir.sequence'].next_by_code('res.partner.supplier') or ''
        return super(res_partner, self).create(vals)
