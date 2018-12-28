# -*- coding: utf-8 -*-

from odoo import fields, models, api


class POSOrder(models.Model):
    _inherit = 'pos.order'

    is_created_po = fields.Boolean(string="Is Created PO ?", default=False)
