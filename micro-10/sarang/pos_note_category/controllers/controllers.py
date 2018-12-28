# -*- coding: utf-8 -*-
from odoo import http

# class PosNoteCategory(http.Controller):
#     @http.route('/pos_note_category/pos_note_category/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_note_category/pos_note_category/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_note_category.listing', {
#             'root': '/pos_note_category/pos_note_category',
#             'objects': http.request.env['pos_note_category.pos_note_category'].search([]),
#         })

#     @http.route('/pos_note_category/pos_note_category/objects/<model("pos_note_category.pos_note_category"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_note_category.object', {
#             'object': obj
#         })