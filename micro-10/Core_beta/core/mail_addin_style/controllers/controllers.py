# -*- coding: utf-8 -*-
from odoo import http

# class MailAddinStyle(http.Controller):
#     @http.route('/mail_addin_style/mail_addin_style/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mail_addin_style/mail_addin_style/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mail_addin_style.listing', {
#             'root': '/mail_addin_style/mail_addin_style',
#             'objects': http.request.env['mail_addin_style.mail_addin_style'].search([]),
#         })

#     @http.route('/mail_addin_style/mail_addin_style/objects/<model("mail_addin_style.mail_addin_style"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mail_addin_style.object', {
#             'object': obj
#         })