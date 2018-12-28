# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class ArkcoModifierRFQTendor(models.Model):
    _inherit = 'purchase.requisition'

    min_order = fields.Integer(string="Min Order", default="1")

    @api.onchange('min_order')
    def check_min_order_value(self):
        for rec in self:
            if rec:
                if rec.min_order <= 0:
                    raise ValidationError(_("Min Order can not be 0 or negative number."))

    @api.model
    def create(self, vals):
        res = super(ArkcoModifierRFQTendor, self).create(vals)
        for rec in res:
            if rec.min_order <= 0:
                raise ValidationError(_("Min Order can not be 0 or negative number."))
        return res

    @api.multi
    def write(self, values):
        res = super(ArkcoModifierRFQTendor, self).write(values)
        for rec in self:
            if 'min_order' in values and (rec.min_order <= 0):
                raise ValidationError(_("Min Order can not be 0 or negative number."))
        return res


class ArkcoModifierPurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    @api.multi
    def button_confirm(self):
        res = super(ArkcoModifierPurchaseOrder, self).button_confirm()
        for order in self:
            rfq_ids = self.env['purchase.order'].search([('requisition_id', '=', order.requisition_id.id), ('state', '=', 'draft')])
            for rfq in rfq_ids:
                if rfq.id == order.id:
                    continue
                else:
                    rfq.button_cancel()
        return res

    @api.multi
    def request_rfq_approve(self):
        for order in self:
            if order.requisition_id:
                if order.requisition_id.order_count < order.requisition_id.min_order:
                    raise UserError(_("Your request can not be processed! \
                        \nThe RFQ Count is less than Min Order for %s."  %(order.requisition_id.name)))
                else:
                    res = super(ArkcoModifierPurchaseOrder, self).request_rfq_approve()
                    return res
            else:
                res = super(ArkcoModifierPurchaseOrder, self).request_rfq_approve()
                return res