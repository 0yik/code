from odoo import api, fields, models, tools, _

class PosOrder(models.Model):
    _inherit = "pos.order"

    delivery_address_id = fields.Many2one('delivery.address', 'Delivery Address')

    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        res.update({'delivery_address_id': ui_order.get('delivery_address_id')})
        return res