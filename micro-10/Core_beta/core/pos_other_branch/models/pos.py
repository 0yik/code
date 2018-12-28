from odoo import api, fields, models

class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def _process_order(self, pos_order):
        order = super(PosOrder, self)._process_order(pos_order)
        if pos_order.get('branch_selection'):
            config_id = int(pos_order.get('branch_selection'))
            pos_config = self.env['pos.config'].sudo().browse(config_id)
            order.location_id = pos_config.stock_location_id.id
        return order

PosOrder()