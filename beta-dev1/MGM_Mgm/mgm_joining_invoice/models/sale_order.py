from odoo import models, fields, api, _ , exceptions
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
import time

class joining_invoice_popup(models.TransientModel):
    _name = 'joining.invoice'

    sale_ids    = fields.Many2many('sale.order',string='SO Name')
    so_date     = fields.Datetime('SO Date',default=fields.Date.today())
    product_id  = fields.Many2one('product.product',string='Product Name',readonly=True)
    total_qty   = fields.Integer('Total Qty',readonly=True)
    description = fields.Text('Description Summary')
    default_code= fields.Char('Internal Reference',readonly=True)

    @api.model
    def default_get(self, fields):
        res = super(joining_invoice_popup, self).default_get(fields)
        if self._context.get('active_ids',False) and self._context.get('active_model',False) == 'sale.order':
            sale_ids = self.env['sale.order'].browse(self._context.get('active_ids'))
            if any(sale.state != 'sale' for sale in sale_ids):
                raise ValidationError(_("Joining Invoice can be use for SO that have status Sale Order"))
            if len(sale_ids.mapped('partner_id')) != 1:
                raise ValidationError(_("The Joining Invoice need be same customer!"))
            product = []
            for order in sale_ids:
                product.append(order.order_line.mapped('product_id').ids)
            if not set.intersection(*map(set, product)):
                raise ValidationError(_("Please make sure have product in the selected SO"))
            else:
                product = list(set.intersection(*map(set, product)))
                res['sale_ids'] = [(6, 0, self._context.get('active_ids', False))]
                res['so_date'] = max(sale_ids.mapped('date_order'))
                if len(product) == 1:
                    product_id = self.env['product.product'].browse(product)
                    res['product_id']   = product_id.id
                    res['default_code'] = product_id.default_code
                    lines    = self.env['sale.order.line'].search([('order_id','in',sale_ids.ids),('product_id','in',product_id.ids)])
                    res['total_qty'] = sum(lines.mapped('product_uom_qty'))
                else:
                    raise ValidationError(_("Product in the selected SO should be the same"))
        return res

    @api.multi
    def joining_invoice(self):
        return {
            'name': '',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.advance.payment.inv',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id'  : self.env.ref('mgm_joining_invoice.view_sale_advance_payment_joining_invoice').id,
            'target': 'new',
            'context'   : {'sale_ids':self.sale_ids.ids,
                           'sale_model':'sale.order',
                           'product_id':self.product_id.id,
                           'total_qty':self.total_qty,
                           'default_code'  : self.default_code,
                           'so_date'    : self.so_date,
                           'description' : self.description
                           }
        }

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    @api.multi
    def create_invoices_inherit(self):
        sale_orders = self.env['sale.order'].browse(self._context.get('sale_ids', []))
        self = self.with_context(rate=self.rate, currency_id=self.currency_to_id.id)
        if self.advance_payment_method == 'delivered':
            invoice = sale_orders.with_context(rate=self.rate, currency_id=self.currency_to_id.id).action_invoice_create_joining()

        elif self.advance_payment_method == 'all':
            invoice = sale_orders.with_context(rate=self.rate, currency_id=self.currency_to_id.id).action_invoice_create_joining(final=True)

        else:
            # Create deposit product if necessary
            # if not self.product_id:
            #     vals = self._prepare_deposit_product()
            #     self.product_id = self.env['product.product'].create(vals)
            #     self.env['ir.values'].sudo().set_default('sale.config.settings', 'deposit_product_id_setting',
            #                                              self.product_id.id)

            self.product_id = self.env['product.product'].browse(self._context.get('product_id', False))
            sale_line_obj = self.env['sale.order.line']

            # for order in sale_orders:
            #     if self.advance_payment_method == 'percentage':
            #         if self.rate:
            #             amount = (order.amount_untaxed * self.rate) * (self.amount * self.rate) / 100
            #         else:
            #             amount = order.amount_untaxed * self.amount / 100
            #     else:
            #         if self.rate:
            #             amount = self.amount * self.rate
            #         else:
            #             amount = self.amount
            #
            #     if self.product_id.invoice_policy != 'order':
            #         raise UserError(_(
            #             'The product used to invoice a down payment should have an invoice policy set to "Ordered quantities". Please update your deposit product to be able to create a deposit invoice.'))
            #     if self.product_id.type != 'service':
            #         raise UserError(_(
            #             "The product used to invoice a down payment should be of type 'Service'. Please use another product or update this product."))
            #     taxes = self.product_id.taxes_id.filtered(
            #         lambda r: not order.company_id or r.company_id == order.company_id)
            #     if order.fiscal_position_id and taxes:
            #         tax_ids = order.fiscal_position_id.map_tax(taxes).ids
            #     else:
            #         tax_ids = taxes.ids
            #     context = {'lang': order.partner_id.lang}
            #
            #     so_line = sale_line_obj.create({
            #         'name': _('Advance: %s') % (time.strftime('%m %Y'),),
            #         'price_unit': amount,
            #         'product_uom_qty': 0.0,
            #         'order_id': order.id,
            #         'discount': 0.0,
            #         'product_uom': self.product_id.uom_id.id,
            #         'product_id': self.product_id.id,
            #         'tax_id': [(6, 0, tax_ids)],
            #     })

                # del context
            # invoice = self._create_invoice_inherit()
            invoice = sale_orders.with_context(rate=self.rate,currency_id=self.currency_to_id.id).action_invoice_create_joining()

        if self.rate:
            # 'name': datetime.today()
            self.env['res.currency.rate'].create({'name': self.date,
                                                  'rate': self.rate,
                                                  'currency_id': self.currency_to_id.id})
        # if self._context.get('open_invoices', False):
        #     return sale_orders.action_view_invoice()
        # return {'type': 'ir.actions.act_window_close'}
        return {
            'name': 'Customer Invoice',
            'type': 'ir.actions.act_window',
            'res_model': 'account.invoice',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('account.invoice_form').id,
            'res_id': invoice.id or []
        }

    @api.multi
    def _create_invoice_inherit(self, order, so_line, amount):
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
                _(
                    'There is no income account defined for this product: "%s". You may have to install a chart of account from Accounting app, settings menu.') %
                (self.product_id.name,))

        if self.amount <= 0.00:
            raise UserError(_('The value of the down payment amount must be positive.'))
        context = {'lang': order.partner_id.lang}
        if self.advance_payment_method == 'percentage':
            # change percentage anount if rate is available
            if self.advance_payment_method == 'percentage':
                if self.rate:
                    amount = (order.amount_untaxed * self.rate) * (self.amount) / 100
                    name = _("Down payment of %s%%") % (self.amount)
                else:
                    amount = order.amount_untaxed * self.amount / 100
                    name = _("Down payment of %s%%") % (self.amount,)
        else:
            # change anount if rate is available
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
        # change currency id if rate is avilable
        if self.rate:
            exchange_rate = amount
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
    def action_invoice_create_joining(self, grouped=False, final=False):
        """
        Create the invoice associated to the SO.
        :param grouped: if True, invoices are grouped by SO id. If False, invoices are grouped by
                        (partner_invoice_id, currency)
        :param final: if True, refunds will be generated if necessary
        :returns: list of created invoices
        """
        inv_obj = self.env['account.invoice']
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        total_qty  = self._context.get('total_qty',0)
        product_id = self._context.get('product_id',False)
        sale_ids    = self._context.get('sale_ids',False)
        so_date     = self._context.get('so_date',False)
        default_code     = self._context.get('default_code',False)
        rate        = self._context.get('rate',0)
        currency_id = self._context.get('currency_id',False)
        order_ids    = self.env['sale.order'].browse(self._context.get('sale_ids',False))
        product     =  self.env['product.product'].browse(self._context.get('product_id',False))
        description = self._context.get('description', False) or product.name
        if total_qty <= 0:
            raise UserError(_('There is no invoicable line.'))
        if self._context.get('rate'):
            rate = self._context.get('rate')
            currency_id = self._context.get('currency_id')
        price_product = product.lst_price or 0
        if rate > 0.0:
            exchange_rate = total_qty * product.lst_price * rate
            rate_currency_id = currency_id
            price_product = product.lst_price * rate
        else:
            exchange_rate = 0.0
            rate_currency_id = order_ids[0].pricelist_id.currency_id.id
        journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
        # number = self.env['account.invoice'].default_get(['number'])['number']
        name = ''
        count = 1
        for s in order_ids:
            name += s.name
            if len(order_ids) >count:
                name += ','
            count +=1
        invoice_vals = {
            # 'name': name or '',
            'origin': name,
            'exchange_rate': rate,
            'type': 'out_invoice',
            'account_id': order_ids[0].partner_invoice_id.property_account_receivable_id.id,
            'partner_id': order_ids[0].partner_invoice_id.id,
            'partner_shipping_id': order_ids[0].partner_shipping_id.id,
            'journal_id': journal_id,
            'currency_id': rate_currency_id,
            'payment_term_id': order_ids[0].payment_term_id.id,
            'fiscal_position_id': order_ids[0].fiscal_position_id.id or order_ids[0].partner_invoice_id.property_account_position_id.id,
            'company_id': order_ids[0].company_id.id,
            'user_id': self._uid,
            'date_invoice':fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'product_id': product.id,
                'name': description,
                'quantity': total_qty,
                'price_unit':price_product,
                'account_id':order_ids[0].partner_invoice_id.property_account_receivable_id.id,
            })]
        }
        invoice = inv_obj.create(invoice_vals)
        for sale in order_ids:
            sale.write({'invoice_status': 'to invoice','invoice_ids': [(4,invoice.id)]})
        return invoice