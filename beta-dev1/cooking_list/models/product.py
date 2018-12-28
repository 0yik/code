from openerp import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    @api.multi
    def getDetails(self, product):
        bom = self.env['mrp.bom'].search([('product_id','=',product.id)])
        res = {}
        if bom:
            res = {
                  'name' : product.name,
                  'qty_to_produce' : product.qty_to_produce,
                  'bom_products' : [line.product_id.name for line in bom.bom_line_ids],
                  'bom_qty' : [(product.qty_to_produce * line.product_qty) for line in bom.bom_line_ids],
                  'bom_uom' : [line.product_uom.name for line in bom.bom_line_ids]
            }
        return [res]