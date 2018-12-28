from odoo import api, fields, models
from datetime import datetime

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def get_installment_loan(self, payslip, employee, date_from, date_to=None):
        if date_to is None:
            date_to = datetime.now().strftime('%Y-%m-%d')
        #added paid state and loan_repayment_method condition
        self._cr.execute("SELECT sum(o.principal_amt) from loan_installment_details as o where \
                            o.employee_id=%s \
                            AND o.state != 'paid'\
                            AND o.loan_repayment_method = 'salary'\
                            AND to_char(o.date_from, 'YYYY-MM-DD') >= %s AND to_char(o.date_from, 'YYYY-MM-DD') <= %s ",
                            (employee.id, date_from, date_to))
        res = self._cr.fetchone()
        if payslip.termination_payslip:
            balance = sum([loan.total_amount_due for loan in employee.loan_ids.filtered(lambda loan : loan.state=='disburse')])
            return balance or 0.0
        else:
            
            return res and res[0] or 0.0

