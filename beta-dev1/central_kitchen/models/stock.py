# -*- coding: utf-8 -*-
import base64
from odoo import models, fields, api
from odoo.tools.float_utils import float_compare, float_round

class stock_production_lot(models.Model):
    _inherit = 'stock.production.lot'

    barcode_image = fields.Binary(string='Barcode image',compute='_compute_barcode_image')
    count_for_print = fields.Integer('Count for Print')
    produce_date = fields.Datetime('Produce Date')

    @api.one
    def _compute_barcode_image(self):
        barcode = self.env['report'].barcode(
            'Code128',
            self.name,
            width=300,
            height=50,
            humanreadable=0
        )

        barcode_base64 = base64.b64encode(barcode)
        self.barcode_image = barcode_base64

    @api.model
    def create(self, data):
        # If Name Numer Avaiable
        try:
            if data['name']:
                vals = {'name': data['name'],'product_id': data['product_id'],'count_for_print': data['count_for_print'],'produce_date': data['produce_date']}
                return super(stock_production_lot, self).create(vals)
        except:
            pass

        sequence = self.env['ir.sequence'].search([('code', '=', 'stock.lot.serial')])
        product = self.env['product.product'].search([('id', '=', data['product_id'])])

        if sequence.category.id == product.categ_id.id:
            if sequence.number_next_actual <= sequence.end_no:
                new_id = sequence.get_new_seq(sequence.id)
                seq_vals = {'name': new_id,'product_id': data['product_id'],'count_for_print': data['count_for_print'],'produce_date': data['produce_date']}
                return super(stock_production_lot, self).create(seq_vals)
        return super(stock_production_lot, self).create({'product_id': data['product_id']})