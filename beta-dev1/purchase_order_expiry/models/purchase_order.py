from odoo import models, fields, api

class purchase_order(models.Model):
    _inherit = 'purchase.order'

    expiry_date     = fields.Date('Expire Date',default=fields.Date.today())

    @api.multi
    def checking_expiry_po(self):
        purchase_ids = self.env['purchase.order'].search([]).filtered(lambda po: fields.Date.today() > po.expiry_date )
        for record in purchase_ids:
            if record.picking_ids:
                for do in record.picking_ids.filtered(lambda s: s.state not in ('done','cancel')):
                    if not do.pack_operation_product_ids:
                        do.write({'state': 'cancel'})
                        if len(record.picking_ids.ids) == 1:
                            record.write({'state': 'cancel'})
                    else:
                        if all(l.qty_done == 0 for l in do.pack_operation_product_ids):
                            do.write({'state': 'cancel'})
                            if len(record.picking_ids.ids) == 1:
                                record.write({'state': 'cancel'})
                        else:
                            operations_to_delete = do.pack_operation_ids.filtered(lambda o: o.qty_done <= 0)
                            for pack in do.pack_operation_ids - operations_to_delete:
                                pack.product_qty = pack.qty_done
                            operations_to_delete.unlink()
                            do.do_transfer()
                            new_do = record.picking_ids - do
                            if new_do:
                                new_do.write({'state':'cancel'})
                            # if cancel_backorder:
                            #     backorder_pick = self.env['stock.picking'].search(
                            #         [('backorder_id', '=', self.pick_id.id)])
                            #     backorder_pick.action_cancel()
                            #     self.pick_id.message_post(
                            #         body=_("Back order <em>%s</em> <b>cancelled</b>.") % (backorder_pick.name))
            else:
                record.write({'state': 'cancel'})