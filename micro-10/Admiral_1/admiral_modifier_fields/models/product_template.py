from odoo import models, fields, api

class product_template(models.Model):
    _inherit = 'product.template'

    form = fields.Selection([
        ('powder', 'Powder'),
        ('liquiq', 'Liquid'),
        ('solid', 'Solid'),
    ], string='Form', default='powder')

    volatile = fields.Boolean(string='Volatile')

class stock_move_lot(models.Model):
    _inherit = 'stock.move.lots'

    sequence = fields.Integer()


