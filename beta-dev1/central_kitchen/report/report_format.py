# -*- coding: utf-8 -*-

from odoo import models, fields

class report_paperformat(models.Model):
    _inherit = "report.paperformat"
    custom_report = fields.Boolean('Temp Formats', default=False)

report_paperformat()