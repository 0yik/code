# -*- coding: utf-8 -*-

from odoo import models, fields, api
import string, random
class Users(models.Model):
    _inherit = 'res.users'

    @api.model
    def create(self, vals):
        user = super(Users, self).create(vals)

        def gennerate_random_string(size=6, chars=string.ascii_uppercase + string.digits):
            return ''.join(random.choice(chars) for _ in range(size))

        pattern = string.ascii_uppercase  + string.ascii_lowercase + string.digits+ '!"#$%&()*+,-./:;?@[]^_`{|}~'
        password = gennerate_random_string(12, pattern)
        user.write({ 'password': password})
        self.send_password_email(user, password)
        print password
        return user

    def send_password_email(self, user, password):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = base_url + '/web/login'
        email_from = user.company_id.email or 'Administrator <admin@example.com>'
        email_to = user.email
        subject = 'An account has been created from your email'
        message = """
            <html>
                <head>
                    Dear %s,
                </head>
                <body>
                    An account has been created with this email from our system %s with:
                     Username : %s
                     Password : %s
                     Click here to login (<a href="%s" target="_blank">Clickable link</a>)<br/><br/>
    
                    <strong>Thank you</strong>
                </body>
            <html>""" % (user.name, user.company_id and user.company_id.name, user.login, password, url)

        vals = {
            'state': 'outgoing',
            'subject': subject,
            'body_html': '<pre>%s</pre>' % message,
            'email_to': email_to,
            'email_from': email_from,
        }
        if vals:
            email = self.env['mail.mail'].create(vals)
            email.send()

    @api.multi
    def write(self, values):
        res = super(Users, self).write(values)
        return res
