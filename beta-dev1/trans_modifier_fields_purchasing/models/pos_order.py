# -*- coding: utf-8 -*-

from odoo import fields, models, api


class POSOrder(models.Model):
    _inherit = 'pos.order'

    is_created_pr = fields.Boolean(string="Is Created PR ?", default=False)
