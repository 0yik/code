from openerp import api, fields, models, _


class pos_config(models.Model):
    _inherit = "pos.config"

    screen_type = fields.Selection([
        ('waiter', 'Waiter'),
        ('kitchen', 'Kitchen'),
    ],  string='Session Type', default='waiter')
    categ_ids = fields.Many2many('pos.category', string='POS Categories',help='Categories for Kitchen/Bar can see at screen')
    play_sound = fields.Boolean('Play a sound', help='On kitchen/bar screen, if you need have ring tone when have some requests from waiters, you can check to this field')

