
import re
import odoo
import bcrypt
import logging
from odoo import http
from odoo.http import request
from odoo.tools.translate import _
from odoo.exceptions import UserError
from odoo.addons.web.controllers.main import Home
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.base.ir.ir_mail_server import MailDeliveryException


class WebHome(Home):

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        request.uid = request.env.ref('base.public_user').id
        if request.env["ir.config_parameter"].get_param("activate_password_validation") and request.httprequest.method == 'POST':
            if request.env["ir.config_parameter"].get_param("password_change_upon_initial_logon"):
                user = request.env['res.users'].sudo().search([('login', '=', request.params['login'])])
                if user and not user.login_date:
                    try:
                        user.sudo(user.id).check_credentials(request.params['password'])
                        try:
                            request.env['res.users'].sudo().reset_password(user.login)
                        except MailDeliveryException, e:
                            print e.message 
                        request.uid = request.env.ref('base.public_user').id
                        values = request.params.copy()
                        try:
                            values['databases'] = http.db_list()
                        except odoo.exceptions.AccessDenied:
                            values['databases'] = None
                        values.update({
                            'error': _("An email has been sent with credentials to reset your password."),
                            'login_success': False,
                        })
                        return request.render('web.login', values)
                    except odoo.exceptions.AccessDenied:
                        print 'You user has not entered correct password.'
        r = super(WebHome, self).web_login(redirect=redirect, **kw)
        if request.env["ir.config_parameter"].get_param("activate_password_validation"):
            if request.httprequest.method == 'POST':
                user = request.env['res.users'].sudo().search([('login', '=', request.params['login'])])
                if user and user.id != odoo.SUPERUSER_ID:
                    allowed_attempts = int(request.env["ir.config_parameter"].get_param("allowed_login_attempts"))
                    if not r.qcontext.get('login_success'):
                        user.login_attempt = user.login_attempt + 1
                        if (allowed_attempts <= user.login_attempt):
                            try:
                                template = request.env.ref('password_validation_security.mail_template_account_block_maximum_login_attempt').sudo()
                                if not user.email:
                                    raise UserError(_("Cannot send email: user %s has no email address.") % user.name)
                                template.with_context(lang=user.lang).send_mail(user.id, force_send=True, raise_exception=True)
                            except MailDeliveryException, e:
                                print e.message
                            r.qcontext['error'] = _("You have reached the maximum limit of logon attempts. Please contact to administrator.")
                        else:
                            attempt = 'attempts'
                            remaining_attempt = allowed_attempts - user.login_attempt
                            if remaining_attempt == 1:
                                attempt = 'attempt'
                            r.qcontext['error'] = _(str(remaining_attempt) + " more " + attempt + " and your account will be inaccessible.")
                    if 'login_success' not in r.qcontext:
                        if (allowed_attempts <= user.login_attempt):
                            request.uid = request.env.ref('base.public_user').id
                            values = request.params.copy()
                            try:
                                values['databases'] = http.db_list()
                            except odoo.exceptions.AccessDenied:
                                values['databases'] = None
                            values.update({
                                'error': _("You have reached the maximum limit of logon attempts. Please contact to administrator."),
                                'login_success': False,
                            })
                            return request.render('web.login', values)                            
                        user.login_attempt = 0
        return r


class AuthSignupHomeExtended(AuthSignupHome):
        
    @http.route('/web/reset_password', type='http', auth='public', website=True)
    def web_auth_reset_password(self, *args, **kw):
        activate_password_validation = request.env["ir.config_parameter"].get_param("activate_password_validation")
        password_info = """
                1. Password must not contain login ID, email address, initials, first, middle or last name.<br/>
                <br/>
                2. Password must contain:<br/>
                - Special Character (~`!@#$%^&*()_-{}[]\|:;''""?/<>,.)<br/>
                - Uppercase letter (A-Z)<br/>
                - Lowercase letter (a-z)<br/>
                - Digit (0-9)
                """ 
        if activate_password_validation:
            qcontext = self.get_auth_signup_qcontext()
            qcontext['password_info'] = password_info
            if 'error' not in qcontext and request.httprequest.method == 'POST':
                if qcontext.get('token'):
                    user_oldpassword_obj = request.env['user.oldpassword'].sudo()
                    user = request.env['res.users'].sudo().search([('login', '=', qcontext.get('login'))])
                    if user:
                        try:
                            user.sudo(user.id).check_credentials(qcontext.get('password'))
                            qcontext['error'] = _("You can not set existing password as new password. Please re-enter your password.")
                            return request.render('auth_signup.reset_password', qcontext)
                        except odoo.exceptions.AccessDenied:
                            print 'You user has not entered existing password.'
                            
                        error = ""
                        validate_password = False
                        
                        if not validate_password and request.env["ir.config_parameter"].get_param("password_history"):
                            oldpasswords = user_oldpassword_obj.search([('user_id', '=', user.id)], limit=3)
                            for oldpassword in oldpasswords:
                                try:
                                    if bcrypt.checkpw(qcontext.get('password').encode('utf8'), bytes(oldpassword.name)):
                                        error = _("You have used this password in the past.")
                                        validate_password = True
                                        continue
                                except ValueError:
                                    continue
                        if not validate_password and request.env["ir.config_parameter"].get_param("password_complexity"):
                            new_password = qcontext.get('password').lower()
                            login = user.login.lower()
                            email = user.email.lower()
                            first_name = user.name.lower()
                            last_name = ''
                            if ' ' in first_name:
                                list_name = first_name.split()
                                last_name =  (list_name and list_name[1]) or ''
                            initials = []
                            for a in [login, email, first_name, last_name]:
                                if a and a[0] and a[0][0]:
                                    initials.append(a[0][0])
                            if new_password == login or new_password == email or new_password == first_name or new_password == last_name or new_password in initials:
                                error = _("Password should not contain login ID, email address, initials, first, middle or last name")
                                validate_password = True
                        
                        new_password = qcontext.get('password')
                        if not validate_password and request.env["ir.config_parameter"].get_param("password_complexity"):
                            #Special Character validation                    
                            #Check Small Character
                            if not re.findall('[a-z]', new_password):
                                validate_password = True
                            #Check Capital Letter
                            if not re.findall('[A-Z]', new_password):
                                validate_password = True
                            #Check Number
                            if not re.findall('[0-9]', new_password):
                                validate_password = True
                            #Check Special Character
                            if not re.findall('[^A-Za-z0-9]', new_password):
                                validate_password = True
                            if validate_password:
                                error = _("Password must contain Special Character, Uppercase letter, Lowercase letter and Digit")
                                validate_password = True
    
                        if not validate_password and request.env["ir.config_parameter"].get_param("activate_minimum_password_length"): 
                            #Check Minimum Length8
                            if len(new_password) < int(request.env["ir.config_parameter"].get_param("minimum_password_length")):
                                error = _("Password must have minimum 8 Characters.")
                                validate_password = True
                            
                        if validate_password:
                            qcontext['error'] = error 
                            return request.render('auth_signup.reset_password', qcontext)

        r = super(AuthSignupHomeExtended, self).web_auth_reset_password(*args, **kw)
        if activate_password_validation and kw.get('token'):
            r.qcontext['password_info'] = password_info 
        return r
