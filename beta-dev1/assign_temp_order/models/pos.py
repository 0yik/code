from openerp import api, fields, models, _


class pos_config(models.Model):
    _inherit = "pos.config"

    screen_type = fields.Selection(selection_add=[
        ('e_menu', 'E-Menu'),
    ],  string='Session Type', default='waiter')

    is_auto_assign_order = fields.Boolean(string="Auto assign order", default=False)