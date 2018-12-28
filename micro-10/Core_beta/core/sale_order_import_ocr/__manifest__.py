# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2017 Serpent Consulting Services Pvt. Ltd.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Import Sale Order OCR',
    'version': '10.1',
    'category': 'Sale',
    'summary': """Import Sales Order Based on Image or PDF.""",
    'author': 'Bharat Chauhan',
    'website': 'www.mptechnolabs.com',
    'depends': [
        'sale', 'account'
    ],
    'data': [
        'wizard/import_sale_order_view.xml',
        'data/res.lang.csv',
        'views/res_lang_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
