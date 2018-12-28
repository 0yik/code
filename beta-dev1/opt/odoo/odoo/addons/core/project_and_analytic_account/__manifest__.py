{
    'name': 'Project and Analytic Account',
    'version': '1.0',
    'category': 'Project',
    'summary': 'Budget related fields in Project',
    'description': """
    It will add reference fields named Budget Cost and Spent Cost in project, related with analytic account of project.
    """,
    'author': 'Hashmicro / Nikunj',
    'website': 'https://www.odoo.com/page/project-management',
    'depends': [
        'account_cost_analytic',
    ],
    'data': [
             'views/project.xml',
    ],
    'application': True,
}
