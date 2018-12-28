# -*- coding: utf-8 -*-
{
    'name': "sales_cancellation_report_reusable",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['product',
                'account','report',],

    # always loaded
    'data': [
        'views/sales_cancel_report_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    "installable": True,
    "auto_install": False,
}