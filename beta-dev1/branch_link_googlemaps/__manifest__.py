# -*- coding: utf-8 -*-
{
    'name': "branch_link_googlemaps",

    'summary': """
        Link master branch to google maps""",

    'description': """
        Link master branch to google maps
    """,

    'author': "HashMicro/ Sang",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'branch', 'sarangoci_modifier_branch', 'sales_field_city'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/branch_views.xml',
        'views/branch_templates.xml',
    ],
}