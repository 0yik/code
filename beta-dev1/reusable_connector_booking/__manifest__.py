# -*- coding: utf-8 -*-
{
    'name': "Send Notification to App",

    'summary': """
        Send notification to app which Workorder due in 
        upcoming 24 hrs""",

    'description': """
        Sending reminder to app for workorder
    """,

    'author': "Hashmicro / Krupesh",
    'website': "https://www.hashmicro.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
         'security/ir.model.access.csv',
        # 'views/views.xml',
        # 'views/templates.xml',
        'views/send_notification_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
       # 'demo/demo.xml',
    ],
}
