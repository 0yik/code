{
    'name' : 'Internal Transfer Receipt',
    'version' : '1.0',
    'category': 'Inventory',
    'author': 'Hashmicro / MPTechnolabs(Chankya)',
    'summary': 'Internal Transfer Receipt.',
    'website': 'www.hashmicro.com',
    'description' : ''' 
         Internal Transfer Receipt
     ''',
    'depends' : ['stock'],
    'data' : [
        'data/transfer_sequence.xml',
        'views/internal_transfer.xml',
    ],
    'installable': True,
    'application': False,
}
