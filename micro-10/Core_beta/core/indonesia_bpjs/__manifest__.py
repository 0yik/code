{
    'name' : 'Indonesia BPJS',
    'version' : '1.0',
    'category': 'Human Resources',
    'author': 'Hashmicro / MPTechnolabs(Chankya)',
    'summary': 'Indonecia BPJS Salary rules.',
    'website': 'www.hashmicro.com',
    'description': ''' 
     Indonesia BPJS Salary rules
     ''',
    'depends' : ['indonesia_hr_employee','indonesia_company', 'province_wage_range','indonesia_income_tax'],
    'data' : [
        'data/salary_rule.xml',
    ],
    'installable': True,
    'application': False,
}
