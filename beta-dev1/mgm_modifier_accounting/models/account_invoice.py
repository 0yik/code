from odoo import api, fields, models, _

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _compute_so_total_amount(self):
        for record in self:
            so_objs = []
            if record.origin:
                so_objs = self.env['sale.order'].search([('name','=',record.origin)], limit=1)
            for so_obj in so_objs:
                record.invoice_total_amount = so_obj.amount_total

    invoice_total_amount = fields.Monetary(string='Total Invoice',compute='_compute_so_total_amount')

    asset_id = fields.Many2one('account.asset.asset', 'Asset')


AccountInvoice()


class AccountAccount(models.Model):
    _inherit = "account.account"

    remarks = fields.Text('Remarks')