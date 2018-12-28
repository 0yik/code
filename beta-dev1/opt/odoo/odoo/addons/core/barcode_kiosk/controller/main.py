# -*- coding: utf-8 -*-

from odoo import http
from odoo import models, fields
from odoo.http import request


class BarcodeKiosk(http.Controller):
    @http.route(['/check_badge'], type='json', auth="public", website=True)
    def check_badge_id(self,  badge=None, **kw):
        emp = request.env['hr.employee'].search([('barcode', '=', int(badge))]).ids
        if emp:
            return emp[0]
        return False

    @http.route('/barcode_kiosk/scan_from_main_menu', type='json', auth='user')
    def main_menu(self, barcode, **kw):
        """ Receive a barcode scanned from the main menu and return the appropriate
            action (open an existing / new picking) or warning.
        """
        ret_open_picking = self.try_open_picking(barcode)
        if ret_open_picking:
            return ret_open_picking

        if request.env.user.has_group('stock.group_stock_multi_locations'):
            ret_new_internal_picking = self.try_new_internal_picking(barcode)
            if ret_new_internal_picking:
                return ret_new_internal_picking

        if request.env.user.has_group('stock.group_stock_multi_locations'):
            return {'warning': _('No picking or location corresponding to barcode %(barcode)s') % {'barcode': barcode}}
        else:
            return {'warning': _('No picking corresponding to barcode %(barcode)s') % {'barcode': barcode}}
