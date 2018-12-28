# -*- encoding: utf-8 -*-
##############################################################################
#    Copyright (c) 2012 - Present Acespritech Solutions Pvt. Ltd. All Rights Reserved
#    Author: <info@acespritech.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of the GNU General Public License is available at:
#    <http://www.gnu.org/licenses/gpl.html>.
#
##############################################################################
{
    'name': 'Assign unique serial number in Point of Sale',
    'version': '1.0',
    'category': 'Point of Sale',
    'author': "Acespritech Solutions Pvt. Ltd.",
    'summary': 'Assign unique serial number to the products from Point of Sale.',
    'description': """
This module is used to assign unique serial number to the products from Point of Sale.
""",
    'price': 170.00, 
    'currency': 'EUR',
    'website': "www.acespritech.com",
    'depends': ['web', 'point_of_sale'],
    'data': [
        'views/pos_serial.xml',
        'views/pos_view.xml',
        'views/stock_view.xml'
    ],
    'demo': [],
    'test': [],
    'qweb': ['static/src/xml/pos.xml'],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: