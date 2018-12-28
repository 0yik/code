# -*- encoding: utf-8 -*-
{
    "name": "Indonesia Payroll",
    "version": "1.3",
    "depends": ["base", "hr_payroll", "sg_holiday_extended", "hr_timesheet_sheet", "l10n_id"],
    "author": "Hashmicro/Kannan",
    "website": "www.hashmicro.com",
    "category": "Localization",
    "description": """
Indonesia Payroll Salary Rules.
============================

    -Configuration of hr_payroll for Indonesia localization
    -All main contributions rules for Indonesia payslip.
    * New payslip report
    * Employee Contracts
    * Allow to configure Basic / Gross / Net Salary
    * CPF for Employee and Employer salary rules
    * Employee and Employer Contribution Registers
    * Employee PaySlip
    * Allowance / Deduction
    * Integrated with Holiday Management
    * Medical Allowance, Travel Allowance, Child Allowance, ...

    - Payroll Advice and Report
    - Yearly Salary by Head and Yearly Salary by Employee Report
    - IR8A and IR8S esubmission txt file reports
    """,
    'data': [
        'security/group.xml',
        'security/ir.model.access.csv',
        'data/hr_employee_category_data.xml',
        'data/hr_salary_rule_category_data.xml',
        'data/hr_contribution_register_data.xml',
        'views/menu.xml',
        'data/salary_rule.xml',
        'data/hr_rule_input.xml',
        'views/payroll_extended_view.xml',
        'views/hr_contract_view.xml',
        'views/report_payslip.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
