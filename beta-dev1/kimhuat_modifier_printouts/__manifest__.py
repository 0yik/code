# -*- coding: utf-8 -*-
{
    'name': "kimhuat_modifier_printouts",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        kimhuat printouts, delivery order, purchase order, quatation order, invoice tax
    """,

    'author': "Luc",
    'website': "vieterp.net",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    'image':['static/src/image/kimhuat_footer_1.jpg',
             'static/src/image/kimhuat_header_1.jpg',
             'static/src/image/kimhuat_header.jpg',
             'static/src/image/kimhuat_footer.jpg',],
    # always loaded
    'data': [
        'report/delivery_order_templates.xml',
        'report/purchase_order_templates.xml',
        'report/quotation_order_templates.xml',
        'report/tax_invoice_templates.xml',
        'report/quotation_order_option_templates.xml',
        'report/sale_order_templates.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
