from odoo import api, fields, models, _
import time
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT

from datetime import datetime


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    @api.model
    def _so_currency(self):
        so_id = self._context.get('active_id')
        so_record = self.env['sale.order'].browse(so_id)
        currency_id = so_record.pricelist_id.currency_id
        return currency_id
        
    @api.model
    def _cur_idr(self):
        currency_record = self.env['res.currency'].search([('name', '=','IDR')], limit=1)
        currency_to_id = currency_record.id
        return currency_to_id

    currency_id = fields.Many2one('res.currency', string='Currency From', default=_so_currency)
    currency_to_id = fields.Many2one('res.currency', string='Currency To', default=_cur_idr)
    rate = fields.Float(string='Rate')
    date = fields.Datetime('Date', default=fields.Datetime.now)

    
    @api.multi
    def create_invoices(self):
        if self.rate > 0.0 and self.currency_id.id == self.currency_to_id.id:
            raise UserError(_("Currency From and Currency To both are same, so Exchange rate should be 0.0"))

        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))

        if self.advance_payment_method == 'delivered':
            if self.rate:
                rate_new = self.rate
                currency_to_id = self.currency_to_id.id
                sale_orders.with_context(rate= self.rate,currency_id=self.currency_to_id.id).action_invoice_create()
            else:
                sale_orders.action_invoice_create()
                
        elif self.advance_payment_method == 'all':
            if self.rate:
                rate_new = self.rate
                currency_to_id = self.currency_to_id.id
                sale_orders.with_context(rate= self.rate,currency_id=self.currency_to_id.id).action_invoice_create(final=True)
            else:
                rate_new = 0.0
                currency_to_id = False
                grouped=False
                sale_orders.action_invoice_create(final=True)

        else:
            # Create deposit product if necessary
            if not self.product_id:
                vals = self._prepare_deposit_product()
                self.product_id = self.env['product.product'].create(vals)
                self.env['ir.values'].sudo().set_default('sale.config.settings', 'deposit_product_id_setting', self.product_id.id)

            sale_line_obj = self.env['sale.order.line']

            for order in sale_orders:
                if self.advance_payment_method == 'percentage':
                    if self.rate:
                        amount = (order.amount_untaxed * self.rate) * (self.amount * self.rate) / 100
                    else:
                        amount = order.amount_untaxed * self.amount / 100
                else:
                    if self.rate:
                        amount = self.amount * self.rate
                    else:
                        amount = self.amount
                    
                if self.product_id.invoice_policy != 'order':
                    raise UserError(_('The product used to invoice a down payment should have an invoice policy set to "Ordered quantities". Please update your deposit product to be able to create a deposit invoice.'))
                if self.product_id.type != 'service':
                    raise UserError(_("The product used to invoice a down payment should be of type 'Service'. Please use another product or update this product."))
                taxes = self.product_id.taxes_id.filtered(lambda r: not order.company_id or r.company_id == order.company_id)
                if order.fiscal_position_id and taxes:
                    tax_ids = order.fiscal_position_id.map_tax(taxes).ids
                else:
                    tax_ids = taxes.ids
                context = {'lang': order.partner_id.lang}
                
                so_line = sale_line_obj.create({
                    'name': _('Advance: %s') % (time.strftime('%m %Y'),),
                    'price_unit': amount,
                    'product_uom_qty': 0.0,
                    'order_id': order.id,
                    'discount': 0.0,
                    'product_uom': self.product_id.uom_id.id,
                    'product_id': self.product_id.id,
                    'tax_id': [(6, 0, tax_ids)],
                })
                
                del context
                self._create_invoice(order, so_line, amount)
                
        if self.rate:
            #'name': datetime.today()
            self.env['res.currency.rate'].create({'name': self.date,
                                                  'rate': self.rate,
                                                  'currency_id': self.currency_to_id.id})
        if self._context.get('open_invoices', False):
            return sale_orders.action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}
        
        
    @api.multi
    def _create_invoice(self, order, so_line, amount):
        inv_obj = self.env['account.invoice']
        ir_property_obj = self.env['ir.property']
        account_id = False
        if self.product_id.id:
            account_id = self.product_id.property_account_income_id.id or self.product_id.categ_id.property_account_income_categ_id.id
        if not account_id:
            inc_acc = ir_property_obj.get('property_account_income_categ_id', 'product.category')
            account_id = order.fiscal_position_id.map_account(inc_acc).id if inc_acc else False
        if not account_id:
            raise UserError(
                _('There is no income account defined for this product: "%s". You may have to install a chart of account from Accounting app, settings menu.') %
                (self.product_id.name,))

        if self.amount <= 0.00:
            raise UserError(_('The value of the down payment amount must be positive.'))
        context = {'lang': order.partner_id.lang}
        if self.advance_payment_method == 'percentage':
            #change percentage anount if rate is available
            if self.advance_payment_method == 'percentage':
                if self.rate:
                    amount = (order.amount_untaxed * self.rate) * (self.amount) / 100
                    name = _("Down payment of %s%%") % (self.amount)
                else:
                    amount = order.amount_untaxed * self.amount / 100
                    name = _("Down payment of %s%%") % (self.amount,)
        else:
            #change anount if rate is available
            if self.rate:
                amount = self.amount * self.rate
                name = _('Down Payment')
            else:
                amount = self.amount
                name = _('Down Payment')

        del context
        taxes = self.product_id.taxes_id.filtered(lambda r: not order.company_id or r.company_id == order.company_id)
        if order.fiscal_position_id and taxes:
            tax_ids = order.fiscal_position_id.map_tax(taxes).ids
        else:
            tax_ids = taxes.ids
        #change currency id if rate is avilable
        if self.rate:
            exchange_rate = self.rate
            currency_id = self.currency_to_id.id
        else:
            exchange_rate = 0.0
            currency_id = order.pricelist_id.currency_id.id
        invoice = inv_obj.create({
            'name': order.client_order_ref or order.name,
            'origin': order.name,
            'type': 'out_invoice',
            'reference': False,
            'account_id': order.partner_id.property_account_receivable_id.id,
            'partner_id': order.partner_invoice_id.id,
            'partner_shipping_id': order.partner_shipping_id.id,
            'exchange_rate': exchange_rate,
            'invoice_line_ids': [(0, 0, {
                'name': name,
                'origin': order.name,
                'account_id': account_id,
                'price_unit': amount,
                'quantity': 1.0,
                'discount': 0.0,
                'uom_id': self.product_id.uom_id.id,
                'product_id': self.product_id.id,
                'sale_line_ids': [(6, 0, [so_line.id])],
                'invoice_line_tax_ids': [(6, 0, tax_ids)],
                'account_analytic_id': order.project_id.id or False,
            })],
            'currency_id': currency_id,
            'payment_term_id': order.payment_term_id.id,
            'fiscal_position_id': order.fiscal_position_id.id or order.partner_id.property_account_position_id.id,
            'team_id': order.team_id.id,
            'user_id': order.user_id.id,
            'comment': order.note,
        })
        invoice.compute_taxes()
        invoice.message_post_with_view('mail.message_origin_link',
                    values={'self': invoice, 'origin': order},
                    subtype_id=self.env.ref('mail.mt_note').id)
        return invoice
        

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        """
        Create the invoice associated to the SO.
        :param grouped: if True, invoices are grouped by SO id. If False, invoices are grouped by
                        (partner_invoice_id, currency)
        :param final: if True, refunds will be generated if necessary
        :returns: list of created invoices
        """
        rate = 0.0
        currency_id = False
        if self._context.get('rate'):
            rate = self._context.get('rate')
            currency_id = self._context.get('currency_id')
            
        inv_obj = self.env['account.invoice']
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        invoices = {}
        references = {}
        for order in self:
            group_key = order.id if grouped else (order.partner_invoice_id.id, order.currency_id.id)
            for line in order.order_line.sorted(key=lambda l: l.qty_to_invoice < 0):
                if float_is_zero(line.qty_to_invoice, precision_digits=precision):
                    continue
                if group_key not in invoices:
                    #if rate then custom other wise default 
                    if rate > 0.0:
                        inv_data = order.with_context(rate= rate,currency_id=currency_id)._prepare_invoice()
                    else:
                        inv_data = order._prepare_invoice()
                        
                    invoice = inv_obj.create(inv_data)
                    references[invoice] = order
                    invoices[group_key] = invoice
                elif group_key in invoices:
                    vals = {}
                    if order.name not in invoices[group_key].origin.split(', '):
                        vals['origin'] = invoices[group_key].origin + ', ' + order.name
                    if order.client_order_ref and order.client_order_ref not in invoices[group_key].name.split(', ') and order.client_order_ref != invoices[group_key].name:
                        vals['name'] = invoices[group_key].name + ', ' + order.client_order_ref
                    invoices[group_key].write(vals)
                if line.qty_to_invoice > 0:
                    #pass rate in invoice_line_create 
                    if rate > 0.0:
                        line.with_context(rate= rate,currency_id=currency_id).invoice_line_create(invoices[group_key].id, line.qty_to_invoice,)
                        #line.invoice_line_create(invoices[group_key].id, line.qty_to_invoice, new_rate)
                    else:
                        line.invoice_line_create(invoices[group_key].id, line.qty_to_invoice)
                elif line.qty_to_invoice < 0 and final:
                    #pass rate in invoice_line_create
                    if rate > 0.0:
                        line.with_context(rate= rate,currency_id=currency_id).invoice_line_create(invoices[group_key].id, line.qty_to_invoice,)
                    else:
                        line.invoice_line_create(invoices[group_key].id, line.qty_to_invoice)

            if references.get(invoices.get(group_key)):
                if order not in references[invoices[group_key]]:
                    references[invoice] = references[invoice] | order

        if not invoices:
            raise UserError(_('There is no invoicable line.'))

        for invoice in invoices.values():
            if not invoice.invoice_line_ids:
                raise UserError(_('There is no invoicable line.'))
            # If invoice is negative, do a refund invoice instead
            if invoice.amount_untaxed < 0:
                invoice.type = 'out_refund'
                for line in invoice.invoice_line_ids:
                    line.quantity = -line.quantity
            # Use additional field helper function (for account extensions)
            for line in invoice.invoice_line_ids:
                line._set_additional_fields(invoice)
            # Necessary to force computation of taxes. In account_invoice, they are triggered
            # by onchanges, which are not triggered when doing a create.
            invoice.compute_taxes()
            invoice.message_post_with_view('mail.message_origin_link',
                values={'self': invoice, 'origin': references[invoice]},
                subtype_id=self.env.ref('mail.mt_note').id)
        return [inv.id for inv in invoices.values()]
        
        
    #use in function action_invoice_create and below func create account_invoice
    @api.multi
    def _prepare_invoice(self, currency_id=False, rate=False):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        #stop 
        #order.with_context(rate= rate,currency_id=currency_id)._prepare_invoice()
        rate = 0.0
        currency_id = False
        if self._context.get('rate'):
            rate = self._context.get('rate')
            currency_id = self._context.get('currency_id')
            
        self.ensure_one()
        journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
        if not journal_id:
            raise UserError(_('Please define an accounting sale journal for this company.'))
        #change currency id
        if rate > 0.0:
            exchange_rate = rate
            rate_currency_id = currency_id
        else:
            exchange_rate = 0.0
            rate_currency_id = self.pricelist_id.currency_id.id
        invoice_vals = {
            'name': self.client_order_ref or '',
            'origin': self.name,
            'exchange_rate': exchange_rate,
            'type': 'out_invoice',
            'account_id': self.partner_invoice_id.property_account_receivable_id.id,
            'partner_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'journal_id': journal_id,
            'currency_id': rate_currency_id,
            'comment': self.note,
            'payment_term_id': self.payment_term_id.id,
            'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
            'company_id': self.company_id.id,
            'user_id': self.user_id and self.user_id.id,
            'team_id': self.team_id.id
            
        }
        return invoice_vals    
        
        
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'        
    #use in function action_invoice_create and below func create so_line  
    
    @api.multi
    def invoice_line_create(self, invoice_id, qty):
        """
        Create an invoice line. The quantity to invoice can be positive (invoice) or negative
        (refund).

        :param invoice_id: integer
        :param qty: float quantity to invoice
        """
        rate = 0.0
        if self._context.get('rate'):
            rate = self._context.get('rate')
            currency_id = self._context.get('currency_id')
            
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        created_ids = []
        for line in self:
            if not float_is_zero(qty, precision_digits=precision):
                #if rate available then pass in _prepare_invoice_line
                if rate > 0.0:
                    vals = line.with_context(rate= rate,currency_id=currency_id)._prepare_invoice_line(qty=qty)
                else:
                    vals = line._prepare_invoice_line(qty=qty)
                vals.update({'invoice_id': invoice_id, 'sale_line_ids': [(6, 0, [line.id])]})
                created_ids+=self.env['account.invoice.line'].create(vals)
        return created_ids
                
    @api.multi
    def _prepare_invoice_line(self, qty):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        """
        rate = 0.0
        if self._context.get('rate'):
            rate = self._context.get('rate')
            currency_id = self._context.get('currency_id')
            
        self.ensure_one()
        res = {}
        account = self.product_id.property_account_income_id or self.product_id.categ_id.property_account_income_categ_id
        if not account:
            raise UserError(_('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') %
                (self.product_id.name, self.product_id.id, self.product_id.categ_id.name))

        fpos = self.order_id.fiscal_position_id or self.order_id.partner_id.property_account_position_id
        if fpos:
            account = fpos.map_account(account)
        if rate > 0.0:
            price_unit = self.price_unit * rate
        else:
            price_unit = self.price_unit
        res = {
            'name': self.name,
            'sequence': self.sequence,
            'origin': self.order_id.name,
            'account_id': account.id,
            'price_unit': price_unit,
            'quantity': qty,
            'discount': self.discount,
            'uom_id': self.product_uom.id,
            'product_id': self.product_id.id or False,
            'layout_category_id': self.layout_category_id and self.layout_category_id.id or False,
            'invoice_line_tax_ids': [(6, 0, self.tax_id.ids)],
            'account_analytic_id': self.order_id.project_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
        }
        return res
        
        
class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    exchange_rate = fields.Float('Exchange Rate')

    @api.multi
    def _compute_so_total_amount(self):
        for record in self:
            so_objs = []
            if record.origin:
                so_objs = self.env['sale.order'].search([('name','=',record.origin)], limit=1)
            for so_obj in so_objs:
                if record.exchange_rate:
                    record.invoice_total_amount = so_obj.amount_total * record.exchange_rate
                else:
                    record.invoice_total_amount = so_obj.amount_total