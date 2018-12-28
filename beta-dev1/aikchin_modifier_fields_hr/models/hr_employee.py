# -*- encoding: utf-8 -*-

from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    salesmen_code = fields.Integer('Salesmen Code')
