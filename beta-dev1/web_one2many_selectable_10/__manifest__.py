# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2016 Shawn
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
    "name": "Multi-selection for one2many fields",
    "version": "1.0",
    "author": "Hashmicro / Quy",
    "website": "https://www.hashmicro.com",
    "summary": "This widget adds the capability for selecting multiple records in one2many fields and calls a python function with the recods as self argument",
    "description": '''
Description
-----------
This widget adds the capability for selecting multiple records in one2many fields and calls a python function with the ids as argument.

e.g. <field name="course_id" widget="one2many_selectable">
        <tree>
            <field name="title" />
        </tree>
    </field>
    ''',
    "category": "Web Enhancements",
    "depends": [
        'web','product'
    ],
    "data": [
        "view/web_assets.xml",
        'view/pricelist_view_form.xml'
    ],
    "qweb":[
        'static/src/xml/widget_view.xml',
    ],
    "auto_install": False,
    "installable": True,
    "application": False,
    "external_dependencies": {
        'python': [],
    },
}
