# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2017-Today Sitaram
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
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

{
    'name': 'Product Approval Workflow',
    'version': '0.1',
    'category': 'Sales',
    'summary': 'This module allows you to approve product only by Product manager.',
    "license": "AGPL-3",
    'description': """
        When you create product at that time state is draft after that product manager will approve that product.
        after product approve by product manager it will shown in the quotations and purchase order.
""",
    "price": 19,
    "currency": 'EUR',
    'author': 'Sitaram',
    'depends': ['base','product','sale','purchase'],
    'data': [
             'security/product_security.xml',
            'views/product.xml',
            'views/sale.xml',
            'views/purchase.xml',
    ],
    'installable': True,
    'live_test_url':'https://youtu.be/xiUmvFKfR7o',
    'auto_install': False,
    "images":['static/description/banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
