# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.exceptions import UserError, AccessError
from odoo.tools.misc import formatLang
from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP
import odoo.addons.decimal_precision as dp


class pricelist_line_partner(models.Model):
    _name = 'pricelist.line.partner'
    _description = 'Select Pricelist Line'

    pricelis_line_ids = fields.Many2many('product.pricelist.item', 'pridct_pricelist_item_group_rel', 'pricelist_id', 'part_id', 'Pricelist Line')
    pricelist_id = fields.Many2one('product.pricelist','Pricelist')

    @api.model
    def default_get(self, fields):
        res = super(pricelist_line_partner, self).default_get(fields)
        if not res.get('pricelist_id'):
            pricelist_id = res.get('pricelist_id', self._context.get('pricelist_id'))
            res['pricelist_id'] = pricelist_id
        return res

    @api.multi
    def compute_sheet_orderline(self):
        sale_obj = self.env['sale.order']
        [data] = self.read()
        active_id = self.env.context.get('active_id')
        if data['pricelis_line_ids']:
            context = self.env.context.copy()
            context.update({'pricelist_line':True})
            for price_id in data['pricelis_line_ids']:
                price_line = self.env['product.pricelist.item'].browse(price_id)
                res = {
                    'product_id': price_line.product_id.id,
                    'product_uom_qty': price_line.min_quantity,
                    'price_unit': price_line.fixed_price or price_line.part_number.seq_price,
                    'name':price_line.product_id.name,
                    'product_uom':price_line.product_id.uom_id.id,
                    'order_id':active_id,
                    'part_number':price_line.part_number.id,
                    'part_number_product':price_line.part_number_product.id,
                    'drawing_number':price_line.drawing_number,
                    'pricing_date':price_line.part_number.pricing_date,
                }
                self.env['sale.order.line'].create(res)
            return {'type': 'ir.actions.act_window_close'}
