from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError, RedirectWarning, ValidationError

# mapping invoice type to journal type
TYPE2JOURNAL = {
    'out_invoice': 'sale',
    'in_invoice': 'purchase',
    'out_refund': 'sale',
    'in_refund': 'purchase',
}

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _compute_vendor_count(self):
        for order in self:
            invoices = self.env['account.invoice']
            invoice_ids = self.env['account.invoice'].search([('vendor_bill_id', '=', order.id)], limit=1)
            order.vendor_bill_ids = invoice_ids.ids
            order.vendor_bill_count = len(invoice_ids)


    vendor_bill_id = fields.Many2one('account.invoice', string='Add Vendor Bills')
    vendor_bill_count = fields.Integer('Vendor Bill', compute='_compute_vendor_count')
    vendor_bill_ids = fields.Many2many('account.invoice', string='Bills',compute='_compute_vendor_count', copy=False)

    @api.model
    def _default_journal(self):
        if self._context.get('default_journal_id', False):
            return self.env['account.journal'].browse(self._context.get('default_journal_id'))
        inv_type = self._context.get('type', 'out_invoice')
        inv_types = inv_type if isinstance(inv_type, list) else [inv_type]
        if not self._context.get('default_vendor_bill_id'):
            company_id = self._context.get('company_id', self.env.user.company_id.id)
        if self._context.get('default_vendor_bill_id'):
            company_id = self.env['res.company'].search([('name','=','PT MSR')], limit=1).id
            if self.env.user.company_id.name == 'PT MSR':
                company_id = self.env['res.company'].sudo().search([('name', '=', 'PT Multi Guna Maritim')], limit=1).id
        domain = [
            ('type', 'in', filter(None, map(TYPE2JOURNAL.get, inv_types))),
            ('company_id', '=', company_id),
        ]
        return self.env['account.journal'].search(domain, limit=1)

    @api.multi
    def action_view_vendor_bill(self):
        '''
        This function returns an action that display existing vendor bills of given purchase order ids.
        When only one found, show the vendor bill immediately.
        '''
        action = self.env.ref('account.action_invoice_tree2')
        result = action.read()[0]

        #override the context to get rid of the default filtering
        result['context'] = {'type': 'in_invoice', 'default_vendor_bill_id': self.id, 'default_date_invoice': self.date_invoice}
        company_id = self.env['res.company'].search([('name','=','PT MSR')], limit=1)
        if self.env.user.company_id.name == 'PT MSR':
            company_id = self.env['res.company'].sudo().search([('name', '=', 'PT Multi Guna Maritim')], limit=1)
        if not self.vendor_bill_ids:
            # Choose a default account journal in the same currency in case a new invoice is created
            journal_domain = [
                ('type', '=', 'purchase'),
                ('company_id', '=', company_id.id if company_id else self.company_id.id),
                ('currency_id', '=', False),
            ]
            default_journal_id = self.env['account.journal'].search(journal_domain, limit=1)
            if default_journal_id:
                result['context']['default_journal_id'] = default_journal_id.id
        else:
            # Use the same account journal than a previous invoice
            result['context']['default_journal_id'] = self.vendor_bill_ids[0].journal_id.id

        #choose the view_mode accordingly
        if len(self.vendor_bill_ids) != 1:
            result['domain'] = "[('id', 'in', " + str(self.vendor_bill_ids.ids) + ")]"
        elif len(self.vendor_bill_ids) == 1:
            res = self.env.ref('account.invoice_supplier_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = self.vendor_bill_ids.id
        return result

    def _prepare_invoice_line_from_po_line1(self, line):
        invoice_line = self.env['account.invoice.line']
        data = {
            'vendor_line_id': line.id,
            'name': self.vendor_bill_id.name or ''+': '+line.name,
            'origin': line.invoice_id.origin,
            'uom_id': line.uom_id.id,
            'product_id': line.product_id.id,
            'account_id': invoice_line.with_context({'journal_id': self.journal_id.id, 'type': 'in_invoice'})._default_account(),
            'price_unit': line.invoice_id.currency_id.with_context(date=self.date_invoice).compute(line.price_unit, self.currency_id, round=False),
            'quantity': line.quantity,
            'discount': 0.0,
            'account_analytic_id': line.account_analytic_id.id,
            'analytic_tag_ids': line.analytic_tag_ids.ids,
            'invoice_line_tax_ids': line.invoice_line_tax_ids.ids
        }
        account = invoice_line.get_invoice_line_account('in_invoice', line.product_id, line.invoice_id.fiscal_position_id, self.env.user.company_id)
        if account:
            data['account_id'] = account.id
            if self.env.user.company_id.name == 'PT MSR':
                company_id = self.env['res.company'].sudo().search([('name', '=', 'PT Multi Guna Maritim')], limit=1).id
            else:
                company_id = self.env['res.company'].sudo().search([('name','=','PT MSR')], limit=1).id
            data['company'] = company_id
        return data

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        payment_term_id = False
        fiscal_position = False
        res = []
        warning = {}
        domain = {}
        company_id = self.company_id.id
        list_of_company =self.env['res.company'].sudo().search([])
        user_company_id = self.env.user.company_id.id
        company_matrix = {}
        if len(list_of_company) == 2:
            company_matrix.update({
                list_of_company[0].id : list_of_company[1].id,
                list_of_company[1].id : list_of_company[0].id,
            })
            company_id = company_matrix[user_company_id]
            p = self.partner_id
            if self.env.context.get('default_vendor_bill_id'):
                # if self.env.user.company_id.name == 'PT MSR':
                #     company_id = self.env['res.company'].sudo().search([('name', '=', 'PT Multi Guna Maritim')], limit=1).id
                company_id = company_matrix[user_company_id]
                p = self.partner_id

            type = self.type
            if p:
                rec_account = p.property_account_receivable_id
                pay_account = p.property_account_payable_id
                if not rec_account and not pay_account:
                    action = self.env.ref('account.action_account_config')
                    msg = _(
                        'Cannot find a chart of accounts for this company, You should configure it. \nPlease go to Account Configuration.')
                    raise RedirectWarning(msg, action.id, _('Go to the configuration panel'))

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

            if self.env.context.get('default_vendor_bill_id'):
                # company_id = self.env['res.company'].search([('name','=','PT MSR')], limit=1).id
                # if self.env.user.company_id.name == 'PT MSR':
                #     company_id = self.env['res.company'].sudo().search([('name', '=', 'PT Multi Guna Maritim')], limit=1).id
                company_id = company_matrix[user_company_id]
            else:
                company_id = self.env.user.company_id.id
            account_id = self.env['account.account'].sudo().search([('company_id', '=', company_id), ('user_type_id', '=', self.env['account.account.type'].search([('type', '=', 'payable')], limit=1).id)], limit=1)

            self.account_id = account_id
            self.payment_term_id = payment_term_id
            self.date_due = False
            self.fiscal_position_id = fiscal_position

            if type in ('in_invoice', 'out_refund'):
                bank_ids = p.commercial_partner_id.bank_ids
                bank_id = bank_ids[0].id if bank_ids else False
                self.partner_bank_id = bank_id
                if self.env.context.get('default_vendor_bill_id'):
                    # company_id = self.env['res.company'].search([('name', '=', 'PT MSR')], limit=1).id
                    # if self.env.user.company_id.name == 'PT MSR':
                    #     company_id = self.env['res.company'].sudo().search([('name', '=', 'PT Multi Guna Maritim')], limit=1).id
                    company_id = company_matrix[user_company_id]
                else:
                    company_id = self.company_id.id
                domain = {'partner_bank_id': [('id', 'in', bank_ids.ids)]}
            if not self.env.context.get('default_journal_id') and self.partner_id and self.currency_id and \
                    self.type in ['in_invoice', 'in_refund'] and \
                    self.currency_id != self.partner_id.property_purchase_currency_id:
                journal_domain = [
                    ('type', '=', 'purchase'),
                    ('company_id', '=', company_id),
                    ('currency_id', '=', self.partner_id.property_purchase_currency_id.id),
                ]
                default_journal_id = self.env['account.journal'].search(journal_domain, limit=1)
                if default_journal_id:
                    self.journal_id = default_journal_id
            if self.env.context.get('default_vendor_bill_id'):
                # self.company_id = self.env['res.company'].search([('name','=','PT MSR')], limit=1).id
                # if self.env.user.company_id.name == 'PT MSR':
                #     self.company_id = self.env['res.company'].sudo().search([('name', '=', 'PT Multi Guna Maritim')], limit=1).id
                self.company_id = company_matrix[user_company_id]
            res = {}
            if warning:
                res['warning'] = warning
            if domain:
                res['domain'] = domain
        return res

    # Load all unsold PO lines
    @api.onchange('vendor_bill_id')
    def vendor_bill_change(self):
        if not self.vendor_bill_id:
            return {}
        if not self.partner_id:
            self.partner_id = self.vendor_bill_id.partner_id.id

        new_lines = self.env['account.invoice.line']
        for line in self.vendor_bill_id.invoice_line_ids - self.invoice_line_ids.mapped('vendor_line_id'):
            data = self._prepare_invoice_line_from_po_line1(line)
            new_line = new_lines.new(data)
            new_line._set_additional_fields(self)
            new_lines += new_line

        self.invoice_line_ids += new_lines
        self.purchase_id = False
        return {}

AccountInvoice()

class AccountInvoiceLine(models.Model):
    """ Override AccountInvoice_line to add the link to the purchase order line it is related to"""
    _inherit = 'account.invoice.line'

    vendor_line_id = fields.Many2one('account.invoice.line', 'Account Invoice Line', ondelete='set null', index=True, readonly=True)
    vendor_bill_id = fields.Many2one('account.invoice', related='vendor_line_id.invoice_id', string='Purchase Order', store=False, readonly=True, related_sudo=False,
        help='Associated Purchase Order. Filled in automatically when a PO is chosen on the vendor bill.')

AccountInvoiceLine()