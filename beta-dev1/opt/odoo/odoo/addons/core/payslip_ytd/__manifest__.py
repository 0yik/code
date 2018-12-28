# -*- coding: utf-8 -*-
{
    'name': "Payslip Ytd",

    'description': """
        Enhance the function to show Overtime Period.
    """,

    'author': "HashMicro/ MPTechnolabs(Chankya)",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'hr_payroll',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['l10n_sg_hr_payroll', 'salary_bonus_deduction'],

    # always loaded
    'data': [
        'views/hr_payslip_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}