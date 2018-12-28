from odoo import models, fields, exceptions, api, _
from odoo.exceptions import UserError
import datetime


class ShippingInvoice(models.TransientModel):
    _name = "shipment.invoice"

    @api.model
    def default_get(self, fields):
        res = super(ShippingInvoice, self).default_get(fields)
        picking_obj = self.env['stock.picking']
        purchase_id = self.env['purchase.order'].browse(self._context.get('active_ids'))
        picking_search = picking_obj.search([('origin', '=', purchase_id.name)])
        res['shiping_domain'] = [('id', 'in', [picking.id for picking in picking_search])]
        return res

    shipment_id = fields.Many2one('stock.picking', 'Shippments')
    shiping_domain = fields.Char('Domain')

    @api.multi
    def create_vendor_bill(self):
        for rec in self:
            purchase_id = self.env['purchase.order'].browse(self._context.get('active_ids'))
            account_id = self.env['account.account'].search(
                [('user_type_id', '=', 2), ('company_id', '=', self.env.user.company_id.id)], limit=1)
            journal_id = self.env['account.journal'].search(
                [('type', '=', 'purchase'), ('company_id', '=', self.env.user.company_id.id)], limit=1)
            invoice_line = []
            shipment_invoice = self.env['ir.values'].get_default('purchase.config.settings', 'shipment_invoice',
                                                                 company_id=self.env.user.company_id.id)
            if (shipment_invoice and shipment_invoice == 'single' and not rec.shipment_id.shipement_invoice_created) or shipment_invoice == 'multiple':
                for ship in rec.shipment_id:
                    for line in ship.move_lines:
                        invoice_line.append([0, 0, {
                            'product_id': line.product_id.id,
                            'product_uom_qty': line.product_uom_qty,
                            'quantity': line.product_qty,
                            'product_uom': line.product_uom.id,
                            'name': line.product_id.name,
                            'price_unit': line.price_unit,
                            'account_id': account_id.id,
                        }
                                             ])
                    invoices = {
                        'purchase_id': purchase_id.id,
                        'partner_id': purchase_id.partner_id.id,
                        'date_invoice': datetime.date.today(),
                        'invoice_line_ids': invoice_line,
                        'account_id': account_id.id,
                        'journal_id': journal_id.id,
                        'user_id': self.env.user.id,
                        'type': 'in_invoice',
                        'is_shipment_bill': True,

                    }
                    create_invoice = self.env['account.invoice'].create(invoices)
                    self.shipment_id.shipement_invoice_created = True
            else:

                raise UserError(_("As per configuration you cannot create more than one vendor bill for the same shipment."))

        return True
