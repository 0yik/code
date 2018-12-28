# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2017-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Niyas Raphy(<niyas@cybrosys.in>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <https://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'XXI Modifier Printout',
    'summary': """Modifier POS Receipt""",
    'version': '10.0.1.0',
    'description': """Modifier POS Receipt""",
    'author': 'HashMicro/ Quy',
    'website': 'http://www.hashmicro.com',
    'category': 'Point Of Sale',
    'depends': ['base', 'point_of_sale','pos_receipt_logo'],
    'data': ['static/src/xml/pos_receipt_view.xml'],
    'qweb': ['static/src/xml/pos_ticket_view.xml'],
    'images': ['static/src/description/xxi_logo.png'],
    'demo': [],
    'installable': True,
    'auto_install': False,

}
