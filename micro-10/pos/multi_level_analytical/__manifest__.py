# -*- coding: utf-8 -*-
{
    'name': 'Multi Level Analytical',
    'version': '1.0',
    'summary': 'Enterprise accounting report with multi level analytical account',
    'description': 'Enterprise accounting report with multi level analytical account',
    'category': 'Accounting & Finance',
    'author': 'Hashmicro / Saravanakumar',
    'website': 'https://www.hashmicro.com',
    'depends': ['base','enterprise_accounting_report', 'purchase', 'account',
                'pos_analytic_by_config', 'hr','so_analytic', 'hr_payroll_account', 'hr_expense', 'project'],
    'data': [
        'security/ir.model.access.csv',
        'views/define.xml',
        'views/partner_view.xml',
        'views/account_res_config.xml',
        'views/stock_view.xml',
        'views/sale_view.xml',
        'views/pos_order_view.xml',
        'views/hr_payroll_view.xml',
        'views/account_invoice_view.xml',
        'views/analytic_level_view.xml',
        'views/purchase_view.xml',
        'views/product_view.xml',

    ],
    'qweb': [
        'static/src/xml/account_report_backend.xml',
    ],
    'installable': True,
    'application': True,
}
