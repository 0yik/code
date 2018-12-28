# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError

class StockAdjustment(models.Model):
    _name = 'stock.adjustment'
    _inherit = ['mail.thread']
    _order = 'id desc'
    _description = 'Stock Adjustment'

    name = fields.Char('Name', copy=False, readonly=True, default='New')
    location_id = fields.Many2one('stock.location', 'Inventoried Location')
    picking_id = fields.Many2one('stock.picking', 'Goods Receipt Note')
    picking_type_id = fields.Many2one('stock.picking.type', 'Picking Type')
    date = fields.Datetime('Inventory Date', default=fields.Datetime.now)
    account_date = fields.Date('Force Accounting Date')
    origin = fields.Char('Source Document')
    line_ids = fields.One2many('stock.adjustment.line', 'adjustment_id', string='Lines', copy=True)
    state = fields.Selection([('draft','Draft'),('done','Done'),('cancel','Cancelled')], string='Status', default='draft')
    inventory_id = fields.Many2one('stock.inventory', 'Inventory', copy=False)

    @api.model
    def default_get(self, fields):
        res = super(StockAdjustment, self).default_get(fields)
        picking_type_id = self.env['stock.picking.type'].search([('code','=','incoming')], limit=1)
        res.update({'picking_type_id': picking_type_id.id})
        return res

    @api.onchange('picking_id')
    def onchange_picking_id(self):
        data = []
        for line in self.picking_id.move_lines:
            vals = {}
            vals['product_id'] = line.product_id.id
            vals['uom_id'] = line.product_id.uom_id.id
            vals['location_id'] = line.location_dest_id.id
            vals['quantity'] = line.product_uom_qty
            data.append((0,0,vals))
        self.line_ids = data
        self.origin = self.picking_id.origin

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('stock.adjustment') or 'New'
        result = super(StockAdjustment, self).create(vals)
        return result

    @api.multi
    def button_validate(self):
        # create inventory adjustment
        vals = {}
        vals['name'] = self.name
        vals['location_id'] = self.location_id.id
        vals['filter'] = 'partial'
        vals['date'] = self.date
        vals['accounting_date'] = self.account_date
        line_data = []
        for line in self.line_ids:
            theoretical_qty = sum([x.qty for x in self._get_quants(line)])
            vals2 = {}
            vals2['product_id'] = line.product_id.id
            vals2['location_id'] = line.location_id.id
            vals2['theoretical_qty'] = theoretical_qty
            if line.new_quantity >= line.quantity:
                vals2['product_qty'] = theoretical_qty + (line.new_quantity - line.quantity)
            else:
                vals2['product_qty'] = theoretical_qty - (line.quantity - line.new_quantity)
            line_data.append((0,0,vals2))
        vals['line_ids'] = line_data
        record_id = self.env['stock.inventory'].create(vals)
        record_id.action_done()
        self.write({'state': 'done', 'inventory_id': record_id.id})

    @api.multi
    def _get_quants(self, line):
        return self.env['stock.quant'].search([
            ('company_id', '=', line.location_id.company_id.id),
            ('location_id', '=', line.location_id.id),
            ('lot_id', '=', False),
            ('product_id', '=', line.product_id.id),
            ('owner_id', '=', False),
            ('package_id', '=', False)])

    @api.multi
    def button_cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def action_view_inventory(self):
        action = self.env.ref('stock.action_inventory_form')
        action_dict = action.read()[0]
        action_dict['res_id'] = self.inventory_id.id
        action_dict['target'] = 'current'
        action_dict['view_mode'] = 'form'
        action_dict['views'] = [(False, 'form')]
        return action_dict

    @api.multi
    def unlink(self):
        for record in self:
            if record.state == 'done':
                raise UserError('Can not delete a record in done status')
        return super(StockAdjustment, self).unlink()

StockAdjustment()

class StockAdjustmentLine(models.Model):
    _name = 'stock.adjustment.line'
    _description = 'Stock Adjustment Line'

    adjustment_id = fields.Many2one('stock.adjustment', 'Adjustment')
    product_id = fields.Many2one('product.product', 'Product')
    uom_id = fields.Many2one('product.uom', 'UoM')
    location_id = fields.Many2one('stock.location', 'Location')
    quantity = fields.Float('Original Received Quantity')
    new_quantity = fields.Float('Adjusted Quantity')

StockAdjustmentLine()