import logging
import werkzeug

from odoo import http, _
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.web.controllers.main import ensure_db, Home
from odoo.http import request

_logger = logging.getLogger(__name__)


from odoo.addons.auth_signup.controllers.main import AuthSignupHome


class Website(Home):

    @http.route('/', type='http', auth="public", website=True)
    def index(self, **kw):
        if not request.session.uid:
            return request.redirect('/web/login')
        else:
            page = 'homepage'
            main_menu = request.env.ref('website.main_menu', raise_if_not_found=False)
            if main_menu:
                first_menu = main_menu.child_id and main_menu.child_id[0]
                if first_menu:
                    if first_menu.url and (not (first_menu.url.startswith(('/page/', '/?', '/#')) or (first_menu.url == '/'))):
                        return request.redirect(first_menu.url)
                    if first_menu.url and first_menu.url.startswith('/page/'):
                        return request.env['ir.http'].reroute(first_menu.url)
            return self.page(page)

class AuthSignupHome(Home):
    
    @http.route('/web/signup', type='http', auth='public', website=True)
    def web_auth_signup(self, *args, **kw):
        if request.httprequest.method == 'POST':
            res = super(AuthSignupHome, self).web_auth_signup(*args, **kw)
            if not res.qcontext.get('error') or res.qcontext.get('error') == "Wrong login/password":
                res.qcontext['error'] = _("Please wait for our Admin to verify your registration. You will receive a notification once approval/rejection is done. Thank You.")
            return res
        return super(AuthSignupHome, self).web_auth_signup(*args, **kw) 
    
    def do_signup(self, qcontext):
        """ Shared helper that creates a res.partner out of a token """
        values = { key: qcontext.get(key) for key in ('login', 'name', 'password','account_number') }
        assert values.values(), "The form was not properly filled in."
        assert values.get('password') == qcontext.get('confirm_password'), "Passwords do not match; please retype them."
        supported_langs = [lang['code'] for lang in request.env['res.lang'].sudo().search_read([], ['code'])]
        if request.lang in supported_langs:
            values['lang'] = request.lang
        self._signup_with_values(qcontext.get('token'), values)
        request.env.cr.commit()
        
    @http.route('/web/reset_password', type='http', auth='public', website=True)
    def web_auth_reset_password(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()

        if not qcontext.get('token') and not qcontext.get('reset_password_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                if qcontext.get('token'):
                    self.do_signup(qcontext)
                    return super(AuthSignupHome, self).web_login(*args, **kw)
                else:
                    login = qcontext.get('login')
                    assert login, "No login provided."
                    _logger.info(
                        "Password reset attempt for <%s> by user <%s> from %s",
                        login, request.env.user.login, request.httprequest.remote_addr)
                    request.env['res.users'].sudo().reset_password(login)
                    qcontext['message'] = _("Password reset email has been sent to your email address")
            except SignupError:
                qcontext['error'] = _("Could not reset your password")
                _logger.exception('error when resetting password')
            except Exception, e:
                qcontext['error'] = e.message or e.name

        return request.render('auth_signup.reset_password', qcontext)  
    
    def _signup_with_values(self, token, values):
        db, login, password = request.env['res.users'].sudo().signup(values, token)
        request.env.cr.commit()     # as authenticate will use its own cursor we need to commit the current transaction
#         uid = request.session.authenticate(db, login, password)
#         if not uid:
#             raise SignupError(_('Authentication Failed.'))

    
       