# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class hr_holidays(models.Model):
    _inherit = 'hr.holidays'

    payslip_status = fields.Boolean('Reported in last payslips')
    payslip_id = fields.Many2one('hr.payslip', string="Payslip")
