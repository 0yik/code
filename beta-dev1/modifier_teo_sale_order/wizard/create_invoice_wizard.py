# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError, Warning

class CreateInvoiceWizard(models.TransientModel):
    _name = 'create.invoice.wizard'
    
    account_id = fields.Many2one("account.account", string="Account", required=True)
    journal_id = fields.Many2one("account.journal", string="Journal", required=True)
    
    @api.multi
    def create_invoice(self):
        values = {}
        so_partner_list = []
        so_line_list = self.env['sale.order.line'].browse(self._context.get('active_ids', []))
        for so_values in so_line_list:
            if not so_values.delivered and not so_values.invoiced:
                raise ValidationError(_('Please Update Delivered and Invoiced Quantity on Selected Line.'))
                break
            if so_values.invoiced > so_values.delivered:
                raise ValidationError(_('Invoiced Quantity must be Less or Equal Delivered Quantity'))
                break
            val_dict = {'partner_id': so_values.order_id.partner_id.id,
                        'order_id':so_values.order_id}
            so_partner_list.append(val_dict)
        
        final_lst = {v['partner_id']:v for v in so_partner_list}.values()
        invoices = []
        for partner in final_lst:
            invoice_id = self.env['account.invoice'].create({'partner_id': partner.get('partner_id'),
                                                             'type': 'out_invoice',
                                                             'account_id': self.account_id.id,
                                                             'journal_id': self.journal_id.id,
                                                             'partner_shipping_id': partner.get('order_id').partner_shipping_id.id,
                                                             'payment_term_id': partner.get('order_id').payment_term_id.id,
                                                             })
            invoices.append(invoice_id.id)
            for line in so_line_list:
                if line.order_id.partner_id.id == partner.get('partner_id'):
                    name = line.product_id.name_get()[0][1]
                    if line.product_id.description_sale:
                        name += '\n' + line.product_id.description_sale
                    line = {'name': name,
                            'invoice_id': invoice_id.id,
                            'origin': line.order_id.name,
                            'account_id': self.account_id.id,
                            'price_unit': line.price_unit,
                            'quantity': line.product_uom_qty,
                            'discount': line.discount,
                            'uom_id': line.product_uom.id,
                            'product_id': line.product_id.id,
                            'invoice_line_tax_ids': [(6, 0, [x.id for x in line.tax_id])],
                            }
                    self.env['account.invoice.line'].create(line)
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
            action['res_id'] = invoices[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action