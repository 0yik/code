{
    'name':"TGW Project Milestone",
    'summary': """Milestone""",
    'description': 'To explain how to manage the Milestones in a Project for TGW.',
    'author': "HashMicro / Inkal",
    'website':"http://www.hashmicro.com",
    'depends': ['project_milestone','modifier_tgw_contract','project_milestone_template'],
    'data': [
        'security/ir.model.access.csv',
        'views/milestone_view.xml',
        'views/email_template_view.xml',
        'views/account_analytic_account_contract_view.xml',
    ],
    'category': '',
    'version':'1.0',
    'application': True,
}
