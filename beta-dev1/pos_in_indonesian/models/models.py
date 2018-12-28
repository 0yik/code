# -*- coding: utf-8 -*-
# import odoo
# from odoo import http
# from odoo.addons.web.controllers.main import WebClient
# from odoo.http import request
#
# class WebClientCustom(WebClient):
#
#     @http.route('/web/webclient/translations', type='json', auth="none")
#     def translations(self, mods=None, lang=None):
#         # if lang == 'en_US':
#
#         res = super(WebClientCustom, self).translations(mods, lang)
#
#         for module_key, module_vals in res['modules'].iteritems():
#             for message in module_vals['messages']:
#                 message['id'] = request.env['ir.translation']._debrand(message['id'])
#                 message['string'] = request.env['ir.translation']._debrand(message['string'])
#         return res
