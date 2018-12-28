# -*- coding: utf-8 -*-
{
    'name': "Verifications Windows",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose Last Update 15-12-2017
    """,

    'author': "HashMicro / Arya",
    'website': "www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base','helpdesk','arf_modifier_fields'
    ],

    # always loaded
    'data': [#'wizard/verification_window_view.xml'
             'call_center_view.xml',
             'helpdesk_ticket_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}