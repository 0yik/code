# -*- coding: utf-8 -*-
import hashlib
import json
from random import randint

from odoo import models, fields, api
from odoo.tools.float_utils import float_compare
from odoo.http import request


class mrp_workorder(models.Model):
    _inherit = 'mrp.workorder'

    @api.multi
    def action_go_scan(self):
        ctx = {}
        ctx['order_name'] = self[0].name
        ctx['data'] = []
        # if self.production_id and self.production_id.bom_id and self.production_id.bom_id.bom_line_ids:
        if self.active_move_lot_ids:
            # recipe_line = self[0].recipe_id.recipe_line.sorted(key=lambda r: r['seq'])
            for line in self.active_move_lot_ids:
                production_lot = self.env['stock.production.lot'].search([('product_id', '=', line.product_id.id)],limit=1)
                ctx['data'].append({
                    'product_name': line.product_id.name or '/',
                    'product_id': line.product_id.id or False,
                    # 'product_qty': line.product_qty or '0',
                    'product_uom': line.product_id.uom_id.name or '',
                    'product_barcode': line.product_id.barcode or '/',
                    'quantity':line.quantity,
                    # 'lot' : production_lot.name if production_lot else '',
                    'quantity_done' : line.quantity_done,
                    'end' : False,
                    'sequence': line.sequence,
                })
            if not ctx['data'] or ctx['data'] == []:
                return
            # ctx['data'][-1].update({'end': True})
            else:
                ctx['data'] = sorted(ctx['data'], key=lambda line: line.get('sequence'))
            return {
                'type': 'ir.actions.client',
                'name': 'Barcode Weighing InterFace',
                'tag': 'barcode_weighing_widget.main',
                'context': ctx,
            }

    @api.model
    def compare_weight(self,workorder_id, product_id, weight):
        check = False
        check_pass = False
        workorder = self.search([('id','=', workorder_id)])
        product = self.env['product.product'].search([('id','=',product_id)])
        if workorder:
            mrp_production = workorder.production_id
            if mrp_production:
                raw_materials = self.env['stock.move'].search([('product_id','=', product_id),('raw_material_production_id', '=', mrp_production.id)])
                if raw_materials:
                    weight_require = raw_materials[0].product_uom_qty
                    if product and product.product_tmpl_id and product.product_tmpl_id.tolerance:
                        tolerance = product.product_tmpl_id.tolerance
                        weight_under = weight_require - (weight_require * tolerance) / 100
                        weight_over  = weight_require + (weight_require * tolerance) / 100
                        if float_compare(float(weight), weight_under, 3) != -1 and float_compare(float(weight), weight_over, 3) != 1:
                            check = True
                        if float_compare(float(weight), weight_over, 3) == 1:
                            check_pass = True
                    else:
                        if float_compare(float(weight), weight_require, 3) == 0:
                            check = True
                        if float_compare(float(weight), weight_require, 3) == 1:
                            check_pass = True
        return check,check_pass

    @api.model
    def get_weight_require(self, workorder_id, product_id):
        weight = 0
        workorder = self.search([('id', '=', workorder_id)])
        if workorder:
            mrp_production = workorder.production_id
            if mrp_production:
                raw_materials = self.env['stock.move'].search(
                    [('product_id', '=', product_id), ('raw_material_production_id', '=', mrp_production.id)])
                if raw_materials:
                    weight = raw_materials[0].product_uom_qty
        return weight

    @api.model
    def supervisor_bypass(self,password):
        user = self.env['res.users'].search([('id','=',self._uid)])
        user_login = str(request.session.login)
        user_password = str(request.session.password)
        if self.env.user.has_group('admiral_modifier_access_rights.supervisor_group') and user_login == user.login and user_password == str(password):
            return True
        else:
            return False

    @api.model
    def update_weight_done(self,active_id,product_id,weight,lot):
        if active_id and product_id and weight and lot:
            lot_production = self.env['stock.production.lot'].search([('name', '=', lot)])
            work_order = self.browse(active_id)
            if work_order and work_order.active_move_lot_ids:
                for line in work_order.active_move_lot_ids:
                    if line.product_id.id == product_id:
                        line.quantity_done = weight
                        line.lot_id = lot_production






class product_template(models.Model):
    _inherit = 'product.template'

    tolerance = fields.Float("Tolerance(%)")

class product_product(models.Model):
    _inherit = 'product.product'

    tolerance = fields.Float("Tolerance(%)")
