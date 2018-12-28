# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    @api.model
    def get_branch_id(self):
        if self._uid:
            return self.env.user.branch_id.id

    branch_id = fields.Many2one('res.branch', string='Branch',required=True, default=get_branch_id)

    @api.onchange('requested_by')
    def change_branch_user(self):
        if self.requested_by:
            if self.requested_by.branch_id:
                self.branch_id = self.requested_by.branch_id

    @api.model
    def create(self,vals):
        res = super(PurchaseRequest, self.with_context({'mail_create_nosubscribe':True})).create(vals)
        return res

    @api.multi
    def write(self,vals):
        res = super(PurchaseRequest, self.with_context({'mail_create_nosubscribe':True})).write(vals)
        return res
