# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Devintelle Solutions (<http://devintellecs.com/>).
#
##############################################################################

{
    'name': 'Default Landed Cost',
    'sequence': 1,
    'category': '',
    'summary': 'Allow users to configure default landed cost based on the Products and auto fill landed cost based on Delivery Order Lines.',
    'version': '1.0',
    'description': """
        Allow users to configure default landed cost based on the Products and auto fill landed cost based on Delivery Order Lines.
        """,
    'author': 'Hashmicro/Janbaz Aga',
    'website': 'http://hashmicro.com/',
    'depends': ['stock','stock_landed_costs'],
    'data': [
        'views/product_view.xml',
        'views/stock_landed_cost.xml',
    ],

    "installable": True,
    "application": True,
    "auto_install": False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
