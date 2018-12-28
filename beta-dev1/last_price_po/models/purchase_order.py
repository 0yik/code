# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DF

class PurchaseConfigSettings(models.TransientModel):
    _inherit = 'purchase.config.settings'

    average_last_calculation = fields.Integer('Average Last Calculation')

    @api.multi
    def set_average_last_calculation(self):
        check = self.env.user.has_group('base.group_system')     
        Values = check and self.env['ir.values'].sudo() or self.env['ir.values']
        for config in self:
            Values.set_default('purchase.config.settings', 'average_last_calculation', config.average_last_calculation)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def update_last_purchase_price(self):
        check = self.env.user.has_group('base.group_system')
        Values = check and self.env['ir.values'].sudo() or self.env['ir.values']
        days = Values.get_default('purchase.config.settings', 'average_last_calculation') or 0
        to_date = datetime.datetime.now()
        from_date = to_date - datetime.timedelta(days=days)
        for rec in self.order_line:
            dom = [('product_id', '=', rec.product_id.id), ('order_id', '!=', self.id)]
            line = self.order_line.search(dom, order='id desc', limit=1)
            rec.last_purchased_unit_price = line.price_unit
            rec.last_average_unit_price = rec.calculate_latest_average_price(rec.product_id, from_date, to_date)

class PurchaseOrderLine(models.Model):

    _inherit = 'purchase.order.line'

    @api.model
    def create(self, vals):
        result = super(PurchaseOrderLine, self).create(vals)
        check = self.env.user.has_group('base.group_system')
        Values = check and self.env['ir.values'].sudo() or self.env['ir.values']
        days = Values.get_default('purchase.config.settings', 'average_last_calculation') or 0
        to_date = datetime.datetime.now()
        from_date = to_date - datetime.timedelta(days=days) 
        line = self.search([('product_id', '=', result.product_id.id), ('order_id', '!=', result.order_id.id)], order='id desc', limit=1)
        result.last_purchased_unit_price = line.price_unit
        result.last_average_unit_price = self.calculate_latest_average_price(result.product_id, from_date, to_date)


    @api.onchange('product_id')
    def onchange_product_id(self):
        check = self.env.user.has_group('base.group_system')
        Values = check and self.env['ir.values'].sudo() or self.env['ir.values']
        days = Values.get_default('purchase.config.settings', 'average_last_calculation') or 0
        to_date = datetime.datetime.now()
        from_date = to_date - datetime.timedelta(days=days)
        for rec in self:
            dom = [('product_id', '=', rec.product_id.id)]
            if self.env.context.get('order_name'):
                dom.append(('order_id.name', '!=', self.env.context['order_name']))
            line = self.search(dom, order='id desc', limit=1)
            rec.last_purchased_unit_price = line.price_unit
            rec.last_average_unit_price = rec.calculate_latest_average_price(rec.product_id, from_date, to_date)

        return super(PurchaseOrderLine, self).onchange_product_id()

    @api.model
    def calculate_latest_average_price(self, product, from_date=None, to_date=None):
        if not from_date or not to_date:
            check = self.env.user.has_group('base.group_system')
            Values = check and self.env['ir.values'].sudo() or self.env['ir.values']
            days = Values.get_default('purchase.config.settings', 'average_last_calculation') or 0
            to_date = datetime.datetime.now()
            from_date = to_date - datetime.timedelta(days=days)
        lines = self.search([('product_id', '=', product.id), ('order_id.create_date', '>=', from_date.strftime(DF)), ('order_id.create_date', '<=', to_date.strftime(DF))], order='id desc')
        price_subtotal = sum([line.price_subtotal for line in lines if line.price_subtotal])
        total_quantity = sum([line.product_qty for line in lines if line.product_qty])
        if not total_quantity:
            return 0
        return price_subtotal/total_quantity

    last_purchased_unit_price = fields.Float(string='Last Purchased Price', digits=dp.get_precision('Product Price'))
    last_average_unit_price = fields.Float(string='Last Average Price', digits=dp.get_precision('Product Price'))
