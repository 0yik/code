# -*- coding: utf-8 -*-
from odoo import http, api, SUPERUSER_ID
from odoo.http import request

# class BarcodeWeighingInterface(http.Controller):
#
#     @http.route('/workorders/scan', auth='user')
#     def index(self, **kw):
#         if kw.get('order_id',False):
#             order_obj = request.env['mrp.workorder']
#             order_id = order_obj.browse(int(kw.get('order_id')))
#             ctx = {}
#             ctx['workorder'] = order_id
#         return request.render('barcode_weighing_interface.barcode_weighing', )
