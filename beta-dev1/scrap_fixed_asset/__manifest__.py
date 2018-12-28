{
    'name': 'Scrap Fixed Assets',
    'category': 'Inventory',
    'summary': 'scrap fixed assets',
    'version': '1.0',
    'description': """
       Scrap fixed assets
        """,
    'author': 'Hashmicro / MP Technolabs - Parikshit Vaghasiya',
    'website': 'www.hashmicro.com',
    'depends': ['stock','purchase','account_asset','account'],
    'data': [
        'views/scrap_view.xml',
    ],
    'qweb': [],
    'installable': True,
    'application': True,
}
