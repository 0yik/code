# -*- coding: utf-8 -*-

from itertools import groupby
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.misc import formatLang

import odoo.addons.decimal_precision as dp

class product_teamplate(models.Model):
    _inherit = 'product.template'

    ##Arya
    date_start  = fields.Date(string='Date Start')
    date_end    = fields.Date(string='Date End')
    ##
    product_bundle_ids = fields.One2many('product.bundle','product_bundle_id')

    can_be_bundle_gift = fields.Boolean('Can be Bundle/Gift')

    @api.onchange('can_be_bundle_gift')
    def onchage_can_be_bundle_gift(self):
        if self.can_be_bundle_gift:
            products = self.env['product.product'].search([])
            return {'domain':{'product_bundle_ids':[('product_id','in', products.ids)]}}
        else:
            return {'domain': {'product_bundle_ids': [('product_id', 'in', [])]}}

class product_bundle(models.Model):
    _name = 'product.bundle'

    @api.model
    def get_quantity_on_hand(self):
        for record in self:
            record.quantity = record.product_id.product_tmpl_id.qty_available if record.product_id else 0

    product_id = fields.Many2one('product.product',string='Bundle/ Gift Name')
    quantity = fields.Integer(string='Quantity', compute=get_quantity_on_hand)
    product_bundle_id = fields.Many2one('product.template')

    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id:
            self.quantity = self.product_id.product_tmpl_id.qty_available

    # @api.onchange('can_be_bundle_gift')
    # def onchange_can_be_bundle_gift(self):
    #     if self.can_be_bundle_gift:
    #         products = self.env['product.product'].search([])
    #         return {'domain':{'product_id':[('id','in', products.ids)]}}
    #     else:
    #         return {'domain': {'product_id': [('id', 'in', [])]}}
    # @api.model
    # def get_default_bundle(self):
    #     return self._context.get('filt_product')


