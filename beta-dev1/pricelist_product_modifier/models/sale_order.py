from odoo import api, fields, models, tools, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('pricelist_id')
    def onchange_pricelist(self):
        if self.pricelist_id:
            for line in self.order_line:
                line.price_unit = self.pricelist_id.price_get(line.product_id.id, line.product_uom_qty, self.partner_id.id)[self.pricelist_id.id]
