{
    'name' : 'Account Cost Analytic',
    'version' : '1.0',
    'summary': 'Set Cost Expences feature in Analytic account',
    'description': """
    """,
    'category': 'Accounting',
    'website': 'https://www.odoo.com/page/accounting',
    'author': 'HashMicro / Nikunj',
    'depends' : ['stable_account_analytic_analysis','purchase'],
    'data': [
             'views/account_analytic.xml',
    ],
    'installable': True,
    'auto_install': False,
}
