# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp
from odoo.tools.translate import _
from odoo import tools
import time
from odoo.exceptions import UserError, ValidationError

class stock_quant(models.Model):
    _inherit = 'stock.quant'

    lot_id = fields.Many2one('stock.production.lot', 'Lot', readonly=True, select=True, )

stock_quant()


class stock_produce_product_qty(models.TransientModel):
    _name = "stock.produce.product.qty"
    _description = "Change Product Quantity"

    product_id = fields.Many2one('product.product', string='Product', default= lambda self: self.env.context.get('active_id', False))
    new_quantity = fields.Float('Amount to be Produced', default=1,
                                 digits_compute=dp.get_precision('Product Unit of Measure'), required=True,
                                 help='This quantity is expressed in the Default Unit of Measure of the product.')
    lot_id = fields.Many2one('stock.production.lot', string='Serial Number', domain="[('product_id','=',product_id)]")
    location_id = fields.Many2one('stock.location', string='Location', required=True,
                                   domain="[('usage', '=', 'internal')]")

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
        context = self.env.context
        if context.get('active_model') == 'product.template':
            product_ids = self.env['product.product'].search([('product_tmpl_id', '=', context.get('active_id'))])

            if len(product_ids) == 1:
                res['product_id'] = product_ids[0]
            else:
                raise ValidationError(_('Please use the Product Variant view to update the product quantity.'))

        ####
        product_ids = self.env['product.product'].browse(context.get('active_id'))
        new_quantity = 0.0
        if abs(product_ids[0].qty_to_produce or 0.0) > 0:
            new_quantity = abs(product_ids[0].qty_to_produce or 0.0)
        res['new_quantity'] = new_quantity
        ##

        if 'location_id' in fields:
            location_id = res.get('location_id', False)
            if not location_id:
                try:
                    model, location_id = self.env['ir.model.data'].get_object_reference('stock',
                                                                                             'stock_location_stock')
                except ValueError:
                    pass
            if location_id:
                try:
                    self.location_id.check_access_rule('read')
                except ValueError:
                    location_id = False

            res['location_id'] = location_id
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

            bom_ids = self.env['mrp.bom'].search(['|', ('product_tmpl_id', '=', data.product_id.id),('product_id', '=', data.product_id.id)])
            group_mrp_user_id = self.env['ir.model.data'].xmlid_to_res_id('mrp.group_mrp_user')
            partner_location_id = self.env['stock.location'].search([('usage', '=', 'customer')])
            for bom in bom_ids:
                if group_mrp_user_id and bom:
                    if bom.bom_line_ids:
                        for line in bom.bom_line_ids:
                            if line.product_id.qty_available >= data.new_quantity:
                                deduct_val = {
                                    'product_id': line.product_id.id,
                                    'product_uom': line.product_id.uom_id.id,
                                    'name': "Deducted " + line.product_id.name,
                                    'location_id': data.location_id.id,
                                    'location_dest_id': partner_location_id.id,
                                    'product_uom_qty': data.new_quantity,
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

stock_produce_product_qty()
