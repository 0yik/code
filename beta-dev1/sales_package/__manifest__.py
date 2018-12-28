{
    'name':"Sales Package",
    'summary': """To explain how to manage the Packages.""",
    'description': 'To explain how to manage the Packages.',
    'author': "HashMicro / Inkal",
    'website':"http://www.hashmicro.com",
    'depends': ['project_milestone_template','product','sales_term_and_condition','account','product_booking','purchase', 'modifier_tgw_contract'],
    'data': [
        'security/ir.model.access.csv',
        'views/sales_product_package_view.xml',
    ],
    'category': '',
    'version':'1.0',
    'application': True,
}
