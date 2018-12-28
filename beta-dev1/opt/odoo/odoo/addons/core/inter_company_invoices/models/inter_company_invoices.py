from odoo.exceptions import UserError
from odoo import api, fields, models

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_invoice_open(self):
        # lots of duplicate calls to action_invoice_open, so we remove those already open
        to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
        if to_open_invoices.filtered(lambda inv: inv.state not in ['proforma2', 'draft']):
            raise UserError(_("Invoice must be in draft or Pro-forma state in order to validate it."))
        to_open_invoices.action_date_assign()
        to_open_invoices.sudo().action_move_create()
        company_partner_id = self.env['res.company'].search([('partner_id', '=', self.partner_id.id)])
        if self.type in ['out_invoice','out_refund']:
            self.create_new_supplier_invoice()
        if self.type in ['in_invoice','in_refund']:
            cust_in = self.create_new_customer_invoice()
        return to_open_invoices.invoice_validate()

    
    def create_new_supplier_invoice(self):
        read = self.search_read([('id','=',self.id)])
        vals =read[0]
        if vals['type'] == 'out_invoice' or vals['type'] == 'out_refund':
            if vals['type'] == 'out_invoice':
                dest_type = 'in_invoice'
            if vals['type'] == 'out_refund':
                dest_type = 'in_refund'
            partner_id = self.env['res.partner'].sudo().browse(vals['partner_id'][0])
            new_vals = {}
            if partner_id.company_id.id != self.env.user.company_id.id:
                new_vals['partner_id'] = self.env.user.company_id.partner_id.id
                new_vals['company_id'] = partner_id.company_id.id
                new_vals['type'] = dest_type
                new_vals['journal_id'] = self.env['account.journal'].search([('type','=','purchase'),('company_id','=',vals['company_id'][0])]).id
                new_vals['account_id'] = self.env.user.company_id.partner_id.property_account_payable_id.id
                new_vals['currency_id'] = vals['currency_id'][0] 
                new_vals['move_id'] = vals['move_id'][0] 
                new_vals['user_id'] = vals['user_id'][0] 
                new_vals['commercial_partner_id'] = self.env.user.company_id.partner_id.commercial_partner_id.id
                new_vals['company_currency_id'] =vals['company_currency_id'][0] 
                invoice_id = self.create(new_vals)
                invoice_obj = self.env['account.invoice'].browse(invoice_id)
                # # write type of supplier invoice
                # if invoice_obj:
                #     if vals['type'] == 'out_invoice':
                #         dest_type = 'in_invoice'
                #     if vals['type'] == 'out_refund':
                #         dest_type = 'in_refund'
                #     invoice_obj.write({'type':dest_type})

                new_line = {}
                for line in self.env['account.invoice.line'].search_read([('invoice_id','=',self.id)]): 
                    new_line['currency_id'] =line['currency_id'][0]
                    new_line['uom_id'] =line['uom_id'][0]
                    new_line['price_unit']=line['price_unit']
                    new_line['name']=line['name']
                    new_line['quantity']=line['quantity']
                    new_line['partner_id'] =line['partner_id'][0]
                    new_line['company_id'] =vals['company_id'][0] 
                    new_line['account_id'] =line['account_id'][0]
                    new_line['company_currency_id'] =line['company_currency_id']
                    new_line['product_id'] =line['product_id'][0]
                    new_line['invoice_id'] = invoice_id.id 
                    invoice_line_id = self.env['account.invoice.line'].create(new_line)

    def create_new_customer_invoice(self): #
        read = self.search_read([('id','=',self.id)]) 
        vals =read[0]
        if vals['type'] == 'in_invoice' or vals['type'] == 'in_refund':
            if vals['type'] == 'in_invoice':
                dest_type = 'out_invoice'
            if vals['type'] == 'in_refund':
                dest_type = 'out_refund'
            partner_id = self.env['res.partner'].sudo().browse(vals['partner_id'][0])
            new_vals = {}
            if partner_id.company_id.id != self.env.user.company_id.id:
                new_vals['partner_id'] = self.env.user.company_id.partner_id.id 
                new_vals['company_id'] = partner_id.company_id.id
                new_vals['type'] = dest_type
                new_vals['journal_id'] = self.env['account.journal'].search([('type','=','sale'),('company_id','=',vals['company_id'][0])]).id
                new_vals['account_id'] = self.env.user.company_id.partner_id.property_account_payable_id.id
                new_vals['currency_id'] = vals['currency_id'][0] 
                new_vals['move_id'] = vals['move_id'][0] 
                new_vals['user_id'] = vals['user_id'][0] 
                new_vals['commercial_partner_id'] = self.env.user.company_id.partner_id.commercial_partner_id.id
                new_vals['company_currency_id'] =vals['company_currency_id'][0] 
                invoice_id = self.create(new_vals)
                invoice_obj = self.env['account.invoice'].browse(invoice_id)
                new_line = {}
                for line in self.env['account.invoice.line'].search_read([('invoice_id','=',self.id)]): 
                    new_line['currency_id'] =line['currency_id'][0]
                    new_line['uom_id'] =line['uom_id'][0]
                    new_line['price_unit']=line['price_unit']
                    new_line['name']=line['name']
                    new_line['quantity']=line['quantity']
                    new_line['partner_id'] =line['partner_id'][0]
                    new_line['company_id'] =vals['company_id'][0] 
                    new_line['account_id'] =line['account_id'][0]
                    new_line['company_currency_id'] =line['company_currency_id']
                    new_line['product_id'] =line['product_id'][0]
                    new_line['invoice_id'] = invoice_id.id 
                    invoice_line_id = self.env['account.invoice.line'].create(new_line)

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        account_id = False
        payment_term_id = False
        fiscal_position = False
        bank_id = False
        warning = {}
        domain = {}
        company_id = self.company_id.id
        p = self.partner_id if not company_id else self.partner_id.with_context(force_company=company_id)
        type = self.type
        if p:
            rec_account = p.property_account_receivable_id
            pay_account = p.property_account_payable_id
            
            if self.env.user.company_id.id != rec_account.company_id.id:
                receivable_account_ids = self.env['account.account'].sudo().search([('company_id','=',self.env.user.company_id.id),                             ('internal_type','=','receivable'),('deprecated','=',False)],limit=1)
                rec_account = receivable_account_ids
            if self.env.user.company_id.id != pay_account.company_id.id:
                payable_account_ids = self.env['account.account'].sudo().search(
                    [('company_id', '=', self.env.user.company_id.id), ('internal_type', '=', 'payable'),
                     ('deprecated', '=', False)], limit=1)
                pay_account = payable_account_ids
            

            if type in ('out_invoice', 'out_refund'):
                account_id = rec_account.id
                payment_term_id = p.property_payment_term_id.id
            else:
                account_id = pay_account.id
                payment_term_id = p.property_supplier_payment_term_id.id

            delivery_partner_id = self.get_delivery_partner_id()
            fiscal_position = self.env['account.fiscal.position'].get_fiscal_position(self.partner_id.id,
                                                                                      delivery_id=delivery_partner_id)

            # If partner has no warning, check its company
            if p.invoice_warn == 'no-message' and p.parent_id:
                p = p.parent_id
            if p.invoice_warn != 'no-message':
                # Block if partner only has warning but parent company is blocked
                if p.invoice_warn != 'block' and p.parent_id and p.parent_id.invoice_warn == 'block':
                    p = p.parent_id
                warning = {
                    'title': _("Warning for %s") % p.name,
                    'message': p.invoice_warn_msg
                }
                if p.invoice_warn == 'block':
                    self.partner_id = False


        self.account_id = account_id
        self.payment_term_id = payment_term_id
        self.date_due = False
        self.fiscal_position_id = fiscal_position

        if type in ('in_invoice', 'out_refund'):
            bank_ids = p.commercial_partner_id.bank_ids
            bank_id = bank_ids[0].id if bank_ids else False
            self.partner_bank_id = bank_id
            domain = {'partner_bank_id': [('id', 'in', bank_ids.ids)]}

        res = {}
        if warning:
            res['warning'] = warning
        if domain:
            res['domain'] = domain
        return res
