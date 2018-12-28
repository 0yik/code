# -*- coding: utf-8 -*-

{
    'name': 'Last Sale Price',
    'version': '1.0',
    'category': 'Sales',
    'author': 'Alpesh Valaki (alpeshvalaki@gmail.com)',
    'sequence': 15,
    'summary': 'Create Last Sale Price List And Use it in Next Sale Order',
    'license' : "OPL-1",
    'price': 2.99,
    'currency': 'EUR',
    'description': """ 
        1. Create Sale Order 
        2. Confirm and Done (Locked) Sale Order.
        3. After Sale Order Locked, Price of sale order line's product added in Sale Price List.
        4. Goto Menu : Sales -> Sales -> Products and switch to "Last Sale Price List" Tab. to see sale price list
        5. when next time you add same product in sale order  last sale price automatically added.
    """,
    'website': 'http://sorrysemicolon.com',
    'depends': ['product', 'sale'],
    'data': [
            'views/product_inherit.xml'
        
            ],
    
    'installable': True,
    'auto_install': False,
    'application': True,
}
