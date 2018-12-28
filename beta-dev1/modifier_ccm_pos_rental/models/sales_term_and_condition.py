# -*- coding: utf-8 -*-

from odoo import models, fields


class SalesTermsCondition(models.Model):
    _inherit = 'sale.tc'

    subject = fields.Char('Subject')
