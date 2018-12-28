# -*- coding: utf-8 -*-

from odoo import models, fields, api

class approving_matrix_line_pr(models.Model):
    _inherit = 'pr.approving.matrix.line'

    @api.model
    def check_amount(self, amount):
        if self.min_amount <= amount:
            return True
        return False