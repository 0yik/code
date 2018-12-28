# -*- coding: utf-8 -*-
{
    'name': "Telering Automate PO",

    'summary': """
        Telering Automate PO""",

    'description': """
        This module add the functionality of telering automate PO buffer. 
    """,

    'category': 'Purchase',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['point_of_sale','sale','purchase_request'],

    # always loaded
    'data': [
	'security/ir.model.access.csv',
        'views/telering_automate_view.xml',
	'views/telering_analysis_view.xml',
	'views/pr_settings_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
	 'demo/pr_demo.xml',
    ],
}
