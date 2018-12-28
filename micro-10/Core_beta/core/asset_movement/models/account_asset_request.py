

import datetime
from odoo import api, fields, models


class AccountAssetRequest(models.Model):
    _name = 'account.asset.request'

    @api.multi
    @api.depends('requester_id')
    def _get_assets(self):
        for rec in self:
            requesters_assets_id = []
            if rec.requester_id:
                requesters_assets_id = self.env['account.asset.asset'].sudo().search([('owner_id', '=', rec.requester_id.id)]).ids
            rec.requesters_assets_id = requesters_assets_id

    name = fields.Char(string="Reference", required=True, copy=False, readonly=True,
                       default='New')
    state = fields.Selection(
        [('draft', 'Draft'), ('waiting_approval', 'Waiting for Approval'), ('approved', 'Approved '), ('rejected', 'Rejected'),
         ('cancel', 'Cancelled')], 'Status', default='draft')
    requester_id = fields.Many2one('res.users', 'Requester')
    current_user_id = fields.Many2one('res.users', 'Assets Currently Holding')
    asset_category_id = fields.Many2one('account.asset.category', 'Requesting Asset')
    asset_id = fields.Many2one('account.asset.asset', 'Asset')
    requesters_assets_id = fields.Many2many('account.asset.asset', compute='_get_assets', string='Assets Currently Holding', store=True)
    date = fields.Date('Date')
    reason = fields.Text('Reason')
    date_transferrd = fields.Date('Transferred Date')
    asset_history_ids = fields.One2many('account.asset.history', 'request_id', string='Movement History')
    is_asset = fields.Boolean('Is there Asset', default=False)

    current_assets_location = fields.Many2one('stock.location', string='Current Assets Location')
    new_assets_location = fields.Many2one('stock.location', string='New Assets Location')

    @api.onchange('current_assets_location')
    def onchange_current_assets_location(self):
        if self.current_assets_location:
            self.new_assets_location = self.current_assets_location

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('account.asset.request') or 'New'
            result = super(AccountAssetRequest, self).create(vals)
        return result

    @api.multi
    def write(self, vals):
        result = super(AccountAssetRequest, self).write(vals)
        if vals.get('asset_id'):
            self.current_user_id = self.asset_id.owner_id.id
        return result


    @api.multi
    def submit_for_approval(self):
        self.state = 'waiting_approval'

    @api.multi
    def reject_request(self):
        self.state = 'rejected'

    @api.multi
    def approve_request(self):
        self.state = 'approved'
        self.date_transferrd = datetime.date.today()
        self.asset_id.write({'owner_id': self.requester_id.id, 'location_id':self.new_assets_location.id})

    @api.onchange('asset_id')
    def asset_onchange(self):
        self.current_user_id = self.asset_id.owner_id.id
        self.current_assets_location = self.asset_id.location_id.id
        if self.asset_id:
            self.is_asset = True
        else:
            self.is_asset = False

    @api.multi
    def cancel_request(self):
        self.state = 'cancel'

    @api.onchange('requester_id')
    def onchange_requester(self):
        domain=[]
        if self.requester_id:
            req_asset_ids = self.env['account.asset.asset'].search(
            [('owner_id', '=', self.requester_id.id)])
            return {'domain': {'asset_id': [('id', 'in', req_asset_ids and req_asset_ids.ids or [])]}}
        else:
            req_asset_ids = self.env['account.asset.asset'].search([])
            return {'domain':
                 {'asset_id': [('id', 'in', req_asset_ids and req_asset_ids.ids or [])]}}






