# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
{
    'name': 'Pos Price List',
    'version': '10.0.0.1',
    'category': 'Point Of Sale',
    'sequence': 6,
    'summary': 'Add Pricelist option in POS Order which will link to customer pricelist',
    'description': 'Add Pricelist option in POS Order which will link to customer pricelist',
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'maintainer': 'Serpent Consulting Services Pvt. Ltd.',
    'website': 'https://www.serpentcs.com',
    'data':[
            'security/ir.model.access.csv',
            'view/templates.xml',
           ],
    'depends': ['sale','point_of_sale', 'pos_options_bar'],
    'qweb': ['static/src/xml/pos_price_list.xml'],
    'installable': True,
    'auto_install':False,
    'application':False,
    'price': 49,
    'currency': 'EUR',
}
