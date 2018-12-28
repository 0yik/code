{
    'name': 'mitsuyoshi_forecast_analysis',
    'category': 'sale,purchase',
    'summary': 'Create Pivot table for Sales blanket order',
    'version': '1.0',
    'description': """
        mitsuyoshi_forecast_analysis
        """,
    'author': 'Hashmicro / Duy',
    'website': 'www.hashmicro.com',
    'depends': ['so_blanket_order'],
    'data': [
        'views/sale_order_report_view.xml',
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
}
