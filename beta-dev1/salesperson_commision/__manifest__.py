# -*- coding: utf-8 -*-
{
    'name': "Sales Commission",
    'summary': """
        """,
    'description': """
    """,
    'author': "HashMicro / MP Technolabs - Purvi",
    'website': "www.hashmicro.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '1.0',
    # any module necessary for this one to work correctly
    'depends': [
        'sale','hr',
    ],
    # always loaded
    'data': [
        'views/sale_order_view.xml',
        'views/employee_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
}