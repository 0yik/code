from odoo import api, fields, models, _

class PosSession(models.Model):
    _inherit = 'pos.config'

    pos_screen_view = fields.Selection([('product_form_view','Product Form View'),('product_list_view','Product List View')],string='POS Screen View',default='product_form_view')