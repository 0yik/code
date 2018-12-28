# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
    'name': 'Mass Mailing Campaigns',
    'category': 'Design, send and track emails',
    'version': '1.02',
    'description': """
        Extension to Mass Mailing Module
    """,
    'author': 'HashMicro / Janeesh',
    'website': 'www.hashmicro.com',
    'depends': ['mass_mailing', 'website_mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/scheduler_data.xml',
        'views/snippets.xml',
        'views/link_tracker_view.xml',
        'wizard/create_mass_mailing_view.xml',
        'wizard/mass_mailing_preview_view.xml',
        'views/mass_mailing_view.xml',
        'views/mass_mailing_report_view.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
