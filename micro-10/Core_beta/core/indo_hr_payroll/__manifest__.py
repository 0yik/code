# -*- encoding: utf-8 -*-
{
    "name": "Indonesia Payroll",
    "version": "1.3",
    "depends": ["sg_cpf_extended", "l10n_id", "indonesia_bpjs"],
    "author": "Hashmicro/ Kannan / MPTechnolans(Chankya)",
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
        'data/hr_salary_rule_category_data.xml',
        'data/salary_rule.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
