{
    'name': 'mitsuyoshi_modifier_access_right',
    'category': 'sale,purchase',
    'summary': 'Create Access Right for Mitsuyoshi',
    'version': '1.0',
    'description': """
        Create Access Right for Mitsuyoshi
        """,
    'author': 'Hashmicro / Duy',
    'website': 'www.hashmicro.com',
    'depends': ['sale','account','so_blanket_order','product','stock','mitsuyoshi_forecast_analysis','sales_team'],
    'data': [
        'views/res_groups.xml',
        'security/ir.model.access.csv',
        'views/so_forecast.xml',
        'views/do.xml',
        'views/product.xml',
        'views/so.xml',
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
}
