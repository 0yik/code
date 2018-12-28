# -*- coding: utf-8 -*-
{
    'name' : 'Fund Request_b2b',
    'version' : '1.0',
    'category': 'Sales',
    'author': 'HashMicro / MP technolabs / Punit Chaudhary',
    'description': """New Module for fund transfer
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['account','so_blanket_order'],
    'data': [
        'data/ir_sequence_data.xml',
        'views/fund_request_view.xml',
        'views/fund_transfer_view.xml',
        'views/fund_relization_view.xml',
        'views/fund_configuration_view.xml',
        'wizard/journal_adjstment_view.xml',
        'wizard/relization_journal_adjstment_view.xml',
    ],
    'demo': [

    ],
    'qweb': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
