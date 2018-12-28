from odoo import fields,models,api,_

class account_invoice(models.Model):

    _inherit = 'account.invoice'

    @api.multi
    def _get_invoice_shipping(self):
        self.ensure_one()

        stock_picking = self.env['stock.picking']

        picking_ids = stock_picking.search(['|',('name','=',self.name),('origin','=',self.origin)])

        res = []
        for picking_id in picking_ids:
            res.append(picking_id.min_date)
        try:
            return res[-1]
        except:
            return False

