# -*- coding: utf-8 -*-

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class stock_location(models.Model):
    _inherit = 'stock.location'

    qty_available = fields.Float(
        string='Quantity On Hand',
        compute='_get_location_availble',
        digits=dp.get_precision('Product Unit of Measure'),
        help='Quantity On Hand for product specified on the context',
    )
    virtual_available = fields.Float(
        string='Forecast Quantity',
        compute='_get_location_availble',
        digits=dp.get_precision('Product Unit of Measure'),
        help='Forecast Quantity for product specified on the context',
    )
    incoming_qty = fields.Float(
        string='Incoming',
        compute='_get_location_availble',
        digits=dp.get_precision('Product Unit of Measure'),
        help='Incoming for product specified on the context',
    )
    outgoing_qty = fields.Float(
        string='Outgoing',
        compute='_get_location_availble',
        digits=dp.get_precision('Product Unit of Measure'),
        help='Outgoing for product specified on the context',
    )

    @api.multi
    def _get_location_availble(self):
        product_id = self._context.get('product_id', False)
        template_id = self._context.get('template_id', False)
        if product_id or template_id:
            source = self.env['product.{}'.format('product' if product_id else 'template')].browse(
                product_id if product_id else template_id
            )
            for field in ('qty_available', 'virtual_available', 'incoming_qty', 'outgoing_qty'):
                for rec in self:
                    rec.__setattr__(field, source.with_context(location=[rec.id]).__getattribute__(field))
