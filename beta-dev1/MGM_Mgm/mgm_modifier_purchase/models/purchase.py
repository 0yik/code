from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    reference_number = fields.Char('Reference Number', size=30)
    asset_id = fields.Many2one('account.asset.asset', 'Asset')

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    product_code = fields.Char(related='product_id.product_tmpl_id.default_code', string='Product Code')
