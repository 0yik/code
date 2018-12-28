# -*- coding: utf-8 -*-
{
    'name': "HR Leave Balance",

    'summary': """
        This Module Add tab in Employee form view that will show you a list of leave and types and balance""",

    'description': """
        Long description of module's purpose
    """,

    'author': "HashMicro / Parikshit Vaghasiya / Vu",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'HashMicro',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'hr',
        'hm_hr_sg_standardization',
    ],

    # always loaded
    'data': [
        'views/hr_employee_balance_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}