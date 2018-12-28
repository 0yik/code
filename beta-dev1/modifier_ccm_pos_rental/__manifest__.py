# -*- coding: utf-8 -*-
{
    'name': 'Modifier for POS Rental',
    'version': '1.0',
    'summary': 'Modifier for POS Rental',
    'description': """
Modifier POS Rental
================================
    """,
    'author': 'HashMicro/ MPTechnolabs - Dhaval - Anand',
    'website':"http://www.hashmicro.com",
    'category': 'Point of Sale',
    'depends': ['pos_rental', 'sales_term_and_condition', 'modifier_ccm_pos_promotion', 'pos_loyalty'],
    'data': [
        'security/ir.model.access.csv',
        'data/term_and_condition.xml',
        'data/picking_type_and_location.xml',
        'views/account_invoice_views.xml',
        'views/res_parnter_views.xml',
        'views/sales_term_and_condition_view.xml',
        'views/templates.xml',
    ],
    'qweb': [
        'static/src/xml/pos_receipt.xml',
        'static/src/xml/pos_zoom_image.xml',
        'static/src/xml/pos_promotion.xml'
    ],
    'installable': True,
}
