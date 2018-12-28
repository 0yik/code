# -*- coding: utf-8 -*-
{
    'name': "Leave Attachment",

    'summary': """
        Leave attachment is compulsory for certain leave types""",

    'description': """
        Leave attachment is compulsory for certain leave types
    """,

    'author': "HashMicro/ Krupesh",
    'website': "https://www.hashmicro.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'hr',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'new_leave_status', 'sg_holiday_extended', 'document', ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/views.xml',
          'views/hr_holidays_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
