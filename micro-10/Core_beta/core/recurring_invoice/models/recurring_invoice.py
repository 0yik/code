# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
TYPE2JOURNAL = {
    'out_invoice': 'sale',
    'in_invoice': 'purchase',
    'out_refund': 'sale',
    'in_refund': 'purchase',
}
class recurring_invoice(models.Model):
    _name = 'recurring.invoice'

    @api.model
    def _default_journal(self):
        if self._context.get('default_journal_id', False):
            return self.env['account.journal'].browse(self._context.get('default_journal_id'))
        inv_type = self._context.get('type', 'out_invoice')
        inv_types = inv_type if isinstance(inv_type, list) else [inv_type]
        company_id = self._context.get('company_id', self.env.user.company_id.id)
        domain = [
            ('type', 'in', filter(None, map(TYPE2JOURNAL.get, inv_types))),
            ('company_id', '=', company_id),
        ]
        return self.env['account.journal'].search(domain, limit=1)

    @api.model
    def _default_currency(self):
        journal = self._default_journal()
        return journal.currency_id or journal.company_id.currency_id or self.env.user.company_id.currency_id

    partner_id = fields.Many2one('res.partner',string='Customer',required=True)
    amount = fields.Monetary('Amount',compute='_compute_amount',store=True)
    state = fields.Selection([('draft', 'Draft'), ('progress', 'In Progress'),('completed','Completed'), ('cancel', 'Cancelled')], string='Status',
                             default='draft')

    journal_id = fields.Many2one('account.journal', string='Journal',
                                 required=True, readonly=True, states={'draft': [('readonly', False)]},
                                 default=_default_journal,
                                 domain="[('type', 'in', {'out_invoice': ['sale'], 'out_refund': ['sale'], 'in_refund': ['purchase'], 'in_invoice': ['purchase']}.get(type, [])), ('company_id', '=', company_id)]")
    account_id = fields.Many2one('account.account', string='Account',
                                 required=True, readonly=True, states={'draft': [('readonly', False)]},
                                 domain=[('deprecated', '=', False)], help="The partner account used for this invoice.")
    type = fields.Selection([
        ('out_invoice', 'Customer Invoice'),
        ('in_invoice', 'Vendor Bill')
    ], readonly=True, index=True, change_default=True,
        default=lambda self: self._context.get('type', 'out_invoice'),
        track_visibility='always')

    start_date = fields.Date(default=fields.Date.today, required=True)
    frequency = fields.Integer('Frequency',required=True)
    interval_unit = fields.Selection([('days', 'Days'), ('weeks', 'Weeks'), ('months', 'Months'), ('quarter', 'Quarter'), ('years', 'Years')], string='Interval Unit',default='days')
    currency_id = fields.Many2one('res.currency', string='Currency',required=True,default=_default_currency)

    company_id = fields.Many2one('res.company', string='Company', change_default=True,
                                 required=True, readonly=True, states={'draft': [('readonly', False)]},
                                 default=lambda self: self.env['res.company']._company_default_get('account.invoice'))

    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency",
                                          readonly=True)

    recurring_invoice_line_ids = fields.One2many('recurring.invoice.line', 'recurring_invoice_id', string='Recurring Invoice Lines',
                                       readonly=True, states={'draft': [('readonly', False)]}, copy=True)

    recurring_schedule_lines = fields.One2many('recurring.schedule','recurring_invoice_id',string='Recurring Invoice Lines',readonly=True)

    @api.multi
    @api.depends('recurring_invoice_line_ids.price_subtotal', 'currency_id', 'company_id')
    def _compute_amount(self):
        self.amount = sum(line.price_subtotal_signed for line in self.recurring_invoice_line_ids)

    @api.multi
    def unlink(self):
        for item in self.filtered(lambda recurring_invoice: recurring_invoice.state not in ['draft']):
            raise UserError(_('In recurring invoice to delete, it must be draft.'))
        return super(recurring_invoice, self).unlink()

    @api.multi
    def button_progress(self):
        self.create_recurring_schedule()
        self.write({'state': 'progress'})
        return True

    @api.multi
    def button_cancel(self):
        self.write({'state': 'cancel'})
        return True

    def create_recurring_schedule(self):
        next_date = datetime.strptime(self.start_date, DEFAULT_SERVER_DATE_FORMAT)
        for i in range(0,self.frequency):
            vals = {
                'date': next_date,
                'recurring_invoice_id' : self.id,
                'created':False,
                'is_last': True if i == self.frequency-1 else False
            }
            print"\n\nvals:\n\n", vals
            next_date = self._compute_recurring_date(next_date)
            self.env['recurring.schedule'].create(vals)

    def _compute_recurring_date(self,date):
        if self.interval_unit == 'days':
            return date + relativedelta(days=1)
        elif self.interval_unit == 'weeks':
            return date + relativedelta(weeks=1)
        elif self.interval_unit == 'months':
            return date + relativedelta(months=1)
        elif self.interval_unit == 'quarter':
            return date + relativedelta(months=4)
        elif self.interval_unit == 'years':
            return date + relativedelta(years=1)
        else:
            return date

    @api.model
    def auto_create_customer_invoice(self):
        now = datetime.now().strftime("%Y-%m-%d")
        recurring_schedule_lines = self.env['recurring.schedule'].search([('date','=',now),('created','=',False)])
        for line in recurring_schedule_lines:
            recurring = line.recurring_invoice_id
            if recurring.type == 'in_invoice':
                continue
            #TODO CREATE INVOICE
            invoice_val = {
                'partner_id': recurring.partner_id.id,
                'reference_type': 'none',
                'account_id': recurring.account_id.id,
                'journal_id' : recurring.journal_id.id,
                'company_id' : recurring.company_id.id,
                'currency_id': recurring.currency_id.id,
                'date_invoice': now,
                'type': 'out_invoice',
            }
            invoice = self.env['account.invoice'].create(invoice_val)
            #TODO CREATE LINE INVOICE
            for invoice_line in recurring.recurring_invoice_line_ids:
                line_val = {
                    'name' : invoice_line.name,
                    'invoice_id': invoice.id,
                    'uom_id' : invoice_line.uom_id and invoice_line.uom_id.id or False,
                    'product_id': invoice_line.product_id.id,
                    'account_id': invoice_line.account_id.id,
                    'price_unit': invoice_line.price_unit,
                    'quantity': invoice_line.quantity,
                    'discount': invoice_line.discount,
                    'invoice_line_tax_ids': [(6, 0, invoice_line.invoice_line_tax_ids.ids)],
                    'account_analytic_id': invoice_line.account_analytic_id and invoice_line.account_analytic_id.id or False,
                    'analytic_tag_ids': invoice_line.analytic_tag_ids and invoice_line.analytic_tag_ids.id or False,
                }
                account_invoice_line = self.env['account.invoice.line'].create(line_val)
            # TODO UPDATE RECURRING
            if line.is_last:
                recurring.write({'state': 'completed'})
            line.write({
                'invoice_id': invoice.id,
                'created' : True
            })
        return True

    @api.model
    def auto_create_vendor_invoice(self):
        now = datetime.now().strftime("%Y-%m-%d")
        recurring_schedule_lines = self.env['recurring.schedule'].search([('date', '=', now), ('created', '=', False)])
        for line in recurring_schedule_lines:
            recurring = line.recurring_invoice_id
            if recurring.type == 'out_invoice':
                continue
            # TODO CREATE INVOICE
            invoice_val = {
                'partner_id': recurring.partner_id.id,
                'reference_type': 'none',
                'account_id': recurring.account_id.id,
                'journal_id': recurring.journal_id.id,
                'company_id': recurring.company_id.id,
                'currency_id': recurring.currency_id.id,
                'date_invoice': now,
                'type': 'in_invoice',
            }
            invoice = self.env['account.invoice'].create(invoice_val)
            # TODO CREATE LINE INVOICE
            for invoice_line in recurring.recurring_invoice_line_ids:
                line_val = {
                    'name': invoice_line.name,
                    'invoice_id': invoice.id,
                    'uom_id': invoice_line.uom_id and invoice_line.uom_id.id or False,
                    'product_id': invoice_line.product_id.id,
                    'account_id': invoice_line.account_id.id,
                    'price_unit': invoice_line.price_unit,
                    'quantity': invoice_line.quantity,
                    'discount': invoice_line.discount,
                    'invoice_line_tax_ids': [(6, 0, invoice_line.invoice_line_tax_ids.ids)],
                    'account_analytic_id': invoice_line.account_analytic_id and invoice_line.account_analytic_id.id or False,
                    'analytic_tag_ids': invoice_line.analytic_tag_ids and invoice_line.analytic_tag_ids.id or False,
                }
                account_invoice_line = self.env['account.invoice.line'].create(line_val)
            # TODO UPDATE RECURRING
            if line.is_last:
                recurring.write({'state': 'completed'})
            line.write({
                'invoice_id': invoice.id,
                'created': True
            })
        return True