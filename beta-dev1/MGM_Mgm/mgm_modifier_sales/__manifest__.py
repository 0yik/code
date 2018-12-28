{
    'name': 'MGM Modifier Sales',
    'category': 'sale',
    'summary': 'MGM Modifier Sales',
    'version': '1.0',
    'description': """
        MGM Modifier Sales
        """,
    'author': 'Hashmicro / Duy',
    'website': 'www.hashmicro.com',
    'depends': ['sale','sale_discount_total','enterprise_accounting_report','so_blanket_order','modifier_discount_type','product','mgm_sales_contract'],
    'data': [
        'views/template.xml',
        'views/sale_view.xml',
        'views/product_view.xml',
    ],
    'qweb': [
        'static/src/xml/mgm_modifier_sales_team_dashboard.xml',
    ],
    'installable': True,
    'application': True,
}
