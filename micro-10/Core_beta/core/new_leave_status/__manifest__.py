{
    'name': 'New Leave Status',
    'description': 'Update the leave request status to “New” when user click “create” button.',
    'category': 'HR',
    'version': '1.0',
    'author': 'HashMicro / MP Technolabs(chankya)',
    'website': 'www.hashmicro.com',
    'depends': ['hr_holidays'],
    'data': [
        'views/hr_holidays_view.xml'
    ],
    'application': True,
    'installable': True,
}