from openerp import api, fields, models, _


class pos_config(models.Model):
    _inherit = "pos.config"

    screen_type = fields.Selection([
        ('waiter', 'Waiter'),
        ('kitchen', 'Kitchen'),
        ('bar', 'Bar'),
    ],  string='Session Type', default='waiter')
    categ_ids = fields.Many2many('pos.category', string='POS Categories',help='Categories for Kitchen/Bar can see at screen')
