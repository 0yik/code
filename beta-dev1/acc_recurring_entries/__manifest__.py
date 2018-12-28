# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Account Recurring Entries',
    'version' : '1.1',
    'summary': 'Recurring Entries',
    'sequence': 30,
    'description': """
Account Recurring Entries
=========================
Last Updated 23 Nov 2017
The specific and easy-to-use Invoicing system in Odoo allows you to keep track of your accounting, even when you are not an accountant. It provides an easy way to follow up on your vendors and customers.

    """,
    'category': 'Accounting',
    'website': 'https://www.hashmicro.com',
    'depends' : ['account'],
    'data': [
        'account_recurring_view.xml',
        'wizard/account_subscription_generate_view.xml',
            ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
