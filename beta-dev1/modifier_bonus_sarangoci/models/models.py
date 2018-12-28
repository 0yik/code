# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
from dateutil.relativedelta import relativedelta


class bonus_register(models.Model):
    _name = 'bonus.register'
    _order = 'name'

    name = fields.Char('Level')
    period = fields.Integer('Period (in years)')
    rate = fields.Float('Rate')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', _("Level already exists !")),
    ]


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.one
    @api.depends('employee_id', 'date_from', 'date_to')
    def _compute_bonus_amount(self):
        bonus = 0.00
        bonus_register_env = self.env['bonus.register']
        if self.employee_id and self.employee_id.join_date:
            join_date = self.employee_id.join_date and datetime.strptime(self.employee_id.join_date, DEFAULT_SERVER_DATE_FORMAT)
            date_to = self.date_to and datetime.strptime(self.date_to, DEFAULT_SERVER_DATE_FORMAT)
            difference_in_years = join_date and date_to and relativedelta(date_to, join_date).years
            if difference_in_years and difference_in_years >= 0:
                bonus_rate = bonus_register_env.search([('period', '=', difference_in_years)])
                if not bonus_rate:
                    bonus_rates = bonus_register_env.search([])
                    bonus_rate = bonus_rates.sorted()[-1]
                bonus = self.bonus_amount * (bonus_rate.rate or 0.00)
        self.computed_bonus_amount = bonus

    computed_bonus_amount = fields.Float('Bonus', compute=_compute_bonus_amount)