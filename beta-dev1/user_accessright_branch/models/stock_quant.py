# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Quant(models.Model):
    _inherit = 'stock.quant'

    @api.multi
    @api.depends('product_id')
    def _get_branch_ids(self):
        '''Method to compute branches'''
        for rec in self:
            rec.branch_ids = [branch_id.id
                            for branch_id in rec.product_id.branch_ids]
        return True

    branch_ids = fields.Many2many('res.branch', string="Branch", compute='_get_branch_ids', store=True)

Quant()
