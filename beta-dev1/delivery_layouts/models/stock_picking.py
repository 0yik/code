# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    total_drums = fields.Integer('Total Drums', compute='_get_drums_info')
    total_nett_weight = fields.Float('Total Nett Weight', compute='_get_drums_info')
    total_gross_weight = fields.Float('Total Grss Weight', compute='_get_drums_info')
    origin_id = fields.Many2one('sale.order', string='Source Document', compute='_get_drums_info')
    report_display_number = fields.Char('Name Display', compute='_get_drums_info')

    @api.multi
    def _get_drums_info(self):
        for record in self:
            origin_id = self.env['sale.order'].search([('name','=',record.origin)])
            total_drums, total_nett_weight, total_gross_weight = 0.0, 0.0, 0.0
            for product in record.move_lines:
                total_drums += product.product_qty
                total_nett_weight += product.product_id.nett_weight
                total_gross_weight += product.product_id.gross_weight
            return record.update({
                'total_drums': int(total_drums),
                'total_nett_weight': total_nett_weight,
                'total_gross_weight': total_gross_weight,
                'origin_id': origin_id.id,
                'report_display_number': record.name.split('/')[-1]
            })
