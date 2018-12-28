# -*- coding: utf-8 -*-
from openerp import api, fields, models

_STATES = [
    ('draft', 'RFQ'),
    ('sent', 'RFQ Sent'),
    ('to approve','To Approve'),
    ('purchase', 'Purchase Order'),
    ('done','Locked'),
    ('cancel', 'Cancelled')
]

class PurchaseMaterialRequest(models.Model):
    _name = 'purchase.material.request'
    _description = 'Purchase Material Request'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    @api.multi
    def _create_picking(self):
        StockPicking = self.env['stock.picking']
        for order in self:
            if any([ptype in ['product', 'consu'] for ptype in order.order_line.mapped('product_id.type')]):
                pickings = order.picking_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
                if not pickings:
                    res = order._prepare_picking()
                    picking = StockPicking.create(res)
                else:
                    picking = pickings[0]
                moves = order.order_line._create_stock_moves(picking)
                moves = moves.filtered(lambda x: x.state not in ('done', 'cancel')).action_confirm()
                seq = 0
                for move in sorted(moves, key=lambda move: move.date_expected):
                    seq += 5
                    move.sequence = seq
                moves.force_assign()
                picking.message_post_with_view('mail.message_origin_link',
                                               values={'self': picking, 'origin': order},
                                               subtype_id=self.env.ref('mail.mt_note').id)
        return True

    @api.model
    def _company_get(self):
        return self.env.user.company_id.id

    @api.model
    def _get_default_name(self):
        return self.env['ir.sequence'].next_by_code('purchase.material.request')

    @api.model
    def _default_picking_type(self):
        type_obj = self.env['stock.picking.type']
        company_id = self.env.context.get('company_id') or self.env.user.company_id.id
        types = type_obj.search([('code', '=', 'internal'), ('warehouse_id.company_id', '=', company_id)]).ids
        if not types:
            types = type_obj.search([('code', '=', 'internal'), ('warehouse_id', '=', False)]).ids
        return (types and types[0]) or False

    @api.multi
    @api.depends('name', 'origin', 'date_start', 'requested_by', 'assigned_to', 'description', 'company_id', 'line_ids',
                 'picking_type_id')
    def _compute_is_editable(self):
        for rec in self:
            if rec.state in ('to_approve', 'purchase', 'cancel'):
                rec.is_editable = False
            else:
                rec.is_editable = True

    @api.model
    def default_requested_by(self):
        if self._uid:
            return self._uid

    name = fields.Char('Request Reference', size=32, required=True, track_visibility='onchange', default=_get_default_name)
    origin = fields.Char('Source Document', size=32)
    date_start = fields.Date('Scheduled date', help="Date when the user initiated the request.",
                             default=fields.Date.context_today, track_visibility='onchange')
    requested_by = fields.Many2one('res.users', 'Requested by', required=True, track_visibility='onchange',default=default_requested_by)
    source_location = fields.Many2one('stock.location', 'Source Location')
    destination_location = fields.Many2one('stock.location', 'Destination Location')
    assigned_to = fields.Many2one('res.users', 'Approver', track_visibility='onchange')
    description = fields.Text('Description')
    company_id = fields.Many2one('res.company', 'Company', required=True, default=_company_get,
                                 track_visibility='onchange')
    line_ids = fields.One2many('purchase.material.request.line', 'request_id', 'Products to Purchase', readonly=False, copy=True,
                               track_visibility='onchange')
    state = fields.Selection(selection=_STATES, string='Status', track_visibility='onchange', required=True,
                             default='draft')
    is_editable = fields.Boolean(string="Is editable", compute="_compute_is_editable", readonly=True)
    picking_type_id = fields.Many2one('stock.picking.type', 'Picking Type',
                                      default=_default_picking_type)
    type_order = fields.Selection([('internal', 'Internal Order'), ('external', 'External Order')],
                                  string='Type of Order', default='internal')
    branch_id   = fields.Many2one('res.branch','Branch')

    @api.multi
    def copy(self, default=None):
        default = dict(default or {})
        self.ensure_one()
        default.update({'state': 'draft', 'name': self.env['ir.sequence'].next_by_code('purchase.material.request')})
        return super(PurchaseMaterialRequest, self).copy(default)

    @api.model
    def create(self, vals):
        if vals.get('assigned_to'):
            assigned_to = self.env['res.users'].browse(vals.get('assigned_to'))
            vals['message_follower_ids'] = False
        return super(PurchaseMaterialRequest, self).create(vals)

    @api.multi
    def write(self, vals):
        self.ensure_one()
        if vals.get('assigned_to'):
            assigned_to = self.env['res.users'].browse(vals.get('assigned_to'))
            vals['message_follower_ids'] = False
        res = super(PurchaseMaterialRequest, self).write(vals)
        return res

    @api.multi
    def button_draft(self):
        self.state = 'draft'
        return True

    @api.multi
    def button_approve(self):
        self.state = 'purchase'
        return True

    @api.multi
    def button_confirm(self):
        self.state = 'purchase'
        self.create_internal_stock_move();
        return True

    @api.multi
    def create_internal_stock_move(self):
        today = fields.Date.today()
        company_id = self.env.get('res.users').browse(self._uid).company_id.id
        picking_type_obj = self.env.get('stock.picking.type').search([('code', '=', 'internal'), ('warehouse_id.company_id', '=', company_id)], limit=1)
        stock_move_obj = self.env.get('stock.move')
        picking_vals = {
            'picking_type_id': self.picking_type_id.id or picking_type_obj.id,
            'date': today,
            'origin': self.name,
            'min_date': self.date_start,
            'location_id': self.source_location.id,
            'location_dest_id': self.destination_location.id,
            'branch_id'     : self.branch_id.id or False
        }
        picking = self.env.get('stock.picking').create(picking_vals)
        move_ids = []

        for line in self.line_ids:
            vals = {
                'name': line.product_id.name,
                'product_id': line.product_id.id,
                'product_uom': line.product_uom_id.id if line.product_uom_id else line.product_id.uom_id.id,
                'product_uom_qty': line.product_qty,
                'date': today,
                # 'brand_id': line.brand_id.ids,
                'date_expected': today,
                'location_id': self.source_location.id,
                'location_dest_id': self.destination_location.id,
                'picking_id': picking.id,
                'partner_id': False,
                'move_dest_id': False,
                'state': 'draft',
                'company_id': company_id,
                'picking_type_id': picking.picking_type_id.id,
                'procurement_id': False,
                'origin': self.name,
                'route_ids': picking.picking_type_id.warehouse_id and [
                    (6, 0, [x.id for x in picking.picking_type_id.warehouse_id.route_ids])] or [],
                'warehouse_id': picking.picking_type_id.warehouse_id.id,
                'branch_id' : line.request_id.branch_id.id or False,
            }

            move = stock_move_obj.create(vals)
            move_ids.append(move.id)
        todo_moves = stock_move_obj.browse(move_ids).action_confirm()
        todo_moves.force_assign()
        todo_moves.action_done()
        return True

    @api.multi
    def button_cancel(self):
        self.state = 'cancel'
        return True


PurchaseMaterialRequest()

class PurchaseMaterialRequestLine(models.Model):
    _name = "purchase.material.request.line"
    _order = "id desc"
    _description = "Purchase Material Request Line"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    @api.multi
    @api.depends('product_id', 'name', 'product_uom_id', 'product_qty', 'analytic_account_id', 'date_required',
                 'specifications')
    def _compute_is_editable(self):
        for rec in self:
            if rec.request_id.state in ('to approve', 'purchase', 'cancel'):
                rec.is_editable = False
            else:
                rec.is_editable = True

    @api.multi
    def _compute_supplier_id(self):
        for rec in self:
            if rec.product_id:
                for product_supplier in rec.product_id.seller_ids:
                    rec.supplier_id = product_supplier.name.id

    product_id = fields.Many2one('product.product', 'Product', domain=[('purchase_ok', '=', True)],
                                 track_visibility='onchange')
    # brand_id = fields.Many2many('product.brand', string="Brand")
    name = fields.Char('Description', size=256, track_visibility='onchange')
    product_uom_id = fields.Many2one('product.uom', 'Product Unit of Measure', track_visibility='onchange')
    product_qty = fields.Float('Quantity', track_visibility='onchange',
                               )
    request_id = fields.Many2one('purchase.material.request', 'Purchase Request', ondelete='cascade', readonly=True)
    company_id = fields.Many2one('res.company', related='request_id.company_id', string='Company', store=True,
                                 readonly=True)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', track_visibility='onchange')
    requested_by = fields.Many2one('res.users', related='request_id.requested_by', string='Requested by', store=True,
                                   readonly=True)
    assigned_to = fields.Many2one('res.users', related='request_id.assigned_to', string='Assigned to', store=True,
                                  readonly=True)
    date_start = fields.Date(related='request_id.date_start', string='Request Date', readonly=True, store=True)
    description = fields.Text(related='request_id.description', string='Description', readonly=True, store=True)
    origin = fields.Char(related='request_id.origin', size=32, string='Source Document', readonly=True, store=True)
    date_required = fields.Date(string='Request Date', required=True, track_visibility='onchange',
                                default=fields.Date.context_today)
    is_editable = fields.Boolean(string='Is editable', compute="_compute_is_editable", readonly=True)
    specifications = fields.Text(string='Specifications')
    request_state = fields.Selection(string='Request state', readonly=True, related='request_id.state',
                                     selection=_STATES, store=True)
    supplier_id = fields.Many2one('res.partner', string='Preferred supplier', compute="_compute_supplier_id")
    procurement_id = fields.Many2one('procurement.order', 'Procurement Order', readonly=True)

    @api.onchange('product_id', 'product_uom_id')
    def onchange_product_id(self):
        if self.product_id:
            name = self.product_id.name
            if self.product_id.code:
                name = '[%s] %s' % (name, self.product_id.code)
            if self.product_id.description_purchase:
                name += '\n' + self.product_id.description_purchase
            self.product_uom_id = self.product_id.uom_id.id
            self.product_qty = 1
            # self.brand_id = self.product_id.brand_ids.ids if self.product_id.brand_ids else False
            self.name = name

    @api.multi
    def button_approved(self):
        self.request_state = 'purchase'
        request_id = self.request_id.id
        req_exist = self.env['purchase.material.request.line'].search([('request_id', '=', request_id),
                                                              ('request_state', '=', 'to_approve')])
        if not req_exist:
            self.request_id.button_approved()
        return True

PurchaseMaterialRequestLine()
