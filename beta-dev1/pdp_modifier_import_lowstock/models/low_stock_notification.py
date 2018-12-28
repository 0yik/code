from odoo import models, api, _, fields

class low_stock_notification(models.Model):
    _inherit = 'low.stock.notification'
    
    @api.multi
    def import_product_wizard(self):
        ir_model_data = self.env['ir.model.data']
        try:
            compose_form_id = ir_model_data.get_object_reference('pdp_modifier_import_lowstock', 'view_import_product_with_qty_form')[1]
        except ValueError:
            compose_form_id = False
        res = {
            'type': 'ir.actions.act_window',
            'name': 'Import Product with Qty',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'import.product.with.qty.csv.xls.file',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': {'default_name': self.id}
        }
        return res   
