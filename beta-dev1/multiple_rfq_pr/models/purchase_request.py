# -*- coding: utf-8 -*-

from odoo import fields, models, api

class purchase_request_line(models.Model):
    _inherit = 'purchase.request.line'

    requested_by    =   fields.Many2one('res.users','Requested by')
    rfq_number      =   fields.Many2one('purchase.order','RFQ Number',readonly=True)
    vendor          =   fields.Many2one('res.partner','Vendor',readonly=True)
    total_amount    =   fields.Float('Total Amount',readonly=True)
    preferred_vendor=   fields.Boolean('Preferred Vendor')
    justification   =   fields.Text('Justification')
    date_required   =   fields.Date(required=True)
    request_id      =   fields.Many2one('purchase.request')

    def action_approve(self):
        self.request_id.write({'state' : 'approved'})
        self.rfq_number.requisition_id.write({'state': 'done'})
        for other_rfq in self.rfq_number.requisition_id.purchase_ids:
            if other_rfq.id != self.rfq_number.id:
                self.other_rfq.write({'state' : 'cancel'})

        return True

    # @api.onchange('preferred_vendor')
    def preferred_vendor_check(self):
        for line in self.request_id.line_ids:
            if line.id != self.id:
                line.write({'preferred_vendor': False})

class purchase_request(models.Model):
    _inherit = 'purchase.request'

    line_ids        =   fields.One2many('purchase.request.line', 'request_id', 'RFQs')
    requisition_id  =   fields.Many2one('purchase.requisition')
