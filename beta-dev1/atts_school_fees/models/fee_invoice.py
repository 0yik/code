import math

from datetime import datetime, timedelta
from odoo import models, fields, api, tools, _
from odoo.tools import amount_to_text_en


class StudentFeesInvoice(models.Model):
    _name = 'student.fees.invoice'

    @api.multi
    @api.depends('invoice_lines')
    def _total_amount(self):
        for rec in self:
            total_amt = 0.0
            for line in rec.invoice_lines:
                total_amt += line.total
            rec.total = total_amt

    @api.onchange('payment_term_id', 'date')
    def _onchange_payment_term_date_invoice(self):
        date_invoice = self.date
        if not date_invoice:
            date_invoice = fields.Date.today()
        if not self.payment_term_id:
            self.dead_line = date_invoice
            if self.registration_id:
                self.dead_line = self.registration_id.class_id and self.registration_id.class_id.date_start or self.registration_id.payment_deadline
        else:
            pterm = self.payment_term_id
            pterm_list = pterm.with_context(currency_id=self.env.user.company_id.currency_id.id).compute(value=1, date_ref=date_invoice)[0]
            self.dead_line = max(line[0] for line in pterm_list)

    name = fields.Char(string='Invoice', required=True, default=lambda self: _('New'))
    registration_id = fields.Many2one('class.registration', 'Registration')
    fee_registration_id = fields.Many2one('student.fees.register', 'Fee Register', required=True)
    student_name = fields.Char("Student Name")
    student_email = fields.Char("Student Email ID")
    date = fields.Date('Date', required=True,
                       help="Date of register",
                       default=fields.Date.today())
    dead_line = fields.Date('Due Date', compute="_onchange_payment_term_date_invoice")
    delegate_id = fields.Many2one('registration.delegate.lines', 'Delegate')
    state = fields.Selection([
        ('draft', 'Invoice Sent'),
        ('paid', 'Paid'),
        ('refund', 'Refund'),
        ('cancel', 'Cancelled')],
        'State', readonly=True, default='draft')

    invoice_lines = fields.One2many('student.fees.invoice.line', 'invoice_id', 'Invoice Lines')
    total = fields.Float("Total", compute="_total_amount", store=True)
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('fee.invoice') or _('New')
        return super(StudentFeesInvoice, self).create(vals)

    def get_invoice_date(self):
        date_start = datetime.strptime(self.date, tools.DEFAULT_SERVER_DATE_FORMAT)
        date = date_start.strftime('%d') + '-' + date_start.strftime('%b') + '-' + date_start.strftime('%y')
        return date

    def get_invoice_due_date(self):
        date_start = datetime.strptime(self.dead_line, tools.DEFAULT_SERVER_DATE_FORMAT)
        date = date_start.strftime('%d') + '-' + date_start.strftime('%b') + '-' + date_start.strftime('%y')
        return date

    def get_amount_in_word(self, amount):
        amount = amount_to_text_en.amount_to_text(amount, 'en', self.env.user.company_id.currency_id.name)
        # amount.replace('SGD', 'Dollars')
        return amount.replace('SGD', 'Dollars')

    def check_any_course_line(self):
        return any([line_id for line_id in self.invoice_lines if line_id.fee_head_id.is_course_head])


class StudentFeesInvoiceLine(models.Model):
    '''Student Fees Structure Line'''
    _name = 'student.fees.invoice.line'

    @api.onchange('fee_head_id')
    def _on_fee_head_id(self):
        for line in self:
            line.details = line.fee_head_id.name
            line.amount = line.fee_head_id.amount
            line.quantity = line.invoice_id.registration_id.individual_billing and len(line.invoice_id.registration_id.delegate_lines) or 1
            line.tax = line.fee_head_id.gst
            line.total = (line.amount * line.quantity) * (1 + line.tax/100)

    invoice_id = fields.Many2one('student.fees.invoice', 'Invoice')
    fee_head_id = fields.Many2one('student.fees.structure.line', string='Description')
    details = fields.Char('Details')
    amount = fields.Float('Amount', digits=(16, 2))
    quantity = fields.Integer('Quantity', default=1)
    tax = fields.Float('TAX(%)', digits=(16, 2), default=7)
    total = fields.Float('Total', digits=(16, 2))

class FeeAccountInvoicePayment(models.Model):
    _inherit = 'account.payment'

    fee_invoice_id = fields.Many2one('student.fees.invoice', 'Fee Invoice')
    registration_id = fields.Many2one('class.registration', 'Registration', related='fee_invoice_id.registration_id')
    sign_amount = fields.Float('Amount')

    def create_payment(self):
        self.name = self.fee_invoice_id.name
        sign = self.payment_type in ['outbound'] and -1 or 1
        self.sign_amount = self.amount * sign
        if self.payment_type == 'inbound':
            self.fee_invoice_id.state = 'paid'
        if self.payment_type == 'outbound':
            self.fee_invoice_id.state = 'refund'

    @api.model
    def default_get(self,fields):
        context = self._context or {}
        ret = super(FeeAccountInvoicePayment,self).default_get(fields)
        payment_id = self.env['student.fees.invoice'].browse([context.get('active_id',False)])
        if payment_id:
            ret['amount'] = payment_id.total
        return ret
