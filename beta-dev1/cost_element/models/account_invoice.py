# -*- coding: utf-8 -*-

from odoo import models, fields, api

class account_invoice_line(models.Model):
    _inherit = 'account.invoice.line'

    cost_element_id = fields.Many2one('project.cost_element', string="Cost Element")
