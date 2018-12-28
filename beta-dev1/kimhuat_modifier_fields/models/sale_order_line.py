from odoo import models, api, fields

class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    sor_ref = fields.Char('SOR Ref')
    description = fields.Text('Description')

    @api.onchange('product_id')
    def onchanger_product_id(self):
        for record in self:
            if record.product_id:
                record.description = record.product_id.product_description

class Account_Payment_Inherit(models.Model):
    _inherit = 'account.payment'

    cheque_number = fields.Char(string="Cheque Number")