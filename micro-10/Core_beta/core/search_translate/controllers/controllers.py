# -*- coding: utf-8 -*-
from odoo import http

# class SearchTranslate(http.Controller):
#     @http.route('/search_translate/search_translate/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/search_translate/search_translate/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('search_translate.listing', {
#             'root': '/search_translate/search_translate',
#             'objects': http.request.env['search_translate.search_translate'].search([]),
#         })

#     @http.route('/search_translate/search_translate/objects/<model("search_translate.search_translate"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('search_translate.object', {
#             'object': obj
#         })