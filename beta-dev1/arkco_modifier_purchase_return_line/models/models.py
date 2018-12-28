# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ArkcoModifierPurhcaseOrder(models.Model):
    _inherit = 'purchase.order'

    state = fields.Selection([
        ('draft', 'RFQ'),
        ('waiting_for_approval', 'RFQ Waiting for Approval'),
        ('rfq_approved', 'RFQ Approved'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ('rfq_reject', 'RFQ Rejected'),
        ('pending', 'Retur Pending')
        ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')

    @api.multi
    def button_cancel(self):
        if self.state == 'draft':
            res = super(ArkcoModifierPurhcaseOrder, self).button_cancel()
            return res
        else:
            res = super(ArkcoModifierPurhcaseOrder, self).button_cancel()
            self.write({'state': 'pending'})
            return res

    @api.multi
    def button_approve_cancel(self):
        for order in self:
            if order.state == 'pending':
                if order.user_has_groups('purchase.group_purchase_manager'):
                    self.write({'state':'cancel'})

    @api.multi
    def button_reject_cancel(self):
        for order in self:
            if order.state == 'pending':
                if order.user_has_groups('purchase.group_purchase_manager'):
                    self.write({'state':'purchase'})
