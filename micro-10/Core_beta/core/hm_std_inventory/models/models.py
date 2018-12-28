# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions




class stock_picking_inherit(models.Model):
    _inherit = 'stock.picking'

    # @api.multi
    # def do_new_transfer(self):
    #     res = super(stock_picking_inherit, self).do_new_transfer()
    #     if len(self.pack_operation_product_ids) > 0:
    #         correct_operas = self.pack_operation_product_ids
    #         stock_out = self.env['stock.picking'].search(
    #             [('group_id', '=', self.group_id.id), ('picking_type_id', '=', 4)])
    #         lots = stock_out.pack_operation_product_ids.pack_lot_ids
    #         for correct_opera in correct_operas:
    #             for r in correct_opera.pack_lot_ids:
    #                 if r.lot_id:
    #                     for lot in lots:
    #                         if lot.lot_id == r.lot_id:
    #                             lot.qty = r.qty
    #         stock_out.pack_operation_product_ids.qty_done = correct_operas.qty_done
    #     return res




class stock_picking_waves(models.Model):
    _inherit = 'stock.picking.wave'

    name = fields.Char( string='Name', required=True)
 #  operation_category = fields.Selection([
 #       ('receiving', 'Receiving'),
 #       ('picking', 'Picking'),
 #       ('packing', 'Packing'),
 #       ('delivery', 'Delivery'),
 #       ('other', 'Others')])

    operation_category = fields.Many2one(
        comodel_name='stock.operation.category',
        string='Operation Category', help='Opration Category')
     #pick_id = fields.Many2one(
     #    comodel_name='stock.picking',
     #    string='Pick id', help='dummy field to filter the o2m')

   #@api.model
   #def default_get(self, flds):
   #    res = super(stock_picking_waves, self).default_get(flds)
   #    return res

    @api.multi
    @api.onchange('operation_category')
    def onchange_operation_category(self):
        """Onchange operation category"""
        if not self.operation_category:
            return {'domain': {'picking_ids': [('id', 'in', [])]}}
        pick_pool = self.env['stock.picking']
        picking_ids = []
        #if self.operation_category == 'receiving':
        if self.operation_category.name == 'Receiving':
            picking_ids = pick_pool.search(
                [('picking_type_id.code', '=', 'incoming')])
        #elif self.operation_category == 'packing':
        elif self.operation_category.name == 'Packing':
            picking_ids = pick_pool.search(
                [('picking_type_id.name', '=', 'Pack')])
        #elif self.operation_category == 'picking':
        elif self.operation_category.name == 'Picking':
            picking_ids = pick_pool.search(
                [('picking_type_id.name', '=', 'Pick')])
        #elif self.operation_category == 'delivery':
        elif self.operation_category.name == 'Delivery':
            picking_ids = pick_pool.search(
                [('picking_type_id.name', '=', 'Delivery Orders')])
        else:
            picking_ids = pick_pool.search([])
        domain={'picking_ids': [('id', 'in', picking_ids and picking_ids.ids or [])]}
        result = {'domain': domain}
        return result


class operation_category(models.Model):
    _name = 'stock.operation.category'

    name = fields.Char('Name', required=True)


class stock_location(models.Model):
    _name = 'stock.location.quant'

    location = fields.Many2one('stock.location', string='Location')
    location_dest_id = fields.Many2one('stock.location', string='Destination  ')

    def create_internal_transfer(self):
        stock_move_obj = self.env['stock.move']
        stock_ids = self.env['stock.quant'].search([('id','=',self.env.context.get('active_ids'))])
        location_list = []
        for stock in stock_ids:
            if stock.location_id.id not in location_list:
                location_list.append(stock.location_id.id)
        if len(location_list) != 1:
            raise exceptions.ValidationError("Can't select product form different Warehouses.")
            return {
                'warning': {
                    'title': "Too many Warehouses",
                    'message': "Can't select product form different Warehouses.",
                },
            }

        else:
            data = {
                'location_id': stock_ids[0].location_id.id,
                'location_dest_id': self.location.id,
                'move_type': 'direct',
                'picking_type_id': self.env['stock.picking.type'].search([('code','=','internal')],limit=1).id
            }
            internal_trans = self.env['stock.picking'].create(data)
            for stock in stock_ids:
                line_data = {
                    'picking_id': internal_trans.id,
                    'name': stock.product_id.name,
                    'product_id': stock.product_id.id,
                    'product_uom_qty':stock.qty,
                    'product_uom': 1,
                    'location_id': stock_ids[0].location_id.id,
                    'location_dest_id': self.location.id,
                }
                stock_move_obj.create(line_data)
        # internal_trans.action_confirm()
        # internal_trans.action_assign()

    def cancel(self):
        pass
class stock_quant(models.Model):
    _inherit = 'stock.quant'


    @api.model
    def put_away(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Put Away Location',
            'res_model': 'stock.location.quant',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id'  : self.env.ref('hm_std_inventory.stock_location_form_view').id,
            'target'   : 'new',
            'context'  :  self.env.context
        }
    def create_internal_transfer(self):
        True
    def cancel(self):
        pass

class user_inherit(models.Model):
    _inherit = 'res.users'

    allowe_WH = fields.Many2many('stock.warehouse', string='Allowed Warehouses')
