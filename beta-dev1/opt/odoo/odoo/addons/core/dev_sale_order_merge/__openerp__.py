# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Devintelle Solutions (<http://devintellecs.com/>).
#
##############################################################################

{
    'name': 'Merge Sale Orders',
    'sequence': 1,
    'category': 'Sale',
    'summary': 'Apps will help you to merge two or many sale orders into one Sale orders.',
    'version': '1.0',
    'description': """
        Apps will help you to merge two or many sale orders into one Sale orders.
        """,
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'http://devintellecs.com/',
    'images': ['images/main_screenshot.png'],
    'depends': ['sale','stock_account'],
    'data': [
        'wizard/sale_order_group_view.xml',
        'views/sale_order.xml',
    ],
    
    "installable": True,
    "application": True,
    "auto_install": False,
    'price':25.0,
    'currency':'EUR', 
    'live_test_url':'https://youtu.be/qCAdwXsdgyo',   
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
