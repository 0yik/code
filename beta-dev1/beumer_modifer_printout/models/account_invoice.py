from odoo import models, fields, api
#
class account_invoice(models.Model):
    _inherit = 'account.invoice'

    # @api.multi
    # def update_bank_id(self):
    #     partner_bank_id = self.env['res.partner.bank'].search([('currency_id', '=', self.currency_id.id)])
    #     self.write({'partner_bank_id':partner_bank_id.id})

    partner_bank_id1     = fields.Many2one('res.partner.bank','Bank Account')