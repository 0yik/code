# -*- coding: utf-8 -*-

{
    'name': 'Warehouse User Management',
    'version': '1.0',
    'category': 'Inventory',
    'summary' : 'Warehouse User Management',
    'description': """
Warehouse User Management
=========================
* This App is useful for companies having multiple warehouses and multiple users managing each warehouse.
* This App allows you to set default warehouse for every users so that the user can only view that warehouse related records.
* This App allow you to configure who can access a warehouse in day or in specific datetime.
* Also have the feature to recurrently schedule a user to a warehouse.
* Only the admin have the permission to configure the warehouse users.
""",
    'author': 'Steigend IT Solutions',
    'website': 'www.steigendit.com',
    'images': [],
    'depends': ['stock','calendar','purchase'],
    'data': [
        'security/stock_security.xml',
        'security/ir.model.access.csv',
        'data/scheduler.xml',
        'views/stock_view.xml',
        'views/users_view.xml',
    ],
    
    'auto_install': False,
    'application':True,
    'currency': 'EUR',
    'price': '20.0',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
