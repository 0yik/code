{
    'name': 'Loan Termination Payslip',
    'description': 'Loan Termination Payslip',
    'category': 'HR',
    'version': '1.0',
    'author': 'HashMicro / MP Technolabs(chankya)',
    'website': 'www.hashmicro.com',
    'depends': ['hr_employee_loan', 'l10n_sg_hr_payroll'],
    'data': [
        'data/hr_salary_rule.xml',
        'views/hr_payslip_view.xml'
    ],
    'application': True,
    'installable': True,
}