from datetime import  datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class StockScrap(models.Model):
    _name = 'scrap.consumption.line'
    _order = 'id desc'

    def _get_default_scrap_location_id(self):
        return self.env.ref('scrap_daily_consumption.location_scrap_daily_consumption').id
        # return self.env['stock.location'].search([('scrap_location', '=', True)], limit=1).id

    def _get_default_location_id(self):
        return self.env.ref('stock.stock_location_stock', raise_if_not_found=False)

    name = fields.Char(
        'Reference',  default=lambda self: _('New'),
        copy=False, readonly=True, required=True,
        states={'done': [('readonly', True)]})
    origin = fields.Char(string='Source Document')
    product_id = fields.Many2one(
        'product.product', 'Product',
        required=True, states={'done': [('readonly', True)]})
    product_uom_id = fields.Many2one(
        'product.uom', 'Unit of Measure',
        required=True, states={'done': [('readonly', True)]})
    tracking = fields.Selection('Product Tracking', readonly=True, related="product_id.tracking")
    lot_id = fields.Many2one(
        'stock.production.lot', 'Lot',
        states={'done': [('readonly', True)]}, domain="[('product_id', '=', product_id)]")
    package_id = fields.Many2one(
        'stock.quant.package', 'Package',
        states={'done': [('readonly', True)]})
    owner_id = fields.Many2one('res.partner', 'Owner', states={'done': [('readonly', True)]})
    move_id = fields.Many2one('stock.move', 'Scrap Move', readonly=True)
    picking_id = fields.Many2one('stock.picking', 'Picking', states={'done': [('readonly', True)]})
    scrap_location_id = fields.Many2one(
        'stock.location', 'Scrap Location', default=False, related=False,
        domain="[('scrap_location', '=', True)]", states={'done': [('readonly', True)]})
    scrap_qty = fields.Float('Quantity', default=1.0, required=True, states={'done': [('readonly', True)]})
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done')], string='Status', default="draft")
    date_expected = fields.Datetime('Expected Date', default=fields.Datetime.now)

    @api.onchange('picking_id')
    def _onchange_picking_id(self):
        if self.picking_id:
            self.location_id = (self.picking_id.state == 'done') and self.picking_id.location_dest_id.id or self.picking_id.location_id.id

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id

    @api.model
    def create(self, vals):
        if 'name' not in vals or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('stock.scrap') or _('New')
        scrap = super(StockScrap, self).create(vals)
        # scrap.do_scrap()
        return scrap

    @api.multi
    def unlink(self):
        if 'done' in self.mapped('state'):
            raise UserError(_('You cannot delete a scrap which is done.'))
        return super(StockScrap, self).unlink()

    def _get_origin_moves(self):
        return self.picking_id and self.picking_id.move_lines.filtered(lambda x: x.product_id == self.product_id)

    @api.multi
    def do_scrap(self):
        for scrap in self:
            moves = scrap._get_origin_moves() or self.env['stock.move']
            move = self.env['stock.move'].create(scrap._prepare_move_values())
            quants = self.env['stock.quant'].quants_get_preferred_domain(
                move.product_qty, move,
                domain=[
                    ('qty', '>', 0),
                    ('lot_id', '=', self.lot_id.id),
                    ('package_id', '=', self.package_id.id)],
                preferred_domain_list=scrap._get_preferred_domain())
            if any([not x[0] for x in quants]):
                raise UserError(_('You cannot scrap a move without having available stock for %s. You can correct it with an inventory adjustment.') % move.product_id.name)
            self.env['stock.quant'].quants_reserve(quants, move)
            move.action_done()
            scrap.write({'move_id': move.id, 'state': 'done'})
            moves.recalculate_move_state()
        return True

    def _prepare_move_values(self):
        self.ensure_one()
        return {
            'name': self.name,
            'origin': self.origin or self.picking_id.name,
            'product_id': self.product_id.id,
            'product_uom': self.product_uom_id.id,
            'product_uom_qty': self.scrap_qty,
            'location_id': self.location_id.id,
            'scrapped': True,
            'location_dest_id': self.consumption_id.location_id.id,
            'restrict_lot_id': self.lot_id.id,
            'restrict_partner_id': self.owner_id.id,
            'picking_id': self.picking_id.id
        }

    def _get_preferred_domain(self):
        if not self.picking_id:
            return []
        if self.picking_id.state == 'done':
            preferred_domain = [('history_ids', 'in', self.picking_id.move_lines.filtered(lambda x: x.state == 'done')).ids]
            preferred_domain2 = [('history_ids', 'not in', self.picking_id.move_lines.filtered(lambda x: x.state == 'done')).ids]
            return [preferred_domain, preferred_domain2]
        else:
            preferred_domain = [('reservation_id', 'in', self.picking_id.move_lines.ids)]
            preferred_domain2 = [('reservation_id', '=', False)]
            preferred_domain3 = ['&', ('reservation_id', 'not in', self.picking_id.move_lines.ids), ('reservation_id', '!=', False)]
            return [preferred_domain, preferred_domain2, preferred_domain3]

    @api.multi
    def action_get_stock_picking(self):
        action = self.env.ref('stock.action_picking_tree_all').read([])[0]
        action['domain'] = [('id', '=', self.picking_id.id)]
        return action

    @api.multi
    def action_get_stock_move(self):
        action = self.env.ref('stock.stock_move_action').read([])[0]
        action['domain'] = [('id', '=', self.move_id.id)]
        return action

    @api.multi
    def action_done(self):
        return {'type': 'ir.actions.act_window_close'}

    def _get_list_location(self):
        ids = [('id','not in',[])]
        if self.warehouse_id:
            parent_location_id = self.env['stock.location'].search([('name','=',self.warehouse_id.code)],limit=1)
            ids = [('id','in',[self.env['stock.location'].search([('usage', '=', 'internal'),('location_id','=',parent_location_id)]).ids])]
        return ids

    consumption_id = fields.Many2one('stock.scrap.consumption','Daily Consumption')
    product_code = fields.Char('Product Code')
    description = fields.Char('Description')
    onhand_qty = fields.Float('Stock on Hand')
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse', help="Technical field depicting the warehouse to consider for the route selection on the next procurement (if any).")
    location_id = fields.Many2one('stock.location', 'Location',default=_get_default_location_id, domain=_get_list_location,required=True, states={'done': [('readonly', True)]})
    categ_id = fields.Many2one('product.category','Internal Category')
    scrap_price = fields.Float('Price')

    @api.onchange('warehouse_id')
    def onchange_warehouse_id(self):
        ids = [('id','not in',[])]
        if self.warehouse_id:
            parent_location_id = self.env['stock.location'].search([('name','=',self.warehouse_id.code)],limit=1)
            ids = [('id','in',[self.env['stock.location'].search([('usage', '=', 'internal'),('location_id','=',parent_location_id.id)]).ids])]
        return {'domain':{'location_id':ids}}

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id
            self.product_code = self.product_id.default_code
            self.description = self.product_id.description
            self.categ_id = self.product_id.categ_id.id
            self.scrap_price = self.product_id.lst_price * self.scrap_qty
            quant_ids = self.env['stock.quant'].search([('product_id','=',self.product_id.id),('location_id.usage','=','internal')])
            if quant_ids:
                total = sum([x.qty for x in quant_ids])
                self.onhand_qty = sum([x.qty for x in quant_ids])




class StockScrapConsumption(models.Model):
    _name = 'stock.scrap.consumption'
    _rec_name = 'name'

    def _get_default_stock(self):
        return self.env['account.journal'].search([('company_id', '=', self.env.user.company_id.id),
                                                   ('type', '=', 'general'), ('name', 'ilike', 'Stock Journal')],
                                                  limit=1).id

    def _get_default_scrap_location(self):
        return self.env.ref('scrap_daily_consumption.location_scrap_daily_consumption').id

    def _compute_picking(self):
        for order in self:
            order.move_count = len(order.scrap_ids.mapped('move_id'))
            order.account_move_count = len(self.env['account.move'].search([('consumption_id','=',self.id)]))

    name = fields.Char('Reference',  default=lambda self: _('New'), copy=False, readonly=True, required=True, states={'done': [('readonly', True)]})
    origin = fields.Char(string='Source Document')
    state = fields.Selection([('draft', 'Draft'),('confirm','Confirmed'),('done', 'Done')], string='Status', default="draft")
    date_expected = fields.Datetime('Expected Date', default=fields.Datetime.now)
    scrap_ids = fields.One2many('scrap.consumption.line','consumption_id',string='Scrap')
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse', help="Technical field depicting the warehouse to consider for the route selection on the next procurement (if any).")
    asset_id = fields.Many2one('account.asset.asset', string="Assets")
    journal_id = fields.Many2one('account.journal','Journal Type',default=_get_default_stock)
    company_id = fields.Many2one('res.company', 'Company',default=lambda self: self.env['res.company']._company_default_get('stock.move'),index=True, required=True)
    location_id = fields.Many2one('stock.location', default=_get_default_scrap_location)
    move_count = fields.Integer(compute='_compute_picking', string='Receptions', default=0)
    account_move_count = fields.Integer(compute='_compute_picking', string='Account Move Count', default=0)

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
            'domain' : [('id','in',self.scrap_ids.mapped('move_id').ids)]
        }

    def action_view_account_move(self):
        formview_ref = self.env.ref('account.view_move_form', False)
        treeview_ref = self.env.ref('account.view_move_tree', False)
        return {
            'name': _('Stock Journal'),
            'view_mode': 'tree,form',
            'view_type': 'form',
            'views': [(treeview_ref and treeview_ref.id or False, 'tree'),
                      (formview_ref and formview_ref.id or False, 'form')],
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'domain' : [('id','in', self.env['account.move'].search([('consumption_id','=',self.id)]).ids )]
        }


    @api.model
    def create(self,vals):
        if 'name' not in vals or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('stock.scrap.consumption') or _('New')
        return super(StockScrapConsumption,self).create(vals)

    @api.multi
    def action_confirm_scrap(self):
        for record in self:
            record.write({'state':'confirm'})
        return True

    @api.multi
    def action_done_scrap(self):
        for record in self:
            for scrap_line in record.scrap_ids:
                line_list = []
                debit_line_vals = {
                    'name': scrap_line.name or '/',
                    'debit': scrap_line.scrap_price,
                    'credit': 0.0,
                    'account_id': scrap_line.product_id.categ_id.property_account_expense_categ_id.id,
                }
                credit_line_vals = {
                    'name': scrap_line.name or '/',
                    'credit': scrap_line.scrap_price,
                    'debit': 0.0,
                    'account_id': scrap_line.product_id.categ_id.property_account_income_categ_id.id
                }
                line_list.append((0, 0, credit_line_vals))
                line_list.append((0, 0, debit_line_vals))
                move = self.env['account.move'].create({
                    'name': '/',
                    'consumption_id' : self.id,
                    'journal_id': record.journal_id.id,
                    'date': record.date_expected or datetime.now().date(),
                    'line_ids': line_list,
                    'ref': record.name
                })
                move.post()
            record.scrap_ids.do_scrap()
            record.write({'state':'done'})
        return True

class AccountMove(models.Model):
    _inherit = 'account.move'

    consumption_id = fields.Many2one('stock.scrap.consumption','Daily Consumption')
