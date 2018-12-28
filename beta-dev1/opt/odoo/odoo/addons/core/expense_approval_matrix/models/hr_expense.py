# -*- coding: utf-8 -*-
from odoo import fields, models

class product_product(models.Model):
    _inherit = 'product.product'

    product_doa_id = fields.Many2one('expense.approval.matrix', 'Product DOA')

product_product()
