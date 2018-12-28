from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    workorder_invoice_policy = fields.Selection( [('order', 'Ordered quantities'),
         ('workorder', 'Workorder completed quantities'),
        ], string='Invoicing Policy',
        default='order')
