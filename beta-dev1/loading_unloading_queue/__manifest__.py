# -*- coding: utf-8 -*-
{
    "name": "Loading_Unloading_Queue",
    "author": "HashMicro/ GYBITSolutions / Anand",
    "version": "10.0.1.0",
    "website": "www.hashmicro.com",
    "description":"This module is for generating and managing loading and unloading queue.",
    "category": "Stock",
    "depends": ["stock", "sale"],
    "data": [
        'data/ir_sequence_data.xml',
        'report/report_generate_queue_menu.xml',
        'report/report_generate_queue_template.xml',
        'views/generate_queue_view.xml',
        'views/loading_unloading_queue_view.xml',
        'views/loading_queue_templates.xml',
    ],
    'demo': [
    ],
    "installable": True,
    'application': True,
}
