# -*- coding: utf-8 -*-

from odoo import models, fields, api

class category_analytic_account(models.Model):
    _name = 'account.analytic.category'

    name = fields.Char('Name')
    level = fields.Float('Level')
