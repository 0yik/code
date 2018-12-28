
from odoo import api, fields, models, tools, _

# Fixed: The branch will be taken from its config

class PosSession(models.Model):
    _inherit = 'pos.session'

    @api.model
    def create(self, values):
        self = super(PosSession, self).create(values)
        self.branch_id = self.config_id.branch_id.id
        return self

class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        res['branch_id'] = ui_order.get('pos_session_id') and self.env['pos.session'].browse(ui_order.get('pos_session_id')).branch_id.id or False 
        return res
        