# -*- coding: utf-8 -*-

from odoo import models, fields, api

class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'

    analytic_distribution_id = fields.Many2one('account.analytic.distribution', string='Analytic Distribution')

    @api.multi
    def create_analytic(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.analytic.distribution',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.analytic_distribution_id.id,
            'target': 'new',
        }
