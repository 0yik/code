# -*- coding: utf-8 -*-

from odoo import models, fields, api

class purchase_request_line(models.Model):
    _inherit = 'purchase.request.line'

    cost_element_id = fields.Many2one('project.cost_element', string="Cost Element")
