from odoo import api, fields, models, _
from odoo.exceptions import Warning
from odoo.addons import decimal_precision as dp
from odoo.addons.stock_landed_costs.models import product


class LandedCost(models.TransientModel):

    _name = 'landed.cost.wizard'

    @api.model
    def _get_purchase_id(self):
        return self._context['active_id']

    purchase_id = fields.Many2one('purchase.order', 'Purchase Order', default=_get_purchase_id)
    date = fields.Date('Tanggal', default=fields.Date.context_today, required=True, )
    picking_ids = fields.Many2many('stock.picking', string='Pengiriman')
    account_journal_id = fields.Many2one('account.journal', 'Journal Account', required=True)
    cost_lines = fields.One2many('stock.landed.cost.lines.wizard', 'cost_id', 'Cost Lines')

    @api.onchange('purchase_id')
    def onchange_purchase_id(self):
        picking_rec = self.env['stock.picking'].search([('origin','=',self.purchase_id.name)])
        if picking_rec:
            return {'domain':{'picking_ids':[('state','=','done'),('id','in',picking_rec.ids)]}}
        

    @api.multi
    def save_landed_cost(self):
        landed_cost_obj = self.env['stock.landed.cost']
        landed_cost_rec = landed_cost_obj.create({'purchase_id': self._context['active_id'],
                                'date': self.date,
                                'picking_ids': [(6, 0, self.picking_ids.ids)],
                                'account_journal_id': self.account_journal_id.id,})
        lc_line_obj = self.env['stock.landed.cost.lines']
        for line in self.cost_lines:
            lc_line_obj.create({'cost_id': landed_cost_rec.id,
                                'name': line.product_id.name,
                                'product_id': line.product_id.id,
                                'price_unit': line.price_unit,
                                'split_method': line.split_method,
                                'account_id': line.account_id.id,})


class LandedCostLine(models.TransientModel):
    _name = 'stock.landed.cost.lines.wizard'

    name = fields.Char('Deskripsi')
    cost_id = fields.Many2one('landed.cost.wizard', 'Landed Cost')
    product_id = fields.Many2one('product.product', 'produk/Biaya', required=True)
    price_unit = fields.Float('Harga', digits=dp.get_precision('Product Price'), required=True)
    split_method = fields.Selection(product.SPLIT_METHOD, string='Metode Pembagian', required=True)
    account_id = fields.Many2one('account.account', 'Nomor Account', domain=[('deprecated', '=', False)])

    @api.onchange('product_id')
    def onchange_product_id(self):
        if not self.product_id:
            self.quantity = 0.0
        self.name = self.product_id.name or ''
        self.split_method = self.product_id.split_method or 'equal'
        self.price_unit = self.product_id.standard_price or 0.0
        self.account_id = self.product_id.property_account_expense_id.id or self.product_id.categ_id.property_account_expense_categ_id.id

