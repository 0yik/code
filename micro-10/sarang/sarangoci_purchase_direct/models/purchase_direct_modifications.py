from odoo import api, fields, models, _
from odoo.exceptions import UserError

class PurchaseDirect(models.Model):
    _inherit = 'purchase.order'

    is_purchase_direct = fields.Boolean(string = "Purchase Direct")

    @api.model
    def create(self, vals):
        res = super(PurchaseDirect, self).create(vals)
        if vals.get("is_purchase_direct") is True:
            res.name = self.env['ir.sequence'].next_by_code('purchase.direct')
        else:
            pass
        return res

    @api.multi
    def button_approve(self, force=False):
        res = super(PurchaseDirect, self).button_approve()
        if self.is_purchase_direct:
            #Creating and completing shipment
            for picking in self.picking_ids:
                if picking.state == 'assigned':
                    if picking.pack_operation_ids:
                        for pack in picking.pack_operation_ids:
                            if pack.product_qty > 0:
                                pack.write({'qty_done': pack.product_qty})
                    if picking.pack_operation_product_ids:
                        for pack in picking.pack_operation_product_ids:
                            if pack.product_qty > 0:
                                pack.write({'qty_done': pack.product_qty})
                    picking.do_transfer()
            # Creating and Payment done for invoice
            for invoice in self.invoice_ids:
                invoice.with_context(from_kp=True).action_invoice_open()
                if not invoice.partner_id.default_payment_journal:
                    raise UserError(_('No account found for this Vendor. \n Please configure Account first.'))
                else:
                    invoice.pay_and_reconcile(pay_journal = invoice.partner_id.default_payment_journal)
        else:
            pass
        # 2/0
        return res


class AccountInvoiceModification(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_move_create(self):
        if self.env.context and self.env.context.get('from_kp'):
            for rec in self:
                seq = self.env['ir.sequence'].search([('name', '=', 'Vendor Bills')])
                rec.journal_id.sequence_id = seq.id

        res = super(AccountInvoiceModification, self).action_move_create()
        return res

