# -*- coding: utf-8 -*-
from odoo import http

# class ModifierBonusSarangoci(http.Controller):
#     @http.route('/modifier_bonus_sarangoci/modifier_bonus_sarangoci/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/modifier_bonus_sarangoci/modifier_bonus_sarangoci/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('modifier_bonus_sarangoci.listing', {
#             'root': '/modifier_bonus_sarangoci/modifier_bonus_sarangoci',
#             'objects': http.request.env['modifier_bonus_sarangoci.modifier_bonus_sarangoci'].search([]),
#         })

#     @http.route('/modifier_bonus_sarangoci/modifier_bonus_sarangoci/objects/<model("modifier_bonus_sarangoci.modifier_bonus_sarangoci"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('modifier_bonus_sarangoci.object', {
#             'object': obj
#         })