from odoo import models, fields, api, _, SUPERUSER_ID


class ResUsers(models.Model):
    _inherit = 'res.users'

    pin_number = fields.Integer(string="PIN Number")

    _sql_constraints = [
        ('unique_pin', 'unique (pin_number)', 'The PIN NUmber must be unique!')
    ]
    
    @api.model
    def compare_pin_number(self, pin_number):
        group_pos_manager_id = self.env.ref('point_of_sale.group_pos_manager')
        user_ids = self.search([('groups_id', 'in', group_pos_manager_id.id)])
        all_pins = [user.pin_number for user in user_ids]
        try:
            pin_number = int(pin_number)
        except Exception:
            return False
        if pin_number in all_pins:
            return True
        return False

class RestaurantFloor(models.Model):
    _inherit = 'restaurant.floor'

    pos_config_ids = fields.Many2many('pos.config','config_id','flor_id', string='Point of Sale')

