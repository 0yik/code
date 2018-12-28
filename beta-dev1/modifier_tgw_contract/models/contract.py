# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from openerp import models, fields, api, _, tools
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)

class account_invoice(models.Model):
    _inherit = 'account.invoice'

    account_analytic_account_id = fields.Many2one('account.analytic.account', string='Contract')

class account_analytic_account(models.Model):
    _inherit = 'account.analytic.account'


    @api.one
    @api.depends('account_analytic_account_line_id.price', 'account_analytic_account_line_id.tax_ids','account_analytic_account_line_id.qty')
    def _compute_amount(self):
        self.amount_untaxed = sum((line.price * line.qty) for line in self.account_analytic_account_line_id)
        self.amount_total = sum(line.price_subtotal for line in self.account_analytic_account_line_id)
        self.amount_tax = self.amount_total - self.amount_untaxed


    @api.multi
    def _compute_invoices(self):
        invoices = 0
        invoice_ids = self.env['account.invoice'].search([('account_analytic_account_id', '=', self.id)])
        if invoice_ids:
            invoices = len(invoice_ids)
        self.invoice_count = invoices

    state = fields.Selection([
        ('template', 'Template'),
        ('draft', 'New'),
        ('validate', 'Validate'),
        ('open', 'In Progress'),
        ('pending', 'To Renew'),
        ('close', 'Closed'),
        ('cancelled', 'Cancelled')], 'Status', required=True, default='draft',
        track_visibility='onchange', copy=False)
    contract_number = fields.Char('Contract Number', select=True, track_visibility='onchange', copy=False,
                       default=lambda self: self.env['ir.sequence'].get('contract.contract'))
    date = fields.Date('Date')
    user_id = fields.Many2one(
        'hr.employee', 'Bridal Advisor', track_visibility='onchange',
        domain=lambda self: [('job_id', '=', self.env.ref('modifier_tgw_contract.job_bridal_advisor').id)])
    user_id2 = fields.Many2one('hr.employee', string="Bridal Advisor2", domain=lambda self: [('job_id', '=', self.env.ref('modifier_tgw_contract.job_bridal_advisor').id)])

    bridal_specialist = fields.Many2one('hr.employee', string="Bridal Specialist",
                                        domain=lambda self: [
                                            ('job_id', '=', self.env.ref('modifier_tgw_contract.job_bridal_specialist').id)])
    backup_bridal_specialist = fields.Many2one('hr.employee', string="Back up Bridal Specialist",
                                        domain=lambda self: [
                                            ('job_id', '=', self.env.ref('modifier_tgw_contract.job_bridal_specialist').id)])
    
    bride_firstname = fields.Char("Bride's First Name",required=True)
    bride_lastname = fields.Char("Bride's Last Name",required=True)
    bride_email = fields.Char(string="Email",required=True)
    bride_phone = fields.Char(string="Bride's Phone",required=True)
    bride_street = fields.Char(string="Street",required=True)
    bride_street2 = fields.Char(string="Street2",required=True)
    bride_zip = fields.Char(string="Zip", size=24, change_default=True,required=True)
    bride_city = fields.Char(string="City",required=True)
    bride_state_id = fields.Many2one(
        "res.country.state", string="State", ondelete='restrict',required=True)
    bride_country_id = fields.Many2one(
        'res.country', string="Country", ondelete='restrict',required=True)
    bride_birthdate = fields.Date(string="DOB")
    bride_nric = fields.Char(string="NRIC")
    
    customer_id = fields.Char(related="bride_phone",
                              string="Customer ID", readonly=False)

    
    groom_firstname = fields.Char("Groom's First Name")
    groom_lastname = fields.Char("Groom's Last Name")
    groom_name = fields.Char(string="Name")
    groom_email = fields.Char(string="Email")
    groom_phone = fields.Char(string="Telephone")
    groom_street = fields.Char(string="Street")
    groom_street2 = fields.Char(string="Street2")
    groom_zip = fields.Char(string="Zip", size=24, change_default=True)
    groom_city = fields.Char(string="City")
    groom_state_id = fields.Many2one("res.country.state", string="State",
                                     ondelete='restrict')
    groom_country_id = fields.Many2one('res.country', string="Country",
                                       ondelete='restrict')
    groom_birthdate = fields.Date(string="DOB")
    groom_nric = fields.Char(string="NRIC")

    contact_name = fields.Char(string="Contact Name")
    contact_num = fields.Char(string="Contact Number")
    contact_email = fields.Char(string="Contact Email")

    date_rom = fields.Datetime(string="Date of ROM")
    wedd_venue = fields.Char(string="Wedding Venue")
    date_wedd = fields.Datetime(string="Wedding Date 1")
    date_wedd2 = fields.Datetime(string="Wedding Date 2")
    wedding = fields.Selection(
        [('lunch', 'Lunch'), ('dinner', 'Dinner')], string='Lunch/Dinner')
    num_guests = fields.Char(string="Number of Guests")
    meet_up_date = fields.Date('First Appointment')
    photography_date = fields.Date('Photography Date')
    
    agree_bool = fields.Boolean("I agree and accept the contract terms and conditions")
    sign = fields.Text("Signature")
    account_analytic_account_line_id = fields.One2many('account.analytic.account.line', 'account_analytic_account_id', string='Analytic Contract Line')
    analytic_milestone_line_id = fields.One2many('milestone.contract.bookings', 'account_analytic_account_id', string='Analytic Booking Contract Line')

    amount_untaxed = fields.Float("Subtotal", digits=dp.get_precision('Account'), store=True, readonly=True,
                         compute='_compute_amount')
    amount_tax = fields.Float(string='Tax', digits=dp.get_precision('Account'),
        store=True, readonly=True, compute='_compute_amount')
    amount_total = fields.Float("Total", digits=dp.get_precision('Account'), store=True, readonly=True,
                                compute='_compute_amount')
    promo_code = fields.Text('Promo Code')
    payment_terms = fields.Many2many('package.payment.term', string="Payment Term")
    invoice_count = fields.Integer(compute='_compute_invoices', String='Invoices')

    @api.onchange('partner_id')
    def on_change_partner_id(self):
        if self.partner_id:
            self.bride_firstname = self.partner_id.bride_firstname
            self.bride_lastname = self.partner_id.bride_lastname
            self.bride_email = self.partner_id.bride_email
            self.bride_phone = self.partner_id.bride_phone
            self.bride_street = self.partner_id.bride_street
            self.bride_street2 = self.partner_id.bride_street2
            self.bride_city = self.partner_id.bride_city
            self.bride_state_id = self.partner_id.bride_state_id.id
            self.bride_zip = self.partner_id.bride_zip
            self.bride_country_id = self.partner_id.bride_country_id.id
            self.groom_firstname = self.partner_id.groom_firstname
            self.groom_lastname = self.partner_id.groom_lastname
            self.groom_email = self.partner_id.groom_email
            self.groom_phone = self.partner_id.groom_phone
            self.groom_street = self.partner_id.groom_street
            self.groom_street2 = self.partner_id.groom_street2
            self.groom_city = self.partner_id.groom_city
            self.groom_state_id = self.partner_id.groom_state_id.id
            self.groom_zip = self.partner_id.groom_zip
            self.groom_country_id = self.partner_id.groom_country_id.id
            self.bridal_specialist = self.partner_id.bridal_specialist.id
            self.user_id = self.partner_id.bridal_advisor.id
            self.user_id2 = self.partner_id.bridal_advisor2.id
            self.customer_id = self.partner_id.customer_id

    @api.multi
    def get_invoices(self):
        invoice_ids = self.env['account.invoice'].search([('account_analytic_account_id', '=', self.id)])
        if invoice_ids:
            view_id = self.env.ref('account.invoice_tree').id
            form_view_id = self.env.ref('account.invoice_form').id
            context = self._context.copy()
            return {
                'name': _('Invoices'),
                'view_type':'form',
                'view_mode':'tree',
                'res_model':'account.invoice',
                'view_id':view_id,
                'views':[(view_id,'tree'),(form_view_id,'form')],
                'type':'ir.actions.act_window',
                'domain':[('id','in',invoice_ids and invoice_ids.ids)],
                'target':'current',
                'context':context,
            }
        else:
            raise Warning("Not any invoice for this contract.")

    @api.multi
    def action_validate(self):
        if not self.agree_bool:
            raise Warning(_("I agree and accept the contract terms and conditions fields are not filled"))
        self.state = 'validate'
        if not self.partner_id:
            raise Warning(_('Please select Customer'))
        if not self.partner_id.property_account_receivable_id:
            raise Warning(_('Please Add account for customer %s') % self.partner_id.name)
        line_dict = []
        tax_ids = []
        if self.account_analytic_account_line_id:
            invoice_id = self.env['account.invoice'].create({'partner_id':self.partner_id and self.partner_id.id,
                            'account_id': self.partner_id.property_account_receivable_id.id,
                            'type':'out_invoice',
                            'account_analytic_account_id':self.id,
                            'analytic_contract_id': self.id,
                            })
            for line in self.account_analytic_account_line_id:
                if not line.product_id.property_account_income_id:
                    if not line.product_id.categ_id.property_account_income_categ_id :
                        raise Warning(_('Please select account for Product %s') % line.product_id.name)
                account_id = line.product_id.property_account_income_id.id or line.product_id.categ_id.property_account_income_categ_id.id
                tax_ids = [tax.id for tax in line.tax_ids]
                self.env['account.invoice.line'].create({'product_id':line.product_id and line.product_id.id or False,
                                        'quantity':line.qty,
                                        'price_unit':line.price,
                                        'name':line.product_id and line.product_id.description or line.product_id.name,
                                        'uom_id': line.product_id and line.product_id.uom_id and line.product_id.uom_id.id or False,
                                        'account_id': account_id,
                                        'account_analytic_id':self.id,
                                        'invoice_id':invoice_id and invoice_id.id,
                                        'invoice_line_tax_ids':[(6,0,tax_ids)]
                                        })
            if tax_ids:
                invoice_id.compute_taxes()

    @api.multi
    def write(self, values):
        if self.state == 'draft':
            values.update({'date':datetime.today().date()})
        res = super(account_analytic_account, self).write(values)
        if (not values.get('bride_firstname', False) and not self.bride_firstname):
            raise Warning(_("Bride's First Name fields are not correctly filled"))
        if (not values.get('groom_firstname', False) and not self.groom_firstname):
            raise Warning(_("Groom's First Name fields are not correctly filled"))
        if (not values.get('bride_lastname', False) and not self.bride_lastname):
            raise Warning(_("Bride's Last Name fields are not correctly filled"))
        if (not values.get('groom_lastname', False) and not self.groom_lastname):
            raise Warning(_("Groom's Last Name fields are not correctly filled"))
        if values.get('groom_lastname', False):
            has_name = any(char.isdigit() for char in values.get('groom_lastname', False))
            if has_name:
                raise Warning(_("Groom's Last Name fields are not correctly filled"))
        if (not values.get('bride_phone', False) and not self.bride_phone) and (not values.get('groom_phone', False) and not self.groom_phone):
            raise Warning(_("Bride's Phone or Groom's Phone fields are not correctly filled"))
        # if not self.user_id and not values.get('user_id', False):
        #     raise Warning(_("Bridal Advisor fields are not filled"))
        if not self.date and not values.get('date', False):
            raise Warning(_("Contract Date fields are not filled"))
        return res

    @api.model
    def create(self, values):
        if values.get('bride_firstname', False):
            has_name = any(char.isdigit() for char in values.get('bride_firstname', False))
            if has_name:
                raise Warning(_("Bride's First Name fields are not correctly filled"))
        if values.get('bride_lastname', False):
            has_name = any(char.isdigit() for char in values.get('bride_lastname', False))
            if has_name:
                raise Warning(_("Bride's Last Name fields are not correctly filled"))

        if values.get('groom_firstname', False):
            has_name = any(char.isdigit() for char in values.get('groom_firstname', False))
            if has_name:
                raise Warning(_("Groom's First Name fields are not correctly filled"))
        if values.get('groom_lastname', False):
            has_name = any(char.isdigit() for char in values.get('groom_lastname', False))
            if has_name:
                raise Warning(_("Groom's Last Name fields are not correctly filled"))

        if not values.get('bride_email', False) and not values.get('groom_email', False):
            raise Warning(_("Bride's Email Or Groom's Emailfields are not correctly filled"))

        if not values.get('bride_phone', False) and not values.get('groom_phone', False):
            raise Warning(_("Bride's Phone fields are not correctly filled"))
        res = super(account_analytic_account, self).create(values)
        if not res.bride_firstname and not res.groom_firstname:
            raise Warning(_("Bride's First Name or Groom's First Name fields are not filled"))
        if not res.groom_lastname and not res.bride_lastname:
            raise Warning(_("Bride's Last Name or Groom's Last Name fields are not filled"))
        if not res.groom_email and not res.bride_email:
            raise Warning(_("Bride's Email or Groom's Email fields are not filled"))
        if not res.groom_phone and not res.bride_phone:
            raise Warning(_("Bride's Phone or Groom's Phone fields are not filled"))
        # if not res.user_id:
        #     raise Warning(_("Bridal Advisor fields are not filled"))
        if not res.date:
            raise Warning(_("Contract Date fields are not filled"))
        return res


class account_analytic_account_line(models.Model):
    _name = 'account.analytic.account.line'

    @api.one
    @api.depends('price', 'tax_ids', 'qty',
        'product_id')
    def _compute_price(self):
        taxes = self.tax_ids.compute_all(self.price, self.currency_id, product=self.product_id, partner=self.account_analytic_account_id.partner_id)
        price_subtotal = 0
        if taxes:
            price_subtotal = taxes['total_included']
        price_subtotal = self.qty * price_subtotal
        if self.account_analytic_account_id:
            self.price_subtotal = self.account_analytic_account_id.currency_id.round(price_subtotal)

    # @api.onchange('qty')
    # @api.depends('qty')
    # def _update_price(self):
    #     if self.product_id and self.product_id.lst_price and self.qty and self.qty != 0:
    #         self.price = self.qty * self.product_id.lst_price

    @api.model
    def _default_currency(self):
        if self.account_analytic_account_id and self.account_analytic_account_id.company_id:
            self.currency_id = self.account_analytic_account_id.company_id.currency_id.id

    line_type = fields.Selection([('package', 'Package'), ('a_la_carte', 'A la carte')], string='Type')
    categ_id = fields.Many2one('product.category',string='Category')
    product_id = fields.Many2one('product.product',string='Product')
    qty = fields.Integer(string='Quantity', digits= dp.get_precision('Product Unit of Measure'),
        required=True, default=1)
    tax_ids = fields.Many2many('account.tax', string='Taxes')
    price = fields.Float('Price', related="product_id.lst_price",
                         default=0.0, digits=dp.get_precision('Product UoS'))
    price_subtotal = fields.Float(string='Amount', digits= dp.get_precision('Account'),
        store=True, readonly=True, compute='_compute_price')
    currency_id = fields.Many2one('res.currency', string='Currency',
        required=False, readonly=True,
        default=_default_currency, track_visibility='always')
    account_analytic_account_id = fields.Many2one('account.analytic.account',string='Analytic Contract')


    @api.onchange('product_id')
    def on_change_product_id(self):
        if self.product_id and self.product_id.taxes_id:
            self.tax_ids = self.product_id.taxes_id.ids
