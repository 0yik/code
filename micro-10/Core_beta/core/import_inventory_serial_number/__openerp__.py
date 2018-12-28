# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 BrowseInfo(<http://www.browseinfo.in>).
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
    'name': 'import stock with Serial number/Lot number',
    'version': '1.0',
    'sequence': 4,
    'summary': 'This module helps to import serial number with stock inventory using csv or excel file',
    "price": 45,
    "currency": 'EUR',
    'category' : 'Warehouse',
    'description': """
	BrowseInfo developed a new odoo/OpenERP module apps.
	This module is useful for import inventory with serial number from Excel and CSV file .
        Its also usefull for import opening stock balance with serial number from XLS or CSV file.
	-Import Stock from CSV and Excel file.
        -Import Stock inventory from CSV and Excel file.
	-Import inventory adjustment, import stock balance
	-Import opening stock balance from CSV and Excel file.
	-Inventory import from CSV, stock import from CSV, Inventory adjustment import, Opening stock import. Import warehouse stock, Import product stock.Manage Inventory, import inventory with lot number, import inventory with serial number, import inventory adjustment with serial number, import inventory adjustment with lot number. import inventory data, import stock data, import opening stock with lot number, import lot number, import serial number. 
    """,
    'author': 'BrowseInfo',
    'website': '',
    'depends': ['base','stock'],
    'data': ["stock_view.xml"],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    "images":["static/description/Banner.png"],
}
