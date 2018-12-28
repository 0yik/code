# -*- encoding: utf-8 -*-
from odoo import fields, models


class HrLeaveConfigSettings(models.TransientModel):
    _inherit = 'hr.leave.config.settings'
    #    _inherit = 'res.config.settings'

    module_sg_allocate_leave = fields.Boolean(string='Leave Allocation for Employee',
                                              help="This allows you to create bulk leave allocation for selected employee's for selected leave types by wizard")
    module_sg_leave_constraints = fields.Boolean(string='Leave Constraints',
                                                 help="This will helps to add constraints for leave.")
    module_sg_leave_extended = fields.Boolean(string="Leave Allocation using Interval functionality",
                                              help="This will help to allocate leave using interval unit functionality")
    module_sg_expire_leave = fields.Boolean(string="Expire carry forward allocated leave using leave expire scheduler.",
                                            help="This will help to expire carry forward allocated leave using scheduler.")

HrLeaveConfigSettings()

class HrExpenseConfigSettings(models.TransientModel):
    _inherit = 'hr.expense.config.settings'

    module_sg_expense_maxcap = fields.Boolean(string='Manage Expense Reimbursement Maximum limit per Employee',
                                              help="This help to add expense product and it's maximum amount limits configurations in employee's contract, which use in expense claim by user")
    module_sg_expense_payroll = fields.Boolean(string='Include Expense reimbursement amount in payslips',
                                               help="This help you to to calculate expenses auto calculation")

HrExpenseConfigSettings()

class hr_payroll_configuration(models.TransientModel):
    _inherit = 'hr.payroll.config.settings'

    module_sg_bank_reconcile = fields.Boolean(string='Manage Bank Reconcilation and Bank Statements',
                                              help="This help to Reconcile bank statement")
    module_sg_dbs_giro = fields.Boolean(string='Generate DBS GIRO file for Employee salary payments',
                                        help="This help to generate Dbs giro file for salary payment upload to bank's site.")
    module_sg_nric_verification = fields.Boolean(string='NRIC Number Validation',
                                                 help="This help to validate employee identification number for NRIC employee ID Type.")
    module_sg_cimb_report = fields.Boolean('Allow to generate CIMB Bank text file report',
                                           help="""This will help to generate CIMB Bank text file report.""")
    module_sg_ocbc_report = fields.Boolean('Allow to generate OCBC Bank text file report',
                                           help="""This will help to generate OCBC Bank text file report.""")
    module_sg_appendix8a_report = fields.Boolean('Allow to generate APPENDIX8A report from IRAS',
                                                 help="""This will help to generate APPENDIX8A income-tax report.""")

hr_payroll_configuration()

class hr_employee_configuration(models.TransientModel):
    _name = 'hr.employee.config.settings'
    _inherit = 'res.config.settings'

    module_sg_document_expiry = fields.Boolean(string="Manage Expiry Document Details With Report",
                                               help="This help to send mail for document expiry with report")

hr_employee_configuration()