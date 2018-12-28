# -*- coding: utf-8 -*-
{
    'name': 'Recurring Invoice',
    'version': '1.0',
    'category': 'Account',
    'sequence': 18,
    'summary': 'Recurring Invoice.',
    'description': "Allow users to setup Recurring Invoice models to auto create invoices.",
    'website': 'http://www.hashmicro.com',
    'author': 'Hashmicro/Viet',
    'depends': [
        'account'
    ],
    'data': [
        'views/recurring_customer_invoice.xml',
        'views/recurring_vendor_invoice.xml',
        'views/cron_job.xml',
        'views/recurring_invoice_automate.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}