from odoo import fields, models, api, _
from odoo.exceptions import UserError


class do_exchange_items(models.Model):
    _name = 'do.exchange.item'

    product_do_line_ids = fields.One2many('product.exchange', 'do_exchange_id', string='Product to Exchange')
    product_do_return_ids = fields.One2many('product.return', 'do_return_id', string='Product to Return')
    return_location_id = fields.Many2one('stock.location', string='Return Location')
    exchange_location_id = fields.Many2one('stock.location', string='Exchange Location')

    @api.multi
    def do_exchange_item(self):
        active_id = self._context.get('active_ids')
        stock_picking_id = self.env['stock.picking'].browse(active_id)
        
        if not self.return_location_id and not self.exchange_location_id:
            raise UserError(_("Please select return location or exchange location."))
        
        picking_type_id = self.env.ref('stock.picking_type_in')
        
        if self.return_location_id:
            line_return = []
            for return_line in self.product_do_return_ids:
                name = return_line.product_id.name_get()[0][1]
                if return_line.product_id.description_sale:
                    name += '\n' + product.description_sale
                line_return.append((0, 0, { 'product_id': return_line.product_id.id,
                                        'product_uom_qty': return_line.qty,
                                        'location_id': stock_picking_id.location_dest_id.id,
                                        'location_dest_id': self.return_location_id.id,
                                        'product_uom': return_line.product_id.uom_id.id,
                                        'name': name,
                                        }))
            return_default = {
                'location_id': self.exchange_location_id.id,
                'location_dest_id': stock_picking_id.location_dest_id.id,
                'move_lines': line_return,
                'origin': stock_picking_id.name,
                'picking_type_id': picking_type_id and picking_type_id.id or False
            }
            return_picking_id = stock_picking_id.copy(default=return_default)
            # get return_picking and change the source and destination location
            
            ## commented code to fix bug by previous developer
            #return_picking_id.write(
             #   {'location_id': stock_picking_id.location_dest_id.id, 'location_dest_id': self.return_location_id.id})
        if self.exchange_location_id:
            # updating deffault value for exchange
            line_ex = []
            for ex_line in self.product_do_line_ids:
                name = ex_line.product_id.name_get()[0][1]
                if ex_line.product_id.description_sale:
                    name += '\n' + product.description_sale
                line_ex.append((0, 0, { 'product_id': ex_line.product_id.id,
                                        'product_uom_qty': ex_line.qty,
                                        'location_id': self.exchange_location_id.id,
                                        'location_dest_id': stock_picking_id.location_dest_id.id,
                                        'product_uom': ex_line.product_id.uom_id.id,
                                        'name': name,
                                        }))
            # get exchnage_picking and change the source and destination location
            ex_default = {
                'location_id': self.exchange_location_id.id,
                'location_dest_id': stock_picking_id.location_dest_id.id,
                'move_lines': line_ex,
                'origin': stock_picking_id.name,
            }
            exchange_picking_id = stock_picking_id.copy(default=ex_default)
            # get exchnage_picking and change the source and destination location
            ## commented code to fix bug by previous developer
            #exchange_picking_id.write(
            #    {'location_id': self.exchange_location_id.id, 'location_dest_id': stock_picking_id.location_dest_id.id})
        return True


class product_Exchange(models.Model):
    _name = 'product.exchange'

    product_id = fields.Many2one('product.product', string='Product')
    qty = fields.Float(string='Quantity')
    do_exchange_id = fields.Many2one('do.exchange.item', string='Do Exchange')
    pack_lot_ids = fields.Many2many('stock.pack.operation.lot', 'exchange_id',string = 'Lots/Serial Numbers Used')
    lot_visible = fields.Boolean('Lots Visible',default=False)


class product_return(models.Model):
    _name = 'product.return'

    product_id = fields.Many2one('product.product', string='Product')
    qty = fields.Float(string='Quantity')
    do_return_id = fields.Many2one('do.exchange.item', string='Do Return')
    pack_lot_ids = fields.Many2many('stock.pack.operation.lot', 'return_id',string = 'Lots/Serial Numbers Used')
    lot_visible = fields.Boolean('Lots Visible',default=False)

class stock_pack_operation_lot(models.Model):
    _inherit = 'stock.pack.operation.lot'

    return_id = fields.Many2one('product.return', string='Product Return')
    exchange_id = fields.Many2one('product.exchange', string='Product Exchange')
