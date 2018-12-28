from odoo import api, fields, models

class StockReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    @api.multi
    def _create_returns(self):
        new_picking, pick_type_id = super(StockReturnPicking, self)._create_returns()
        self.env['stock.picking'].browse(new_picking).name = 'GRN-' + self.env['stock.picking'].browse(new_picking).name.split('-')[1]
        return new_picking, pick_type_id

class stock_pack_operation(models.Model):
    _inherit = 'stock.pack.operation'

    remarks = fields.Char('Remarks')


class stock_picking(models.Model):
    _inherit = 'stock.picking'

    remarks = fields.Char('Remarks')

class stock_move(models.Model):
    _inherit = 'stock.move'

    remarks = fields.Char('Remarks')