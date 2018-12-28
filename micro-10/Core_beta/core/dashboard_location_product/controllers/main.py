# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import fields, http
from odoo.exceptions import AccessError
from odoo.http import request
from odoo import release

class WebSettingsDashboard(http.Controller):

    @http.route('/dashboard_location_product/data', type='json', auth='user')
    def dashboard_location_product_data(self, **kw):
        location_product_1 = request.env['ir.model.data'].xmlid_to_object("dashboard_location_product.stock_location_loc1")
        location_product_2 = request.env['ir.model.data'].xmlid_to_object("dashboard_location_product.stock_location_loc2")
        location_product_3 = request.env['ir.model.data'].xmlid_to_object("dashboard_location_product.stock_location_loc3")
        location_product_4 = request.env['ir.model.data'].xmlid_to_object("dashboard_location_product.stock_location_loc4")
        location_product_5 = request.env['ir.model.data'].xmlid_to_object("dashboard_location_product.stock_location_loc5")
        location_product_6 = request.env['ir.model.data'].xmlid_to_object("dashboard_location_product.stock_location_loc6")
        location_product_7 = request.env['ir.model.data'].xmlid_to_object("dashboard_location_product.stock_location_loc7")
        location_product_8 = request.env['ir.model.data'].xmlid_to_object("dashboard_location_product.stock_location_loc8")
        return {
            'location_product_1': {'id': location_product_1.id, 'name': location_product_1.name},
            'location_product_2': {'id': location_product_2.id, 'name': location_product_2.name},
            'location_product_3': {'id': location_product_3.id, 'name': location_product_3.name},
            'location_product_4': {'id': location_product_4.id, 'name': location_product_4.name},
            'location_product_5': {'id': location_product_5.id, 'name': location_product_5.name},
            'location_product_6': {'id': location_product_6.id, 'name': location_product_6.name},
            'location_product_7': {'id': location_product_7.id, 'name': location_product_7.name},
            'location_product_8': {'id': location_product_8.id, 'name': location_product_8.name},
        }
