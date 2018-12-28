from odoo import fields,models,api, _

class landed_cost(models.Model):
    _inherit = 'stock.landed.cost'

    @api.multi
    def button_get_cost_lines(self):

        product_temp = self.env['product.template']

        if self.cost_lines:
            self.cost_lines.unlink()
#         for picking_id in self.picking_ids:
#             if picking_id.pack_operation_product_ids:
#                 for pack_operation_product_id in picking_id.pack_operation_product_ids:
#                     product_temp_id = product_temp.search([('name','=',pack_operation_product_id.product_id.name)])
#                     if product_temp_id.landed_cost_ok and product_temp_id.product_id:
#                         self.write({'cost_lines':[(0,0,{'product_id':product_temp_id.product_id.id,'split_method':product_temp_id.split_method,'price_unit':product_temp_id.product_id.standard_price})]})
        for picking_id in self.picking_ids:
            for pack_operation_product_id in picking_id.pack_operation_product_ids:
                for landed_product in pack_operation_product_id.product_id.product_tmpl_id.product_ids:
                    if landed_product.landed_cost_ok:
                        self.write({'cost_lines':[(0,0,{'product_id':landed_product.id,'split_method':landed_product.split_method,'price_unit':landed_product.standard_price})]})
        
        return True