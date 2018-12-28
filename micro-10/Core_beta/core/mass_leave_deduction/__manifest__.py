# -*- coding: utf-8 -*-
{
    'name': "Mass Leave Deduction",

    'summary': """
        Similar to “allocate leaves” function but this is mass deduction leave for all employees. For example, company enforced additional 1 day leave for Chinese New Year. This enforced leave would be deducted from Annual Leave of all employees.""",

    'description': """
        Similar to “allocate leaves” function but this is mass deduction leave for all employees. For example, company enforced additional 1 day leave for Chinese New Year. This enforced leave would be deducted from Annual Leave of all employees.
    """,

    'author': "HashMicro/Kannan",
    'website': "https://www.hashmicro.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'hr',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sg_holiday_extended', 'sg_hr_holiday','sg_leave_constraints'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/hr_holidays_status_view.xml',
        'views/hr_holidays_view.xml',
        'wizard/mass_leave_deduction_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
