

from odoo import http, tools, _
from odoo.http import request


class ForgotpwdAppAlert(http.Controller):

    @http.route('/check_and_update_password', type='json', auth="public", website=True)
    def check_and_update_password(self, **post):
        user = request.env['res.users'].sudo().search([('login', '=', post.get('login'))])
        if user.has_group('forgotpwd_app_alert.group_access_to_app_and_system'):
            return {'password_updated': False}
        elif user.has_group('forgotpwd_app_alert.group_access_to_app'):
            token = post.pop('token', None)
            db, login, password = request.env['res.users'].sudo().signup(post, token)
            return {'password_updated': True}
        return {}