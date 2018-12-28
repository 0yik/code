from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare

class stock_picking(models.Model):
    _inherit = 'stock.picking'

    def _prepare_pack_ops(self, quants, forced_qties):
        result = super(stock_picking, self)._prepare_pack_ops(quants, forced_qties)
        return result

    @api.multi
    def do_prepare_partial(self):
        # TDE CLEANME: oh dear ...
        PackOperation = self.env['stock.pack.operation']

        # get list of existing operations and delete them
        existing_packages = PackOperation.search([('picking_id', 'in', self.ids)])  # TDE FIXME: o2m / m2o ?
        if existing_packages:
            existing_packages.unlink()
        for picking in self:
            # forced_qties = {}  # Quantity remaining after calculating reserved quants
            picking_quants = self.env['stock.quant']
            # Calculate packages, reserved quants, qtys of this picking's moves
            for move in picking.move_lines:
                forced_qties = {}
                if move.state not in ('assigned', 'confirmed', 'waiting'):
                    continue
                move_quants = move.reserved_quant_ids
                picking_quants += move_quants
                forced_qty = 0.0
                if move.state == 'assigned':
                    # qty = move.product_uom._compute_quantity(move.product_uom_qty, move.product_id.uom_id, round=False)
                    qty = move.product_uom_qty
                    forced_qty = qty - sum([x.qty for x in move_quants])
                # if we used force_assign() on the move, or if the move is incoming, forced_qty > 0
                if float_compare(forced_qty, 0, precision_rounding=move.product_uom.rounding) > 0:
                    if forced_qties.get(move.product_id):
                        forced_qties[move.product_id] += forced_qty
                    else:
                        forced_qties[move.product_id] = forced_qty
                for vals in picking._prepare_pack_ops(picking_quants, forced_qties):
                    vals['fresh_record'] = False
                    vals['product_uom_id'] = move.product_uom.id
                    vals['product_qty'] = forced_qty
                    PackOperation |= PackOperation.create(vals)
        # recompute the remaining quantities all at once
        self.do_recompute_remaining_quantities()
        for pack in PackOperation:
            pack.ordered_qty = sum(
                pack.mapped('linked_move_operation_ids').mapped('move_id').filtered(
                    lambda r: r.state != 'cancel').mapped('ordered_qty')
            )
        self.write({'recompute_pack_op': False})