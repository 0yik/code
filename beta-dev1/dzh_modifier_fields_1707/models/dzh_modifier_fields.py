from odoo import models, api, fields

class dzh_customer(models.Model):
    _inherit = 'dzh.partner.user'

    @api.multi
    def unlink(self):
        unlink_partner_id = self.dzh_partner_id.id
        res = super(dzh_customer, self).unlink()
        partner_users = self.env['dzh.partner.user'].search([('dzh_partner_id','=',unlink_partner_id)],order='serial_number asc')
        if partner_users:
            serial_number_start = 0
            for partner_user in partner_users:
                serial_number_start = serial_number_start + 1
                partner_user.write({'serial_number':serial_number_start})

        return res

    @api.model
    def create(self,vals):
        res = super(dzh_customer, self).create(vals)
        unlink_partner_id = res.dzh_partner_id.id
        partner_users = self.env['dzh.partner.user'].search([('dzh_partner_id', '=', unlink_partner_id)],
                                                            order='serial_number asc')
        if partner_users:
            serial_number_start = 0
            for partner_user in partner_users:
                serial_number_start = serial_number_start + 1
                partner_user.write({'serial_number': serial_number_start})
        return res

    @api.model
    def default_get(self,fields):
        res = super(dzh_customer, self).default_get(fields)
        res.update({
            'dzh_partner_id' : self._context.get('dzh_partner_id')
        })
        return res


