# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class Picking(models.Model):
    _inherit = 'stock.picking'
    
    @api.multi
    def do_print_sku(self):
        print "calling >>>",self
        return self.env["report"].get_action(self, 'vinay-27022017-test-a-b.report_stock_picking_new')


class Merge_Transfer_Stock(models.TransientModel):
    _name = 'merge.transfer.stock'
    _description = 'Merged Transfer Stock'

    pick_ids = fields.Many2many('stock.picking', 'stock_picking_merge_rel', 'pick_id', 'merge_id', string='All Transfer')

    @api.model
    def default_get(self, fields):
        res = super(Merge_Transfer_Stock, self).default_get(fields)
        if not res.get('pick_ids') and self._context.get('active_ids'):
            res['pick_ids'] = self._context['active_ids']
        return res
        
    @api.multi
    def merged_transfer(self):
        first_picking = self.pick_ids[0]
        picking_type_id = first_picking.picking_type_id.id
        for pick in self.pick_ids:
            if pick.picking_type_id.id <> picking_type_id:
                raise UserError(_('Diff Picking type selected, choose same picking type to merge.'))
        new_picking = first_picking.copy()
        picking_names = ', '.join(self.pick_ids.mapped('name'))
        new_picking.write({'name':picking_names})
        new_picking.move_lines.unlink()
        product_move_dict = {}
        done_l = []
        for pick in self.pick_ids:
            for move in pick.move_lines:
                if move.product_id.id not in done_l:
                    done_l.append(move.product_id.id)
                    product_move_dict[move.product_id.id] = [move]
                    new_move = move.copy()
                    new_move.write({'picking_id':new_picking.id, 'product_uom_qty':0.0})
                else:
                    product_move_dict[move.product_id.id].append(move)
        for k, v in product_move_dict.items():
            for move in new_picking.move_lines:
                if move.product_id.id == k:
                    qty = 0.0
                    for m in v:
                        qty += m.product_uom_qty
                    move.write({'product_uom_qty':qty})
        self.pick_ids.action_cancel()
        return {
                'name': _('Merge Picking Order'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.picking',
                'type': 'ir.actions.act_window',
                'res_id': new_picking.id,
                'context': self.env.context
            }