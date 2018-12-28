# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError

class sale_order(models.Model):
    _inherit = 'sale.order'

    @api.depends('order_line')
    def get_product_bundle(self):
        self.bundle_line_ids.bundle_id = self.order_line.product_tmpl_id.product_bundle_ids
    bundle_line_ids = fields.One2many('bundle.line', 'sale_order_id', string="bundle line")

    @api.onchange('order_line')
    def modify_bundle(self):
        bundle_line_ids = self.bundle_line_ids.browse([])
        for order_line in self.order_line:
            product_template = self.env['product.template'].search([('id', '=', order_line.product_id.product_tmpl_id.id)])
            if product_template.product_bundle_ids:
                order_line.special_start = True
            for product_bundle in product_template.product_bundle_ids:
                bundle_line_ids += self.bundle_line_ids.new({
                    'bundle_id': product_bundle.id,
                    'product_name': product_bundle.product_bundle_id.name,
                    'name': product_bundle.product_id.name,
                    'gift_qty_on_hand': product_bundle.quantity,
                    'sale_order_id': self.id,
                })
        self.bundle_line_ids = bundle_line_ids

    @api.multi
    def add_bundle(self):
        uom = self.env['product.uom'].search([('name', '=', 'Unit(s)')], limit=1) or self.env['product.uom'].search([], limit=1)
        for record in self:
            for bundle_line in self.bundle_line_ids:
                product_id = self.env['product.template'].search([(('name', '=', bundle_line.name))], limit=1)
                record.order_line += record.order_line.new({
                    'product_id' : bundle_line.bundle_id.product_id.id or product_id.id,
                    'name' : bundle_line.name,
                    'product_uom_qty' : bundle_line.gift_qty_to_give,
                    'price_unit' : 0,
                    'product_uom' : uom and uom.id,
                    'discount' : 0,
                    'price_subtotal' : 0
                })

class bundle_line(models.Model):
    _name = 'bundle.line'

    bundle_id = fields.Many2one('product.bundle', required=True)
    name = fields.Char('Bundle/Gift Name', required=True)
    product_name = fields.Char('Product', required=True)
    gift_qty_on_hand = fields.Integer('Gift Qty On Hand', required=True)
    gift_qty_to_give = fields.Integer('Gift Qty To Give')
    sale_order_id = fields.Many2one('sale.order')

    @api.multi
    @api.depends('gift_qty_to_give')
    def contrains_gift_qty_to_give(self):
        for record in self:
            if record.gift_qty_to_give > record.gift_qty_on_hand:
                record.gift_qty_to_give = record.gift_qty_on_hand

    @api.onchange('gift_qty_to_give')
    def validate_gift_qty_to_give(self):
        if self.gift_qty_to_give > self.gift_qty_on_hand:
            self.gift_qty_to_give = self.gift_qty_on_hand
            return {
                'warning': {'title': 'Warning!', 'message': 'The gift qty to give must be less than gift qty on hand'},
            }

    @api.multi
    def add_bundle(self):

        pass


class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    product_bundle_id = fields.Many2many('product.product', 'rel_so_product_bundle',
                                         'so_line_id', 'product_id', string='Bundle/gift', readonly=False, store=True)
    special_start = fields.Boolean(default=False)

    @api.multi
    @api.onchange('product_id')
    def onchange_product_with_freegift(self):
        for order_line in self:
            if order_line.product_id:
                if order_line.product_id.product_tmpl_id.product_bundle_ids:
                    order_line.special_start = True

    @api.multi
    @api.onchange('product_id', 'product_bundle_id')
    def onchange_product_and_bundle(self):
        for order_line in self:
            if order_line.product_id:
                product_buble_ids = []
                for product_buble in order_line.product_id.product_tmpl_id.product_bundle_ids:
                    if product_buble:
                        product_buble_ids.append(product_buble.product_id.id)

                if product_buble_ids:
                    order_line.special_start = True
                order_line.product_budle_id = product_buble_ids

    @api.multi
    def _action_procurement_create(self):
        """
        Create procurements based on quantity ordered. If the quantity is increased, new
        procurements are created. If the quantity is decreased, no automated action is taken.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        new_procs = self.env['procurement.order']  # Empty recordset
        for line in self:
            if line.state != 'sale' or not line.product_id._need_procurement():
                continue
            qty = 0.0
            for proc in line.procurement_ids:
                qty += proc.product_qty
            if float_compare(qty, line.product_uom_qty, precision_digits=precision) >= 0:
                continue

            if not line.order_id.procurement_group_id:
                vals = line.order_id._prepare_procurement_group()
                line.order_id.procurement_group_id = self.env["procurement.group"].create(vals)

            vals = line._prepare_order_line_procurement(group_id=line.order_id.procurement_group_id.id)
            vals['product_qty'] = line.product_uom_qty - qty
            new_proc = self.env["procurement.order"].create(vals)

            new_proc.message_post_with_view('mail.message_origin_link',
                                            values={'self': new_proc, 'origin': line.order_id},
                                            subtype_id=self.env.ref('mail.mt_note').id)
            new_procs += new_proc

            ###Gift Process
            vals_picking = {
                'partner_id': line.order_id.partner_id.id,
                'picking_type_id': 4,
                'location_id': 15,
                'location_dest_id': 9}
            picking_id = self.env['stock.picking'].create(vals_picking)

            if line.special_start:
                for lgift in line.product_bundle_id:
                    print "lgift---->>", lgift

                    vals_move = {
                        'name': lgift.name,
                        'product_id': lgift.id,
                        'product_uom': lgift.uom_id.id,
                        'product_uom_qty': 1,
                        'location_id': 15,
                        'location_dest_id': 9,
                        'picking_id': picking_id.id
                    }
                    self.env['stock.move'].create(vals_move)

        new_procs.run()

        return new_procs





