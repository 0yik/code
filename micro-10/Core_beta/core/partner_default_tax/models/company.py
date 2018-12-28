# -*- coding: utf-8 -*-
from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    default_tax_ids = fields.Many2many('account.tax', string='Default Tax')

ResCompany()