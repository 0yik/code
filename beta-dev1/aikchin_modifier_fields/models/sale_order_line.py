# -*- coding: utf-8 -*-

from odoo import models, fields, api

class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags', required=True)