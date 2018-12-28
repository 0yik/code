# -*- encoding: utf-8 -*-

from odoo import models, fields


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    payment_by=fields.Selection([('giro', 'GIRO'), ('cash', 'CASH')], string="Payment By", help="Select payment value from selection")
