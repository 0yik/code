{
    'name':"TGW Modifier Booking Contract",
    'summary': """TGW Modifier Booking Contract """,
    'description': 'product_booking_view',
    'author': "HashMicro / Inkal",
    'website':"http://www.hashmicro.com",
    'depends': ['product_booking','product_booking_contract'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_booking_view.xml',
    ],
    'category': '',
    'version':'1.0',
    'application': True,
}
