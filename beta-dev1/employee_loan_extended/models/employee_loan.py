# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, SUPERUSER_ID
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date, time, timedelta
from odoo.exceptions import Warning, UserError

class EmployeeLoan(models.Model):
    _inherit = "employee.loan.details"
    _description = 'Employee Loan Details'

    flag=fields.Boolean(default=False)

    @api.multi
    def applied_state(self):
        if self.flag:
            self.write({'state':'applied'})
        else:
            raise Warning(_('Please Compute first!!'))

    @api.multi
    def compute_installments(self):
        for loan in self:
            if not len(loan.installment_lines):
                self.create_installments(loan)
                self.flag=True
            elif self._context.get('recompute') and loan.int_payable:
                access_payment = 0.0
                duration_left = 0
                prin_amt_received = 0.0
                total_acc_pay = 0.0
                for install in loan.installment_lines:
                    access_payment += round(install.total - (install.principal_amt + install.interest_amt), 2)
                    if install.state in ('paid', 'approve'):
                        prin_amt_received += round(install.principal_amt, 2)
                        continue
                    duration_left += 1
                total_acc_pay = loan.duration - duration_left
                new_p = round(loan.principal_amount - round(prin_amt_received, 2) - round(access_payment, 2))
                if loan.interest_mode == 'reducing':
                    reducing_val = self.reducing_balance_method(new_p, loan.int_rate, duration_left)
                if loan.interest_mode == 'flat':
                    interest_amt = 0.0
                    principal_amt = new_p / duration_left
                    if loan.int_payable:
                        interest_amt = self.flat_rate_method(new_p, loan.int_rate, duration_left) / duration_left
                    total = principal_amt + interest_amt
                cnt = -1
                for install in loan.installment_lines:
                    cnt += 1
                    if install.state in ('paid', 'approve'):continue
                    if loan.interest_mode == 'reducing':
                        principal_amt = reducing_val[cnt - total_acc_pay]['principal_comp']
                        if loan.int_payable:
                            interest_amt = reducing_val[cnt - total_acc_pay]['interest_comp']
                        total = principal_amt + interest_amt
                    install.write({'principal_amt':principal_amt,
                                 'interest_amt':interest_amt,
                                 'total':total})
            	self.flag=True
            else:
                # this is to reload the values
                loan.write({})
                for install in loan.installment_lines:
                    install.write({})
                self.flag=True
        return True