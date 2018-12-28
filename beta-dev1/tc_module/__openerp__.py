# -*- encoding: utf-8 -*-
{
    
    "name" : "TC Module",
    "version" : "1.3",
    "author" : "HashMicro/Vipin",
    "website":'www.hashmicro.com',
        "summary": "Add Terms & Conditions Template ",
    "depends" : ['web','product','sale','purchase','stock', 'account'],
    "init_xml" : [],
    "demo_xml" : [],
    "data" : [
        "sale_custom.xml",
        'views/sale_view.xml',
        'views/purchase_view.xml',
        'views/invoice_view.xml',
        "views/invoice_print.xml",
        "views/sale_print.xml",
        "views/po_order.xml",
        "views/rfq_report.xml",
    ],
    'qweb': [
    ],
    "test" : [
    ],
    "auto_install": False,
    "application": False,
    "installable": True,
}


