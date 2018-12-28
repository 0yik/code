from odoo import models, fields, api
from odoo.tools.translate import _

class product_product(models.Model):
    _inherit = 'product.product'

    def compute_avarage_cost(self):
        inventories = self.env['stock.quant'].search([('product_id', '=', self.id)])
        if(inventories):
            quantity = inventories.mapped('qty')
            inventory_values = inventories.mapped('inventory_value')
            if sum(quantity) == 0:
                return 0.0
            return sum(inventory_values)/float(sum(quantity))
        else:
            return 0.0

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    cost = fields.Float('Cost')

    @api.model
    def create(self, vals):
        pos_line = super(PosOrderLine, self).create(vals)
        def check_bom(bom, qty):
            total = 0.0
            bom_obj = self.env['mrp.bom']
            for line in bom.bom_line_ids:
                inner_bom = bom_obj.search([('product_tmpl_id', '=', line.product_id.product_tmpl_id.id)])
                if not inner_bom:
                    amount = line.product_uom_id._compute_quantity(line.product_qty * qty, line.product_id.uom_id, round=True, rounding_method='UP')
                    total += amount * line.product_id.compute_avarage_cost()
                else:
                    qty = line.product_uom_id._compute_quantity(line.product_qty * qty, line.product_id.uom_id, round=True, rounding_method='UP')
                    total += check_bom(inner_bom, qty)
            return total
        
        bom = self.env['mrp.bom'].search([('product_tmpl_id','=',pos_line.product_id.product_tmpl_id.id)])
        qty = pos_line.qty
        if bom:
            pos_line.cost = check_bom(bom, qty)
        else:
            pos_line.cost = float(qty) * float(pos_line.product_id.standard_price)
        return pos_line


