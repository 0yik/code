from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AssetProductSelection(models.TransientModel):
    _name= 'asset.product.selection'

    @api.model
    def default_get(self, fields):
        res = super(AssetProductSelection, self).default_get(fields)

        if self._context.get('active_ids', False) and self._context.get('active_model', False) == 'account.asset.asset':
            asset_br = self.env['account.asset.asset'].browse(self._context.get('active_ids'))
            if not asset_br.invoice_id:
                raise ValidationError(_("Please select any one vendor bill before process the asset."))
            res['invoice_id'] = asset_br.invoice_id.id
            purchase_search = self.env['purchase.order'].search([('name', '=', asset_br.invoice_id.origin)], limit=1)
            res['purchase_id'] = purchase_search.id
            line_vals = []
            for line in purchase_search.order_line:
                if line.is_capital and line.remaining_asset_qty:
                    line_vals.append((0, 0, {
                        'product_id': line.product_id.id,
                        'product_code': line.product_code,
                        'purchase_line_id': line.id,
                        'quantity': line.remaining_asset_qty,
                        'purchase_id': asset_br.invoice_id.purchase_id.id,
                        'unit_price' : line.price_unit
                    }))
            if not line_vals:
                raise ValidationError(_("There is no lines available to proceed."))
            res['purchase_line']= line_vals
        return res

    invoice_id = fields.Many2one('account.invoice', 'Selected Vendor Bill', readonly=True)
    purchase_id = fields.Many2one('purchase.order', 'Related Purchase Order', readonly=True)
    purchase_line = fields.One2many('asset.purchase.line', 'master_id', 'Purchase Line')

    def action_select_product(self):
        asset_br = self.env['account.asset.asset'].browse(self._context.get('active_ids'))
        has_selected_products = any(self.purchase_line.filtered(lambda line: line.is_selected == True))
        if not has_selected_products:
            raise ValidationError(_("Select any one product before process the asset."))
        for line in self.purchase_line:
            if line.is_selected:
               asset_br.name = line.product_id.name
               asset_br.code = line.product_code
               asset_br.value = line.unit_price
               asset_br.is_asset_proceeded = True
               line.purchase_line_id.remaining_asset_qty -= 1
               break


class AssetPurchaseLine(models.TransientModel):
    _name= 'asset.purchase.line'

    master_id = fields.Many2one('asset.product.selection', 'Master Record', readonly=True)
    product_id = fields.Many2one('product.product', 'Product Name', readonly=True)
    purchase_line_id = fields.Many2one('purchase.order.line', 'Purchase Order Line', readonly=True)
    product_code = fields.Char('Product Code', readonly=True)
    quantity = fields.Float('Qty', readonly=True)
    unit_price = fields.Float('Unit Price', readonly=True)
    is_selected = fields.Boolean('Select')