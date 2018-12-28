{
    'name': 'Report Field Manager',
    'category': 'report',
    'summary': 'Add and remove fields in the reporting',
    'version': '1.0',
    'author': 'HashMicro / Kunal',
    'website': 'www.hashmicro.com',
    'description': """
Features:
    - There are pre selected fields in every reporting that user can select and create their own report.
    - We need users to be able to select their own fields in this. So in the top right of every reporting, add "add fields".So you can add any fields related to that object to the reporting. 
    - Everytime you add, you will be able to see it in the selection of fields in the pivot table
    - Right under that function, add "remove field", which will remove fields that already exists in the reporting.
    - This feature only shows on Developer Mode.
        """,
    'depends': [
                'web',
    ],
    'data': [
            "views/webclient_templates.xml",
    ],
    'qweb': [
           "static/src/xml/*.xml",
    ],
    'demo': [
        
    ],
    'installable': True,
    'application': True,
}
