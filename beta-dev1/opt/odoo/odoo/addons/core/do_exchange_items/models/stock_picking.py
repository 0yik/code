from odoo import fields, api, models, _


class delivery_order(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def open_do_exchange_wizard(self):
        do_exchange_item = self.env['do.exchange.item']
        product = []
        lot_visible = False
        for pack_operation_product_id in self.pack_operation_product_ids:
            pack_operation_product = {
                'product_id': pack_operation_product_id.product_id.id,
                'qty': pack_operation_product_id.qty_done
            }
            if pack_operation_product_id.pack_lot_ids:
                lots = []
                for pack_lot_id in pack_operation_product_id.pack_lot_ids:
                    pack_lot_ids = {'lot_id': pack_lot_id.lot_id.id}
                    lots.append((0, 0, pack_lot_ids))
                pack_operation_product.update({'pack_lot_ids': lots,'lot_visible':True})
            product.append((0, 0, pack_operation_product))

        do_exchange_id = do_exchange_item.create(
            { # 'product_do_line_ids': product, 
              'product_do_return_ids': product})

        # first fatch wizard view id
        view_id = self.env.ref('do_exchange_items.do_exchange_wizard_view', False)
        return {
            'name': _("Do Exchange Wizard"),
            'view_mode': 'form',
            'view_id': view_id.id,
            'view_type': 'form',
            'res_model': 'do.exchange.item',
            'res_id': do_exchange_id.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
