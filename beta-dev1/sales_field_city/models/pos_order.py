from odoo import api,fields, models

class PosOrder(models.Model):
    _inherit = 'pos.order'
    
    @api.model
    def _get_pos_order_default_city(self):
        branch_id = self.env.user.branch_id or False
        city_id = branch_id and branch_id.city_id and branch_id.city_id.id or False
        return city_id
    
    city_id = fields.Many2one('city.city', 'City',default = _get_pos_order_default_city)