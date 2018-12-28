# -*- coding: utf-8 -*-
from odoo import http

# class ImportExportSoLine(http.Controller):
#     @http.route('/import_export_so_line/import_export_so_line/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/import_export_so_line/import_export_so_line/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('import_export_so_line.listing', {
#             'root': '/import_export_so_line/import_export_so_line',
#             'objects': http.request.env['import_export_so_line.import_export_so_line'].search([]),
#         })

#     @http.route('/import_export_so_line/import_export_so_line/objects/<model("import_export_so_line.import_export_so_line"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('import_export_so_line.object', {
#             'object': obj
#         })