# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from dateutil.relativedelta import relativedelta
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    stock_standard_id = fields.Many2one('stock.standard')

    def default_get(self, fields):
        res = super(StockPicking, self).default_get(fields)
        StockMove = self.env['stock.move']
        context = self._context or {}
        active_model = context.get('active_model', False)
        active_ids = context.get('active_ids', False)
        ids = []
        if (active_model or active_ids) and active_model == 'stock.standard':
            StockStandard = self.env[active_model].browse(active_ids)
            res.update({
                'picking_type_id': StockStandard.picking_type_id and StockStandard.picking_type_id.id or False,
                'location_dest_id': StockStandard.location_id and StockStandard.location_id.id or False,
                'state': 'draft',
                'stock_standard_id': StockStandard.id,
            })
            res['move_lines'] = [[0, 0, {
                        'product_id' : line.product_id.id,
                        'code' : line.product_id_code,
                        'product_uom_qty' : line.to_do_amount,
                        'product_uom' : line.product_id.uom_id.id,
                        'location_id' : line.warehouse_id and line.warehouse_id.id or False,
                        'location_dest_id': StockStandard.location_id and StockStandard.location_id.id or False,
                        'scrapped' : True,
                        'state' : 'draft',
                        'date_expected' : datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT),
                }] for line in StockStandard.stock_standard_line]
        #     for line in StockStandard.stock_standard_line:
        #         vals = {
        #                 'product_id' : line.product_id.id,
        #                 'code' : line.product_id_code,
        #                 'product_uom_qty' : line.to_do_amount,
        #                 'product_uom' : line.product_id.uom_id.id,
        #                 'stock_standard_id' : StockStandard.id,
        #                 'location_id' : line.warehouse_id and line.warehouse_id.id or False,
        #                 'location_dest_id': StockStandard.location_id and StockStandard.location_id.id or False,
        #         }
        #         id = [0, 0, vals]
        #         ids.append(id)
        # if ids:
        #     res['move_lines'] = ids
        return res

class stock_standard(models.Model):
    _name = 'stock.standard'

    def _compute_picking(self):
        for order in self:
            order.picking_count = len(order.picking_ids)
            order.move_count = len(order.picking_ids.mapped('move_lines'))

    name = fields.Char(string='Name')
    location_id = fields.Many2one('stock.location',string="Location")

    responsible_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('done', 'Done'),
    ], string='Order Status', readonly=True, copy=False, store=True, default='draft')

    stock_standard_line = fields.One2many('stock.standard.line', 'stock_standard_id', string='Stock Standard Lines', copy=True)
    notes = fields.Text('Notes')
    total_to_do_amount = fields.Float(compute='total_to_do')
    picking_type_id = fields.Many2one('stock.picking.type', required=True)

    @api.depends('stock_standard_line')
    @api.multi
    def total_to_do(self):
        for rec in self:
            if rec.stock_standard_line:
                rec.total_to_do_amount = sum(rec.stock_standard_line.mapped('to_do_amount'))

    picking_count = fields.Integer(compute='_compute_picking', string='Receptions', default=0)
    picking_ids = fields.One2many('stock.picking', 'stock_standard_id', string='Operations')
    move_count = fields.Integer(compute='_compute_picking', string='Receptions', default=0)


    @api.multi
    def action_confirm(self):
        self.write({'state': 'confirm'})

    @api.multi
    def action_button_done(self):
        self.write({'state': 'done'})

    def action_view_picking(self):
        return {
            'name': _('Stock Operation'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            # 'view_id': self.env.ref('stock.view_picking_form').id,
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'domain' : [('id','in',self.picking_ids.ids)]
        }

    def action_view_move(self):
        formview_ref = self.env.ref('stock.view_move_form', False)
        treeview_ref = self.env.ref('stock.view_move_tree', False)
        return {
            'name': _('Stock Move'),
            'view_mode': 'tree,form',
            'view_type': 'form',
            'views': [(treeview_ref and treeview_ref.id or False, 'tree'),
                      (formview_ref and formview_ref.id or False, 'form')],
            'res_model': 'stock.move',
            'type': 'ir.actions.act_window',
            'domain' : [('id','in',self.picking_ids.mapped('move_lines').ids)]
        }

class stockt_standard_line(models.Model):
    _name = 'stock.standard.line'

    stock_standard_id = fields.Many2one('stock.standard', string='Stock Standard', required=True, ondelete='cascade', index=True,
                               copy=False)
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)],
                                change_default=True, required=True)
    product_id_code = fields.Char('Product Code',related='product_id.default_code')
    investment_standard_amount = fields.Float(string='Investment standard', compute="compute_qty_of_product")
    stock_buffer_amount = fields.Float(string='Stock Buffet',compute="compute_qty_of_product")
    total_sold_a_month = fields.Integer('Total Sold a Month',compute="compute_qty_of_product")
    stock_current_shop_amount = fields.Float('Stock Current Shop',compute="compute_qty_of_product")
    warehouse_id = fields.Many2one('stock.location', string='Warehouse')
    stock_warehouse_amount = fields.Float('Stock warehouse',compute="compute_stock_warehouse")
    to_do_amount = fields.Float('To do', compute="compute_qty_of_product")

    @api.depends('warehouse_id', 'product_id')
    @api.multi
    def compute_stock_warehouse(self):
        for rec in self:
            stock_qty_onhand_warehouse = rec.env['stock.quant'].search([
                ('product_id', '=', rec.product_id.id),
                ('location_id', '=', rec.warehouse_id.id),
            ])
            if stock_qty_onhand_warehouse:
                rec.stock_warehouse_amount = sum(stock_qty_onhand_warehouse.mapped('qty'))

    @api.depends('stock_standard_id.location_id','product_id')
    @api.multi
    def compute_qty_of_product(self):
        for rec in self:
            if rec.stock_standard_id.location_id and rec.product_id:
                reordering_rules_matched = rec.env['stock.warehouse.orderpoint'].search([
                    ('product_id','=',rec.product_id.id),
                    ('location_id','=',rec.stock_standard_id.location_id.id),
                ])
                if reordering_rules_matched:
                    rec.investment_standard_amount = sum(reordering_rules_matched.mapped('product_min_qty'))

                stock_buffer_matched = rec.env['stock.buffer.line'].search([
                    ('product_id', '=', rec.product_id.id),
                    ('stock_buffer_id.location_id', '=', rec.stock_standard_id.location_id.id),
                ])
                if stock_buffer_matched:
                    rec.stock_buffer_amount = sum(stock_buffer_matched.mapped('stock_buffer_amount'))

                stock_qty_onhand_current_shop = rec.env['stock.quant'].search([
                    ('product_id', '=', rec.product_id.id),
                    ('location_id', '=', rec.stock_standard_id.location_id.id),
                ])
                if stock_qty_onhand_current_shop:
                    rec.stock_current_shop_amount = sum(stock_qty_onhand_current_shop.mapped('qty'))


                today = datetime.now()
                start_date_current_month = today.strftime("%Y-%m-1")
                # start_date_current_month = datetime.strptime(start_date_current_month, DEFAULT_SERVER_DATE_FORMAT)
                next_month = today + relativedelta(months=1)
                next_month_string = next_month.strftime("%Y-%m-1")
                # next_month_date = datetime.strptime(next_month_string, DEFAULT_SERVER_DATE_FORMAT)
                pos_orders = self.env['pos.order.line'].search([
                    ('order_id.date_order','>=',start_date_current_month),
                    ('order_id.date_order','<',next_month_string),
                    ('product_id','=',rec.product_id.id),
                    ('order_id.location_id','=',rec.stock_standard_id.location_id.id),
                                                                ])
                if pos_orders:
                    rec.total_sold_a_month = sum(pos_orders.mapped('qty'))
                rec.to_do_amount = rec.investment_standard_amount - rec.stock_current_shop_amount + rec.stock_buffer_amount