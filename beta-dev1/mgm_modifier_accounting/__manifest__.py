{
    'name': 'MGM Modifer Accounting',
    'version': '1.0',
    'summary': 'MGM Modifer Accounting',
    'description': 'It will allows you to Create Total invoice amount of Sale Order',
    'author': 'Hashmicro/Muthulakshmi',
    'website': 'www.hashmicro.com',
    'category': 'Accounts',
    'depends': ['account','account_asset'],
    'data': [
        'views/account_invoice_view.xml',
        'views/account_asset_view.xml',
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
}
