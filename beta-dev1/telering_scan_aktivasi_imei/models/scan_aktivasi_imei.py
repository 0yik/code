# -*- coding: utf-8 -*-

from odoo import fields,models,_,api

class stock_picking_internal(models.Model):
    
    _inherit = "stock.picking"
    
    imei_active = fields.Boolean("IMEI Activation")
    
class stock_location_imei(models.Model):
    
    _inherit = "stock.location"
    
    imei_active = fields.Boolean("IMEI Activation")

class stock_pack_operation_imei(models.Model):
    
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
        if self.picking_id.imei_active:
            imei_active = True
        else:
            imei_active = False
        action_ctx.update({
            'show_imei' : is_imei,
            'imei_active' : imei_active,
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
    
class stock_pack_operation_lot_imei(models.Model):
    
    _inherit = 'stock.pack.operation.lot'
    
    lot_number = fields.Char("Lot/Serial Number")
    
    @api.constrains('lot_id', 'lot_name', 'lot_number')
    def _check_lot(self):
        if any(not lot.lot_name and not lot.lot_id and not lot.lot_number for lot in self):
            raise ValidationError(_('Lot/Serial Number required'))
        return True
