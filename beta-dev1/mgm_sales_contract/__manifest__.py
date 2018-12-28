{
    'name': 'MGM Sale Contract',
    'author': 'HashMicro / Quy / MP Technolabs(Chankya)/ MP Technolabs - Vatsal',
    'category': 'Sale Contract',
    'description': 'Modification of Sales Requisition',
    'version': '1.0',
    'depends': ['so_blanket_order','account_asset'],
    'data': [
        'data/mail_template_data.xml',
        'views/sequence.xml',
        'views/sales_contract.xml',
        'views/business_unit.xml',
    ],
    "installable": True,
    "auto_install": False,
}