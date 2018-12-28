# -*- coding: utf-8 -*-
{
    'name': "fleet_delivery",

    'summary': """
        Fleet delivery """,

    'description': """
        Allow users to tag the Vehicle in Delivery Order and show a history of Delivery Orders handled by each Vehicle 
    """,

    'author': "HashMicro / Viet",
    'website': "www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','fleet','stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/trips_view.xml',
        'views/views.xml',
    ],
}