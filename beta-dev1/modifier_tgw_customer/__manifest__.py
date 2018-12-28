{
    'name':"Modifier TGW Customer",
    'summary': """Manage the Customer""",
    'description': 'To explain how to manage the Customer linked to The Gown Warehouse.',
    'author': "HashMicro / Inkal",
    'website':"http://www.hashmicro.com",
    'depends': ['sale','hr','crm','modifier_tgw_contract','account_voucher','project'],
    'data': [
        'security/ir.model.access.csv',
        'views/customer_view.xml',
    ],
    'category': 'Customer',
    'version':'1.0',
    'application': True,
}
