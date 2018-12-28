# -*- coding: utf-8 -*-
{
    'name': "Inventory Valuation Comparison",
    'description': """
       
    """,
    'author': 'Hashmicro/GYB IT SOLUTIONS-Anand',
    'website': 'www.hashmicro.com',
    'category': 'stock',
    'version': '0.1',
    'depends': ['sale','stock','purchase','product','sales_team',],
    'data': [
        'security/ir.model.access.csv',
        'views/product.xml',
        'report/inventory_valuation_comparison_sql.xml',
    ],
    'qweb':[],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
