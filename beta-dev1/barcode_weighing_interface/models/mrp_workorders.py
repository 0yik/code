# -*- coding: utf-8 -*-

from odoo import models, fields, api


class mrp_workorder(models.Model):
    _inherit = 'mrp.workorder'

    @api.multi
    def action_go_scan(self):
        ctx = {}
        ctx['order_name'] = self[0].name
        ctx['data'] = []
        if self[0].recipe_id.recipe_line and len(self[0].recipe_id.recipe_line) > 0:
            recipe_line = self[0].recipe_id.recipe_line.sorted(key=lambda r: r['seq'])
            for line in recipe_line:
                ctx['data'].append({
                    'product_name': line.product_id.name or '/',
                    'product_id': line.product_id.id or False,
                    'product_qty': line.product_qty or '0',
                    'product_uom': line.product_id.uom_id.name or '',
                    'recipe_line_id': line.id,
                    'product_barcode': line.product_id.barcode or '/',
                    'end' : False,
                })
            if not ctx['data'] or ctx['data'] == []:
                return
            ctx['data'][-1].update({'end': True})
            return {
                'type': 'ir.actions.client',
                'name': 'Barcode Weighing InterFace',
                'tag': 'barcode_weighing_widget.main',
                'context': ctx,
            }