from odoo import models, fields, api
from odoo.tools.translate import _



class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    cost = fields.Float('Cost')

    @api.model
    def create(self, vals):
        pos_line = super(PosOrderLine, self).create(vals)
        total = 0.0
        def check_bom(bom, qty, total):
            bom_obj = self.env['mrp.bom']
            for line in bom.bom_line_ids:
                inner_bom = bom_obj.search([('product_id', '=', line.product_id.id)])
                if not inner_bom:
                    amount = line.product_uom_id._compute_quantity(float(float(line.product_qty) * float(qty)), line.product_id.uom_id, round=True, rounding_method='UP')
                    total = float(total) + (float(amount) * float(line.product_id.standard_price))
                    pos_line.cost = total
                else:
                    qty = line.product_uom_id._compute_quantity(float(float(line.product_qty) * float(qty)), line.product_id.uom_id, round=True, rounding_method='UP')
                    check_bom(inner_bom, qty, total)
            return total
        
        bom = self.env['mrp.bom'].search([('product_id','=',pos_line.product_id.id)])
        qty = pos_line.qty
        if bom:
            final_total = check_bom(bom, qty, total)
        else:
            pos_line.cost = float(qty) * float(pos_line.product_id.standard_price)
        return pos_line
