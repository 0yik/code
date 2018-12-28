# -*- encoding: utf-8 -*-
##############################################################################
#
#    Samples module for Odoo Web Login Screen
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#    
#
##############################################################################

import odoo
import odoo.modules.registry
import ast

from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import ensure_db, Home
from odoo.tools.translate import _
import datetime
import pytz


#----------------------------------------------------------
# OpenERP Web web Controllers
#----------------------------------------------------------
class Home(Home):

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        ensure_db()
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return http.redirect_with_hash(redirect)

        if not request.uid:
            request.uid = odoo.SUPERUSER_ID

        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            old_uid = request.uid
            user=request.env["res.users"].sudo().search([("login", "=", request.params['login'])])
            if user.login<>'admin':
                if user.locked==True:
                    values['error'] = _("Sorry you have reach maximum number of attempts. Please contact admin to unlock your account.")
                else:
                    uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
                    if uid is not False:
                        request.params['login_success'] = True
                        if not redirect:
                            redirect = '/web'
                        return http.redirect_with_hash(redirect)
                    request.uid = old_uid
                    no_value=no_value_less=0
                    password = request.env["res.password"].sudo().search([])
                    values['error'] = _("Wrong login/password")
                    if user.no_attempted>=password.lock_after:
                        user.sudo().write({"locked" : True})
                    if user.no_attempted>=password.lock_after:
                        values['error'] = _("Sorry you have reach maximum number of attempts. Please contact admin to unlock your account.")
                    if user.no_attempted<password.lock_after:
                        no_value = user.no_attempted+1
                        no_value_less = password.lock_after-no_value
                        user.sudo().write({"no_attempted" : no_value})
                        if no_value==password.lock_after:
                            user.sudo().write({"locked" : True})
                    if user.no_attempted<password.lock_after:
                        values['error'] = _("You have attempted %s times, you have %s attempts left."%(no_value,no_value_less))
                    if user.no_attempted==password.lock_after:
                        values['error'] = _("Sorry you have reach maximum number of attempts. Please contact admin to unlock your account.")
            else:
                uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
                if uid is not False:
                    request.params['login_success'] = True
                    if not redirect:
                        redirect = '/web'
                    return http.redirect_with_hash(redirect)
                request.uid = old_uid
                no_value=no_value_less=0
                password = request.env["res.password"].sudo().search([])
                values['error'] = _("Wrong login/password")
        return request.render('web.login', values)

