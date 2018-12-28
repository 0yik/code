# -*- coding: utf-8 -*-
{
    'name': " DZH custom printout",

    'summary': """
        Modifies the Invoice Printout
        """,

    'description': """
        1. Create Invoice format according to client’s printout 
            a. Company Registry to be mapped to GST Registration No. 
            b. The rest are straightforward, please map accordingly
    """,

    'author': "Hashmicro / Kunal",
    'website': "http://www.hashmicro.com",
    'category': 'Hashmicro',
    'version': '1.0',
    'depends': ['account','company_bank_details'],
    'data': [
        #'security/ir.model.access.csv',
        'views/account_report.xml',
        'reports/invoice_report.xml',
    ],
}
