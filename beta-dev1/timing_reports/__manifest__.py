# -*- coding: utf-8 -*-
{
    'name': "timing_reports",

    'summary': """
        branch, category, Average Customer Time, Average Cooking time""",

    'description': """
        Modify report
    """,

    'author': "HashMicro / MP Technolabs-Purvi",
    'website': "http://www.hashMicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'complex_kds', 'sales_field_city'],

    # always loaded
    'data': ['views/pos_order_report_view.xml'],
    # only loaded in demonstration mode
    'demo': [],
}