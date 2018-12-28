# -*- coding: utf-8 -*-
{
    'name': "Past Dated Leave Allowed",

    'summary': """
        Leave Allow for past date.
        """,

    'description': """
        Create a new module to configure number of days that employee can submit past dated leave for specific leave type.
    """,

    'author': "Hashmicro/ Krupesh",
    'website': "https://www.hashmicro.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'HR',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sg_holiday_extended'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/views.xml',
          'views/hr_holidays_view.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
}
