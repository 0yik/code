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
    'name': 'Odoo all import for Sale, Purchase, Invoice, Inventory, Product and Customer.',
    'version': '1.0',
    'sequence': 4,
    'summary': 'Easy to import all odoo data i.e Sale, Purchase, Invoice, Inventory, Product and Customer.',
    'price': 89,
    'currency': 'EUR',
    'category' : 'Extra Tools',
    'description': """

	BrowseInfo developed a new odoo/OpenERP module apps 
	This module use for following easy import.
	Import Stock from CSV and Excel file.
    Import Stock inventory from CSV and Excel file.
	Import inventory adjustment, import stock balance
	Import opening stock balance from CSV and Excel file.
	Import Sale order, Import sales order, Import Purchase order, Import purchases.
	Import sale order line, import purchase order line, Import data, Import files, Import data from third party software
	Import invoice from CSV, Import Bulk invoices easily.Import warehouse data,Import warehouse stock.Import product stock.
	Invoice import from CSV, Invoice line import from CSV, Sale import, purchase import
	Inventory import from CSV, stock import from CSV, Inventory adjustment import, Opening stock import. 
	Import product from CSV, Import customer from CSV, Product Import,Customer import, Odoo CSV bridge,Import CSV brige on Odoo.Import csv data on odoo.All import, easy import, Import odoo data, Import CSV files, Import excel files 
	Import tools Odoo, Import reports, import accounting data, import sales data, import purchase data, import data in odoo, import record, Import inventory.import data on odoo,Import data from Excel, Import data from CSV.Odoo Import Data
    """,
    'author': 'BrowseInfo',
    'website': '',
    'depends': ['base', 'sale', 'account', 'account_accountant', 'purchase', 'stock'],
    'data': [
             "views/account_invoice.xml",
             "views/purchase_invoice.xml",
             "views/sale.xml",
             "views/stock_view.xml",
             "views/product_view.xml",
             "views/partner.xml"
             ],
	'qweb': [
		],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'images':['static/description/Banner.png'],



}
