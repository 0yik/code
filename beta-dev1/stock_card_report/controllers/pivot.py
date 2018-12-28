# -*- coding: utf-8 -*-

import json
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers import pivot as Pivot


class TableExporterPDF(Pivot.TableExporter):

    @http.route('/web/pivot/export_pdf', type='http', auth="user")
    def export_pdf(self, data, token):
        rows = json.loads(data)
        pdf = request.env['report'].sudo().with_context(rows=rows).get_pdf([1], 'stock_card_report.report_stock_card')
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'), ('Content-Length', len(pdf)),
            ('Content-Disposition', 'attachment; filename=stock_card_pivot.pdf;'),
        ]
        response = request.make_response(pdf, headers=pdfhttpheaders)
        return response
