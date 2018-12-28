from odoo import api, fields, models
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    _rec_name = 'name'

PurchaseOrder()

class StockScrap(models.Model):
    _name = 'stock.scrap.assets'
    _inherit = 'stock.scrap'

    def _get_po_number(self):
        purchase_obj = self.env['purchase.order']
        purchase_ids = purchase_obj.search([('state','=','purchase')])
        final_list = []
        for purchase in purchase_ids:
            deliver_ids = self.env['stock.picking'].search([('origin','=',purchase.name)])
            for deliver in deliver_ids:
                if deliver.state == 'done':
                    final_list.append(purchase.id)
        return [('id','in',final_list)]

    def _get_default_scrap_location_id(self):
        return self.env.ref('scrap_fixed_asset.location_scrap_fixed_assets', raise_if_not_found=False)

    def _get_default_stock(self):
        return self.env['account.journal'].search([('company_id','=',self.env.user.company_id.id),
                                                      ('type', '=', 'general'),('name','ilike','Stock Journal')], limit=1).id

    def _compute_picking(self):
        for order in self:
            order.account_move_count = len(self.env['account.move'].search([('scrap_asset_id','=',self.id)]))

    state = fields.Selection([('draft', 'Draft'),('confirm','Confirmed'),('done', 'Done')], string='Status', default="draft")
    scrap_location_id = fields.Many2one('stock.location', 'Scrap Location', default=_get_default_scrap_location_id, domain="[('scrap_location', '=', True)]", states={'done': [('readonly', True)]})
    scrap_price = fields.Float('Price')
    po_ids = fields.Many2one('purchase.order',string='PO Number',domain=_get_po_number,required=True)
    journal_id = fields.Many2one('account.journal', 'Journal Type', default=_get_default_stock)
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company']._company_default_get('stock.move'),
                                 index=True, required=True)
    account_move_count = fields.Integer(compute='_compute_picking', string='Account Move Count', default=0)

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
            'domain' : [('id','in', self.env['account.move'].search([('scrap_asset_id','=',self.id)]).ids )]
        }

    @api.model
    def create(self, vals):
        print "SSSSSSSSs",vals
        if 'name' not in vals or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('stock.scrap.assets') or _('New')
        res = super(StockScrap, self).create(vals)
        return res

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id and self.po_ids:
            for line in self.po_ids.order_line:
                if line.product_id == self.product_id:
                    asset_ids = self.env['stock.scrap.assets'].search([('po_ids','=',self.po_ids.id),('state','=','done')])
                    if asset_ids:
                        total_qty = 0
                        for aset_id in asset_ids:
                            total_qty += aset_id.scrap_qty
                        if line.product_qty > total_qty:
                            self.scrap_qty = line.product_qty - total_qty
                            self.product_uom_id = line.product_uom.id
                            self.location_id = self.po_ids.picking_type_id.default_location_dest_id.id
                            self.scrap_price = line.product_qty * line.price_unit
                        else:
                            self.scrap_qty = 0
                            raise UserError(_('All Quantity is scrap from the purchase order for product %s.') % self.product_id.name)
                    else:
                        self.scrap_qty = line.product_qty
                        self.product_uom_id = line.product_uom.id
                        self.location_id = self.po_ids.picking_type_id.default_location_dest_id.id
                        self.scrap_price = line.product_qty * line.price_unit

    @api.onchange('scrap_qty')
    def onchange_scrap_qty(self):
        if self.product_id and self.po_ids:
            for line in self.po_ids.order_line:
                total_qty = 0
                asset_ids = self.env['stock.scrap.assets'].search([('po_ids','=',self.po_ids.id),('state','=','done')])
                if asset_ids:
                    for aset_id in asset_ids:
                        total_qty += aset_id.scrap_qty
                if self.scrap_qty > line.product_qty:
                    raise UserError(_('%s Quantity is left for scrap from the purchase order for : %s.') % (line.product_qty - total_qty ,self.product_id.name))
                elif self.scrap_qty <= line.product_qty:
                    self.scrap_price = self.scrap_qty * line.price_unit 
                    self.product_uom_id = line.product_uom.id
                    self.location_id = self.po_ids.picking_type_id.default_location_dest_id.id
                else:
                    self.scrap_qty = 0
                    raise UserError(_('%s Quantity is left for scrap from the purchase order for : %s.') % (self.scrap_qty ,self.product_id.name))

    @api.onchange('po_ids')
    def onchange_po_ids(self):
        if self.po_ids:
            product_ids = []
            for line in self.po_ids.order_line:
                product_ids.append(line.product_id.id)
            return {'domain':{'product_id':[('id','in',product_ids)]}}

    @api.multi
    def action_confirm_scrap_asset(self):
        for record in self:
            record.write({'state':'confirm'})
        return True

    @api.multi
    def action_done_scrap_asset(self):
        for record in self:
            record.write({'state':'done'})
            record.do_account_move()
            record.do_scrap()
        return True

    @api.multi
    def do_account_move(self):
        for rec in self:
            line_list = []
            debit_line_vals = {
                'name': rec.name or '/',
                'debit': rec.scrap_price,
                'credit': 0.0,
                'account_id': rec.product_id.categ_id.property_account_expense_categ_id.id,
            }
            credit_line_vals = {
                'name': rec.name or '/',
                'credit': rec.scrap_price,
                'debit': 0.0,
                'account_id': rec.product_id.categ_id.property_account_income_categ_id.id
            }
            line_list.append((0, 0, credit_line_vals))
            line_list.append((0, 0, debit_line_vals))
            move = self.env['account.move'].create({
                'name': '/',
                'scrap_asset_id': self.id,
                'journal_id': rec.journal_id.id,
                'date': rec.date_expected or datetime.now().date(),
                'line_ids': line_list,
                'ref': rec.name,

            })
            move.post()

    @api.multi
    def do_scrap(self):
        for scrap in self:
            if scrap.state == 'done':
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

    @api.multi
    def action_get_stock_assets(self):
        action = self.env.ref('account_asset.action_account_asset_asset_form').read([])[0]
        action['domain'] = [('scrap_asset_id', '=', self.id)]
        return action

StockScrap()

class AccountassetAsset(models.Model):
    _inherit = 'account.asset.asset'

    def _get_domain_list_assets(self):
        final_list = []
        assets_ids = []
        final_list = self.env['stock.scrap.assets'].search([]).ids
        for default_obj in final_list:
            default_id = self.env['stock.scrap.assets'].browse(default_obj)
            assets_ids = self.search([('scrap_asset_id','=',default_id.id),('code','=',default_id.product_id.code)])
            if assets_ids and len(assets_ids) >= default_id.scrap_qty:
                final_list.remove(default_id.id)
        return [('id','in',final_list)]

    scrap_asset_id = fields.Many2one('stock.scrap.assets','Scrap Fixed Asset Number', domain=_get_domain_list_assets)


    @api.onchange('scrap_asset_id')
    def onchange_scrap_asset_id(self):
        final_list = []
        assets_ids = []
        name = ''
        if self and self.scrap_asset_id:
            name = self.scrap_asset_id.name
            assets_ids = self.search([('scrap_asset_id','=',self.scrap_asset_id.id),('code','=',self.scrap_asset_id.product_id.code)]).ids
            if assets_ids and len(assets_ids) >= self.scrap_asset_id.scrap_qty:
                self.scrap_asset_id = False
                raise UserError(_('All Product already converted scrap of %s.') % name)
            else:
                self.product_id = self.scrap_asset_id.product_id
                self.code = self.product_id.default_code
                self.name = self.product_id.name
                self.value = self.scrap_asset_id.scrap_price / self.scrap_asset_id.scrap_qty


class AccountMove(models.Model):
    _inherit = 'account.move'

    scrap_asset_id = fields.Many2one('stock.scrap.assets','Scrap Fixed Asset')