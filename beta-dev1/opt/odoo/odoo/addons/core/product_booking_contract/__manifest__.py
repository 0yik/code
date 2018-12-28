{
    'name':"Product Booking Contract",
    'summary': """Manage the Product Booking Contract""",
    'description': 'Product Booking Contract',
    'author': "HashMicro / Inkal",
    'website':"http://www.hashmicro.com",
    'depends': ['product_booking','stable_account_analytic_analysis'],
    'data': [
        'data/ir_sequence_data.xml',
        'security/ir.model.access.csv',
        'views/booking_order_contract_view.xml',
    ],
    'category': 'booking',
    'version':'1.0',
    'application': True,
}
