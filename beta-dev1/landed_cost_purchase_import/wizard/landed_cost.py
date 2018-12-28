# coding=utf-8
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.addons.stock_landed_costs.models import product

class LandedCost(models.TransientModel):
    _name = 'landed.cost.purchase'

    @api.multi
    @api.depends('picking_ids')
    def _compute_purchase_order_name(self):
        for rec in self:
            rec.purchase_order_name = self.env['purchase.order'].search([('id','=',self._context.get('active_id'))]).name
            print ">>>>>>>>>>>",rec.purchase_order_name

    date = fields.Date(
        'Date', default=fields.Date.context_today,
        copy=False, required=True, track_visibility='onchange')
    account_journal_id = fields.Many2one('account.journal',string='Journal Account')
    picking_ids = fields.Many2many('stock.picking', string='Pengiriman')
    attachment = fields.Binary('Attachment')
    cost_lines = fields.One2many('stock.landed.cost.lines1', 'cost_id', 'Cost Lines', copy=True)
    purchase_order_name = fields.Char(string='Purchase Order Name', compute='_compute_purchase_order_name')

    def quick_add_landed_costs(self):
        landed_costs_obj = self.env['stock.landed.cost']
        purchase_order = self.env[self._context.get('active_model')].search([('id','=',self._context.get('active_id'))])
        vals = {
            'date' : self.date,
            'account_journal_id' : self.account_journal_id.id,
            'picking_ids': [(6, 0, self.picking_ids.ids)],
            'cost_lines' : [(0, 0, {'name': p.name, 'product_id': p.product_id.id, 'price_unit': p.price_unit, 'split_method': p.split_method, 'account_id' : p.account_id.id, 'cost_id' : self.id}) for  p in self.cost_lines],
            'source_reference' : purchase_order.name,
            'attachment': self.attachment,
        }
        landed_costs_obj.create(vals)

        return True


class LandedCostLine(models.TransientModel):
    _name = 'stock.landed.cost.lines1'
    _description = 'Stock Landed Cost Lines'

    name = fields.Char('Description')
    cost_id = fields.Many2one(
        'landed.cost.purchase', 'Landed Cost')
    product_id = fields.Many2one('product.product', 'Product', required=True)
    price_unit = fields.Float('Cost', digits=dp.get_precision('Product Price'), required=True)
    split_method = fields.Selection(product.SPLIT_METHOD, string='Split Method', required=True)
    account_id = fields.Many2one('account.account', 'Account', domain=[('deprecated', '=', False)])

    @api.onchange('product_id')
    def onchange_product_id(self):
        if not self.product_id:
            self.quantity = 0.0
        self.name = self.product_id.name or ''
        self.split_method = self.product_id.split_method or 'equal'
        self.price_unit = self.product_id.standard_price or 0.0
        self.account_id = self.product_id.property_account_expense_id.id or self.product_id.categ_id.property_account_expense_categ_id.id