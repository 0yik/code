# -*- coding: utf-8 -*-
{
    'name': "dzh_revenue_breakdown_by_country",

    'summary': """
        DZH REPORT""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Luc Vieterp",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','report','dzh_modifier_fields'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/revenue_breakdown_by_country_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}