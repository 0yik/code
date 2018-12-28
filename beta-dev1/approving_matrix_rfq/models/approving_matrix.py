# -*- coding: utf-8 -*-

from odoo import models, fields, api

class approving_matrix_line_pr(models.Model):
    _inherit = 'pr.approving.matrix.line'

    purchase_order_id = fields.Many2one('purchase.order', string="Purchase Order")

