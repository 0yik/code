{
    'name': 'Google Map Locator',
    'category': 'Hidden',
    'summary': '',
    'version': '1.0',
    'description': """
Google Map Locator
========================

        """,
    'author': 'Hashmicro',
    'depends': ['web','account','sale', 'crm','sale_crm'],
    'data': ['views/google_map_locator.xml',
                'views/crm_lead_view.xml'
             ],
    'qweb': ['static/src/xml/google_map_locator.xml'],
    'installable': True,
    'auto_install': False,
}
