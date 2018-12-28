from openerp import api, fields, models, _

class pos_config(models.Model):

    _inherit = "pos.config"

    floor_ids = fields.Many2many('restaurant.floor', 'pos_config_restaurant_floor_rel', 'pos_config_id', 'floor_id', string="Floors")

class restaurant_table(models.Model):

    _inherit = "restaurant.table"

    floor_id = fields.Many2one('restaurant.floor', 'Floor')

