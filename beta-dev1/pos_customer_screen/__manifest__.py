# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

{
    'name': 'POS Customer screen',
    'version': '1.0',
    'category': 'Point of Sale',
    'website': 'http://www.acespritech.com',
    'price': 30,
    'currency': 'EUR',
    'summary': "Allows Seller's to promote there new products and customers can also see there products.",
    'description': "Allows Seller's to promote there new products and customers can also see there products.",
    'author': "Acespritech Solutions Pvt. Ltd.",
    'website': "www.acespritech.com",
    'depends': ['point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_mirror_image.xml',
        'views/pos_mirror_image_template.xml',
        'views/web_widget_color_view.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'images': ['static/description/customer_screen.png'],
    'installable': True,
    'auto_install': False
}
