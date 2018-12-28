# -*- coding: utf-8 -*-


{
    'name': 'Opencloud Cashflows Reports',
    'version': '1.0',
    'category': 'Accounting',
    'summary': "Get daily cashflows reports, export to diferent formats and filters",
    'description': """

        Get daily cashflows reports, export to diferent formats and filters:

    """,
    'author': 'Opencloud',
    'website': 'http://opencloud.pro',
    'depends': ['account','website'],
    'init_xml': [],
    'update_xml': ["wizard/cashflow_report.xml",
                    "controllers/view_website.xml",
                    "inherit_conta_view.xml",
                    "security/ir.model.access.csv"],
    'data': ['data/account_data.xml'],
    'installable': True,
    'active': False,
    'price': 190.00,
    'currency': 'EUR',
    'live_test_url':'https://demov8.opencloud.pro/cashflows/refresh',
    'images': ['images/imagem_cashflow.png'],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
