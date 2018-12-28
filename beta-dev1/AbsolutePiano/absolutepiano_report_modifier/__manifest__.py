{
    'name': 'Absolutepiano Report Modifier',
    'description': 'This module will Modified Report of Delivery, Invoice, Purchase, Quotation reports.',
    'category': 'Report',
    'version': '1.0',
    'author': 'absolutepiano / Janbaz Aga',
    'website': 'www.hashmicro.com',
    'depends': ['sale','purchase','account','delivery'],
    'data': [
        'views/delivery_report.xml',
        'views/quotation_report.xml',
        'views/purchase_order_report.xml',
        'views/invoice_report.xml',
        'views/report.xml',
    ],
    'application': True,
    'installable': True,
}