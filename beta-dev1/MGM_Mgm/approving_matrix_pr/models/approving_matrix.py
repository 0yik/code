# -*- coding: utf-8 -*-

from odoo import models, fields, api

class approving_matrix_line_pr(models.Model):
    _inherit = 'pr.approving.matrix.line'

    purchase_request_id = fields.Many2one('purchase.request', string="Purchase Request")
    purchase_request_line_id = fields.Many2one('purchase.request.line', string="Purchase Request Line")

