# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

{
    "name" : "Accounting Sales vs Cash Report",
    'summary' : "This report will show last 90 days record how much you sale in cash and credit.",
    "version" : "1.0",
    "description": """
        This report will show last 90 days record how much you sale in cash and credit.
    """,
    'author' : 'Acespritech Solutions Pvt. Ltd.',
    'category' : 'Accounting',
    'website' : 'http://www.acespritech.com',
    'price': 15,
    'currency': 'EUR',
    'images': ['static/description/main_screenshot.png'],
    "depends" : ['base', 'account', 'account_accountant'],
    "data" : [
        'views/sale_vs_cash.xml',
    ],
    "auto_install": False,
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: