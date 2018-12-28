# -*- coding: utf-8 -*-

from odoo import models, fields, api

class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    cost_element_id = fields.Many2one('project.cost_element', string="Cost Element")