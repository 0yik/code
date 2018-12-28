# -*- coding: utf-8 -*-


from odoo import models, fields, api,_


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    imei_number = fields.Char('IMEI')

class StockPackOperation(models.Model):
    _inherit = 'stock.pack.operation'




    @api.multi
    def action_split_lots_inherit(self):
        action_ctx = dict(self.env.context)
        # If it's a returned stock move, we do not want to create a lot
        returned_move = self.linked_move_operation_ids.mapped('move_id').mapped('origin_returned_move_id')
        picking_type = self.picking_id.picking_type_id
        is_imei = False
        if self.product_id.product_type == 'smartphone' and self.product_id.tracking == 'serial':
            is_imei = True
        if self.product_id.product_type != 'smartphone' and self.product_id.tracking == 'serial':
            is_imei = False

        action_ctx.update({
            'show_imei' : is_imei,
            'serial': self.product_id.tracking == 'serial',
            'only_create': picking_type.use_create_lots and not picking_type.use_existing_lots and not returned_move,
            'create_lots': picking_type.use_create_lots,
            'state_done': self.picking_id.state == 'done',
            'show_reserved': any([lot for lot in self.pack_lot_ids if lot.qty_todo > 0.0])})
        view_id = self.env.ref('stock.view_pack_operation_lot_form').id
        return {
            'name': _('Lot/Serial Number Details'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.pack.operation',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
            'res_id': self.ids[0],
            'context': action_ctx}

    split_lot = action_split_lots_inherit


class StockPackoperationLot(models.Model):
    _inherit = 'stock.pack.operation.lot'

    imei_number = fields.Char('IMEI')

    def action_add_quantity(self, quantity):
        for lot in self:
            lot.write({'qty': lot.qty + quantity})
            lot.operation_id.write({'qty_done': sum(operation_lot.qty for operation_lot in lot.operation_id.pack_lot_ids)})
        return self.mapped('operation_id').action_split_lots_inherit()
    @api.model
    def create(self, vals):
        if 'imei_number'in vals and vals['imei_number'] == False:
            vals.update({
                'imei_number': vals['lot_name'],
            })
        res = super(StockPackoperationLot, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        if 'lot_name' in vals:
            vals.update({
                'imei_number': vals['lot_name'],
            })
        res = super(StockPackoperationLot, self).write(vals)
        if self.lot_id:
            self.lot_id.imei_number = self.imei_number and self.imei_number or False
        return res