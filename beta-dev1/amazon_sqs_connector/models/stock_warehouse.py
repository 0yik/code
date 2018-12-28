# -*- coding: utf-8 -*-

from odoo import fields, models


class Warehouse(models.Model):
    _inherit = "stock.warehouse"

    code = fields.Char('Short Name', required=True, size=16,
                       help="Short name used to identify your warehouse")
