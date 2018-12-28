from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = "stock.picking"
    
    auto_invoice_refund = fields.Boolean(string="Auto Invoice Refund")

class StockReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    @api.multi
    def _create_returns(self):
        new_picking_id, pick_type_id = super(StockReturnPicking, self)._create_returns()
        new_picking = self.env['stock.picking'].browse([new_picking_id])
        ###Edit###
        picking = self.env['stock.picking'].browse(self.env.context['active_id'])
        print "picking>>>>>", picking, picking.sale_id.id
         
        sale = self.env['sale.order'].browse([picking.sale_id.id])
         
        #sale.action_invoice_create(final=True)
        #raise UserError("XXXX")
        ##########
        for move in new_picking.move_lines:
            return_picking_line = self.product_return_moves.filtered(lambda r: r.move_id == move.origin_returned_move_id)
            if return_picking_line and return_picking_line.to_refund_so:
                move.to_refund_so = True
                ###Edit###
                new_picking.write({'auto_invoice_refund' : True})
                ##########
        #raise UserError(_("OOOOOOOO"))
        return new_picking_id, pick_type_id
    
#     @api.multi
#     def create_returns(self):
#         for wizard in self:
#             new_picking_id, pick_type_id = wizard._create_returns()
#             print "####new_picking_id>>>>>>>", new_picking_id
#             ###Edit####
#             picking = self.env['stock.picking'].browse([new_picking_id])
#             picking.write({'auto_invoice_refund' : True})
#             raise UserError(_("OOOOOOOO"))
#             ###########
#         # Override the context to disable all the potential filters that could have been set previously
#         ctx = dict(self.env.context)
#         ctx.update({
#             'search_default_picking_type_id': pick_type_id,
#             'search_default_draft': False,
#             'search_default_assigned': False,
#             'search_default_confirmed': False,
#             'search_default_ready': False,
#             'search_default_late': False,
#             'search_default_available': False,
#         })
#         return {
#             'name': _('Returned Picking'),
#             'view_type': 'form',
#             'view_mode': 'form,tree,calendar',
#             'res_model': 'stock.picking',
#             'res_id': new_picking_id,
#             'type': 'ir.actions.act_window',
#             'context': ctx,
#         }
    
    
class StockImmediateTransfer(models.TransientModel):
    _inherit = 'stock.immediate.transfer'
    _description = 'Immediate Transfer'

    @api.multi
    def process(self):
        self.ensure_one()
        # If still in draft => confirm and assign
        if self.pick_id.state == 'draft':
            self.pick_id.action_confirm()
            if self.pick_id.state != 'assigned':
                self.pick_id.action_assign()
                if self.pick_id.state != 'assigned':
                    raise UserError(_("Could not reserve all requested products. Please use the \'Mark as Todo\' button to handle the reservation manually."))
        for pack in self.pick_id.pack_operation_ids:
            if pack.product_qty > 0:
                pack.write({'qty_done': pack.product_qty})
            else:
                pack.unlink()
        self.pick_id.do_transfer()
        
        ###Edit###
        picking = self.pick_id
        print "picking>>>>>", picking, picking.sale_id.id
        
        sale = self.env['sale.order'].browse([picking.sale_id.id])
        
        if self.pick_id.auto_invoice_refund:
            return sale.action_invoice_create(final=True)
            #raise UserError("XXXX")
        ##########
        
        