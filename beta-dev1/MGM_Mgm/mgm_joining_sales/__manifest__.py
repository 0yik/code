{
    'name': 'MGM Joining Sales',
    'author': 'HashMicro / Quy',
    'category': 'Quotation To Sale',
    'description': 'Sale',
    'version': '1.0',
    'depends': ['sale','account', 'mgm_sales_contract'],
    'data': [
        'views/sale_order.xml',
        'static/src/xml/hiden_action.xml',
    ],
    "installable": True,
    "auto_install": False,
}
