# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp
from odoo.tools.translate import _
from odoo import tools
import time
from odoo.exceptions import UserError, ValidationError

class stock_produce_product_qty(models.TransientModel):
    _inherit = "stock.produce.product.qty"
    _description = "Change Product Quantity"

    stock_produce_lines = fields.One2many('stock.produce.product.qty.line', 'stock_produce')
    product_uom = fields.Many2one('product.uom')

    @api.onchange('product_uom')
    def onchange_product_uom_id(self):
        res = {}
        if self.product_uom.category_id != self.product_id.uom_id.category_id:
            self.product_uom = self.product_id.uom_id.id
            res['warning'] = {'title': _('Warning'), 'message': _('The Product Unit of Measure you chose has a different category than in the product form.')}
        else:
            self.onchange_new_quantity()
        return res

    @api.multi
    @api.onchange('new_quantity')
    def onchange_new_quantity(self):
        for line in self.stock_produce_lines:
            amount = self.product_uom._compute_quantity(float(self.new_quantity), line.bom_line_id.bom_id.product_uom_id, round=True, rounding_method='UP')
            qty = amount * line.bom_line_id.product_qty/ line.bom_line_id.bom_id.product_qty
            qty = line.bom_line_id.product_uom_id._compute_quantity(float(qty), line.product_uom, round=True, rounding_method='UP')
            line.actual_qty = qty
            line.bom_qty = qty


    @api.model
    def default_get(self, fields):
        """ To get default values for the object.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param fields: List of fields for which we want default values
         @param context: A standard dictionary
         @return: A dictionary which of fields with values.
        """
        res = super(stock_produce_product_qty, self).default_get(fields)
        if 'product_id' in res.keys():
            product_ids = self.env['product.product'].search([('id', '=', res['product_id'])])
            res['product_uom'] = product_ids[0].uom_id.id
            res['stock_produce_lines'] = []
            bom = self.env['mrp.bom'].search(['|', ('product_tmpl_id', '=', product_ids[0].product_tmpl_id.id),('product_id', '=', product_ids[0].id)], limit=1)
            for line in bom.bom_line_ids:
                qty = res['new_quantity'] * line.product_qty/ bom.product_qty
                res['stock_produce_lines'].append((0, 0, {
                    'product_id': line.product_id.id,
                    'product_uom': line.product_uom_id.id,
                    'actual_qty': qty,
                    'bom_qty': qty,
                    'bom_line_id':line.id,
                }))

        return res

    @api.multi
    def produce_product_qty(self):
        move_obj = self.env['stock.move']
        seq_obj = self.env['ir.sequence']

        for data in self:
            sequence_search = seq_obj.search([('code', '=', 'stock.lot.serial')])
            if not sequence_search:
                raise ValidationError(_('Not Sequence Setting'))
            if sequence_search.category.id == data.product_id.categ_id.id:
                next_number = sequence_search.next_by_id()
            else:
                next_number = ''

            lot_ids = []

            lot_vals = {'name': next_number, 'product_id': data.product_id.id,'count_for_print': data.new_quantity,'produce_date': time.strftime('%Y-%m-%d %H:%M:%S')}

            ####One Lot Number
            new_lot = self.env['stock.production.lot'].create(lot_vals)
            lot_ids.append(new_lot.id)
            val = {
                'product_id': data.product_id.id,
                'product_uom': data.product_id.uom_id.id,
                'name': "Produced " + data.product_id.name,
                'location_id': data.product_id.property_stock_production.id,
                'location_dest_id': data.location_id.id,
                'product_uom_qty': data.new_quantity,
                'restrict_lot_id': new_lot.id if new_lot else False,
            }
            move_id = move_obj.create(val)
            move_id.action_done()
            move_id.write({'picking_type_id': 1})

            # bom_ids = self.env['mrp.bom'].search(['|', ('product_tmpl_id', '=', data.product_id.id),('product_id', '=', data.product_id.id)])
            # group_mrp_user_id = self.env['ir.model.data'].xmlid_to_res_id('mrp.group_mrp_user')
            partner_location_id = self.env['stock.location'].search([('usage', '=', 'customer'), ('company_id', '=', self.env.user.company_id.id)], limit=1)
            for line in data.stock_produce_lines:
                available_qty = line.product_id.with_context(location=data.location_id.id)._product_available().get(line.product_id.id, {}).get('qty_available')
                after_available_qty = line.product_id.uom_id._compute_quantity(float(available_qty), line.product_uom, round=True, rounding_method='UP')
                if after_available_qty >= line.actual_qty:
                    deduct_val = {
                        'product_id': line.product_id.id,
                        'product_uom': line.product_uom.id,
                        'name': "Deducted " + line.product_id.name,
                        'location_id': data.location_id.id,
                        'location_dest_id': partner_location_id.id,
                        'product_uom_qty': line.actual_qty,
                        'restrict_lot_id': new_lot.id if new_lot else False,
                    }
                    move_id = move_obj.create(deduct_val)
                    move_id.action_done()
                    move_id.write({'picking_type_id': 1})
                else:
                    raise ValidationError(_('Material '+line.product_id.name+' have not enough stock.'))

            datas = {'ids': lot_ids}
            datas['model'] = 'stock.produce.product.qty'
            return self.env['report'].get_action(new_lot, 'central_kitchen.report_lot_barcode_custom')
    @api.multi
    def produce_product_qty2(self):
        """ Changes the Product Quantity by making a Physical Inventory.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param context: A standard dictionary
        @return:
        """

        inventory_obj = self.env['stock.inventory']
        inventory_line_obj = self.env['stock.inventory.line']

        for data in self:
            if data.new_quantity < 0:
                raise ValidationError(_('Quantity cannot be negative.'))
            ctx = self._context.copy()
            ctx['location'] = data.location_id.id
            ctx['lot_id'] = data.lot_id.id
            if data.product_id.id and data.lot_id.id:
                filter = 'none'
            elif data.product_id.id:
                filter = 'product'
            else:
                filter = 'none'
            inventory_id = inventory_obj.create({
                'name': _('INV: %s') % tools.ustr(data.product_id.name),
                'filter': filter,
                'product_id': data.product_id.id,
                'location_id': data.location_id.id,
                'lot_id': data.lot_id.id})
            product = data.product_id.with_context(location=data.location_id.id, lot_id=data.lot_id.id)
            th_qty = product.qty_available
            line_data = {
                'inventory_id': inventory_id,
                'product_qty': data.new_quantity,
                'location_id': data.location_id.id,
                'product_id': data.product_id.id,
                'product_uom_id': data.product_id.uom_id.id,
                'theoretical_qty': th_qty,
                'prod_lot_id': data.lot_id.id
            }
            inventory_line_obj.create(line_data)
            inventory_id.action_done()
        return {}

class stock_produce_product_qty_line(models.TransientModel):
    _name = "stock.produce.product.qty.line"

    product_id = fields.Many2one('product.product', string='Product')
    bom_qty = fields.Float('BOM Qty')
    actual_qty = fields.Float('Actual Qty')
    product_uom = fields.Many2one('product.uom')
    stock_produce = fields.Many2one('stock.produce.product.qty')
    bom_line_id = fields.Many2one('mrp.bom.line')


    @api.onchange('product_uom')
    def onchange_product_uom_id(self):
        res = {}
        if self.product_uom.category_id != self.product_id.uom_id.category_id:
            self.product_uom = self.product_id.uom_id.id
            res['warning'] = {'title': _('Warning'), 'message': _('The Product Unit of Measure you chose has a different category than in the product form.')}
        else:
            self.onchange_new_quantity()
        return res

