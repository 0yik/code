# -*- coding: utf-8 -*-
{
    'name' : 'HashMicro OTP Email',
    'version' : '1.1',
    'category': 'Email Management',
    'depends' : [
        'base',
        'mail',
    ],
    'author' : 'HashMicro/ MP Technolabs/ Purvi',
    'description': """
Make a link to reference the attachment that sent in email. 
The recipient need to request and key in OTP to acceess attachments.
=========================================================
The workflow is:
    1. send email to clients with the link for the attachments
    2. clients click onto the link
    3. request for token/OTP
    4. send the token/OTP
    5. enter the token/OTP to view and download the attachments- token to last for only 2hours starting from the time clients click on Request, after that it becomes invalid and clients will have to request again
    """,
    'website': 'www.hashmicro.com',
    'data': [
        'security/ir.model.access.csv',
        'views/otp_email_view.xml',
        'views/otp_email_template.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False
}