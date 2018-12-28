# -*- coding: utf-8 -*-
{
    'name': "Company Bank Details",

    'summary': """
        Add a Bank Details in Partner and Company
        """,

    'description': """
        1. Implement Bank Account Tab Menu in odoo 8 to odoo 10
        2. Same fields in odoo 8 to odoo 10
        3. Add Bank Details in Company
        4. Add Bank Details in Partner
    """,

    'author': "Hashmicro / Kunal",
    'website': "http://www.hashmicro.com",
    'category': 'Bank',
    'version': '1.0',
    'depends': ['base','account','sales_team'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_company_view.xml',
        'views/res_partner_bank_view.xml',
    ],
}
