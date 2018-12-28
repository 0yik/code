

import datetime
from odoo import api, fields, models


class AccountAssetRequest(models.Model):
    _name = 'account.asset.request'

    name = fields.Char(string="Reference", required=True, copy=False, readonly=True,
                       default='New')
    state = fields.Selection(
        [('draft', 'Draft'), ('waiting_approval', 'Waiting for Approval'), ('approved', 'Approved '), ('rejected', 'Rejected'),
         ('cancel', 'Cancelled')], 'Status', default='draft')
    requester_id = fields.Many2one('res.users', 'Requester')
    current_user_id = fields.Many2one('res.users', 'Assets Currently Holding')
    asset_category_id = fields.Many2one('account.asset.category', 'Requesting Asset')
    asset_id = fields.Many2one('account.asset.asset', 'Asset')
    date = fields.Date('Date')
    reason = fields.Text('Reason')
    date_transferrd = fields.Date('Transferred Date')
    asset_history_ids = fields.One2many('account.asset.history', 'request_id', string='Movement History')
    is_asset = fields.Boolean('Is there Asset', default=False)

    current_assets_location = fields.Many2one('stock.location',string='Current Assets Location')
    new_assets_location = fields.Text(string='New Assets Location')


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
        self.asset_id.write({'owner_id': self.requester_id.id})

    @api.onchange('asset_id')
    def asset_onchange(self):
        self.current_user_id = self.asset_id.owner_id.id
        if self.asset_id:
            self.is_asset = True
        else:
            self.is_asset = False







