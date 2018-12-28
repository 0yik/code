# -*- coding: utf-8 -*-

from odoo import models, fields, api

class account_analytic_line(models.Model):
    _inherit = 'account.analytic.line'

    time_in = fields.Float('Time In', default=9)
    time_out = fields.Float('Time Out', default=18)