# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class hr_holidays_status(models.Model):
    _inherit = 'hr.holidays.status'

    leave_cashable = fields.Boolean('Leave Cashable')
    max_encash_days = fields.Integer('Max Encash Days')
    calculation_type = fields.Selection([('exact','Exact'),('rounding','Rounding')], default='exact', string='Calculation Type')

    @api.onchange('max_encash_days')
    def onchange_max_encash_days(self):
        warning = {}
        if self.max_encash_days and (self.max_encash_days > 31):
            self.max_encash_days = False
            warning = {'title': 'Value Error', 'message': "Please input 0 to 31 for maximum encashment days allowed."}
        return {'warning': warning}

hr_holidays_status()