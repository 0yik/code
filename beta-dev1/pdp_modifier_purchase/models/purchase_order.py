# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from lxml import etree
import json

import logging
_logger = logging.getLogger(__name__)

class purchase_order(models.Model):
    _inherit = 'purchase.order'

    @api.depends('order_line','order_line.qty_unreceived')
    def _compute_received_status(self):
        for record in self:
            for line in record.order_line:
                if line.qty_unreceived > 0:
                    record.received_status = 'Undone'
                else:
                    record.received_status = 'Done'

    received_status = fields.Char(compute='_compute_received_status', string="Received Status", store=True)

purchase_order()

class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'


    # product_code = fields.Char(string='Product Code')

    @api.multi
    @api.onchange('product_id')
    def onchange_stock_pick_product_id(self):
        if self.product_id:
            self.price_unit = self.product_id.lst_price
            # self.update({'product_code': self.product_id.product_tmpl_id.code})


    @api.depends('product_qty', 'qty_received')
    def _compute_qty_unreceived(self):
        for line in self:
            line.qty_unreceived = line.product_qty - line.qty_received

    @api.depends('product_id')
    def _get_product_code(self):
        for record in self:
            if record.product_id:
                record.product_code = record.product_id.product_tmpl_id.code

    product_code = fields.Char(string='Product Code', compute='_get_product_code')
    qty_unreceived = fields.Float(compute='_compute_qty_unreceived', string="Unreceived Qty",digits=dp.get_precision('Product Unit of Measure'), store=True)

    @api.model
    def create(self, vals):
        res = super(purchase_order_line, self).create(vals)
        for line in res:
            if line.order_id:
                order_lines = self.env['purchase.order.line'].search([('order_id.id','=',line.order_id.id),
                    ('product_id.id','=',line.product_id.id),('price_unit','=',line.price_unit),('product_uom.id','=',line.product_uom.id),
                     ('discount_type','=',line.discount_type),('discount_rate','=',line.discount_rate)])

                if len(order_lines) > 1:
                    self._cr.execute('''select product_qty from purchase_order_line where id=%s''' % (order_lines[0].id))
                    order_lines_qty = [x[0] for x in self.env.cr.fetchall()]
                    total_qty = order_lines[1].product_qty + order_lines_qty[0]

                    self._cr.execute('''update purchase_order_line set product_qty = %s where id=%s''' % (total_qty, order_lines[0].id))
                    self._cr.commit()
                    self._cr.execute('''delete from purchase_order_line where id=%s''' % (order_lines[1].id))
                    self._cr.commit()

    @api.multi
    def write(self,vals):
        res = super(purchase_order_line, self).write(vals)
        for line in self:

            if line.order_id:
                order_lines = self.env['purchase.order.line'].search([('order_id.id','=',line.order_id.id),
                ('product_id.id', '=', line.product_id.id),('price_unit','=',line.price_unit),('product_uom.id','=',line.product_uom.id),
                ('discount_type','=',line.discount_type),('discount_rate','=',line.discount_rate)])

                if len(order_lines) > 1:
                    self._cr.execute('''select product_qty from purchase_order_line where id=%s''' % (order_lines[0].id))
                    order_lines_qty = [x[0] for x in self.env.cr.fetchall()]
                    total_qty = order_lines[1].product_qty + order_lines_qty[0]

                    self._cr.execute('''update purchase_order_line set product_qty = %s where id=%s''' % (total_qty, order_lines[0].id))
                    self._cr.commit()
                    self._cr.execute('''delete from purchase_order_line where id=%s''' % (order_lines[1].id))
                    self._cr.commit()

purchase_order_line()


class res_partner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def name_get(self):
        if 'search_supplier_purchase' in self._context and self._context.get('search_supplier_purchase') == 1:
            res = []
            for record in self:
                if record.vendor_code:
                    res.append((record.id, str(record.vendor_code + " - " + record.name)))
                else:
                    res.append((record.id, str(record.name)))
            return res
        else:
            return super(res_partner, self).name_get()

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(res_partner, self).fields_view_get(view_id, view_type, toolbar=toolbar, submenu=False)
        doc = etree.XML(res['arch'])
        if 'search_supplier_purchase' in self._context and self._context.get('search_supplier_purchase') == 1:
            if view_type == 'tree':
                for node in doc.xpath("//field[@name='vendor_code']"):
                    node.set('invisible', "0")
                    node.set('modifiers', "{}")
                for node in doc.xpath("//field[@name='customer_code']"):
                    modifiers = json.loads(node.get("modifiers"))
                    modifiers['invisible'] = True
                    modifiers['tree_invisible'] = True
                    node.set('modifiers', json.dumps(modifiers))
        res['arch'] = etree.tostring(doc)
        return res

res_partner()
