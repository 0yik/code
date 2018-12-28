# -*- coding: utf-8 -*-
{
    'name': "Zones & Postal Code Configuration",

    'summary': """
        Zones and postal code management""",

    'description': """
    """,

    'author': "HILTI/Nitin",
    'website': "http://www.hilti.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Zone and Postal',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'sales_team'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/zone_views.xml',
    ],
    # only loaded in demonstration mode
}
