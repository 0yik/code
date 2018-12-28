
from odoo import api, fields, models, _
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError
from lxml import etree
class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    @api.depends('state', 'order_line.invoice_status_dp', 'order_line.state')
    def _get_invoiced_dp(self):
        for order in self:
            # Ignore the status of the deposit product
            deposit_product_id = self.env['purchase.advance.payment.inv']._default_product_id()
            line_invoice_status = [line.invoice_status_dp for line in order.order_line if
                                   line.product_id != deposit_product_id]

            if order.state not in ('purchase', 'done'):
                invoice_status_dp = 'no'
            elif any(invoice_status_dp == 'to invoice' for invoice_status_dp in line_invoice_status):
                invoice_status_dp = 'to invoice'
            elif all(invoice_status_dp == 'invoiced' for invoice_status_dp in line_invoice_status):
                invoice_status_dp = 'invoiced'
            elif all(invoice_status_dp in ['invoiced', 'upselling'] for invoice_status_dp in line_invoice_status):
                invoice_status_dp = 'upselling'
            else:
                invoice_status_dp = 'no'
            order.update({
                'invoice_status_dpp': invoice_status_dp
            })

    invoice_status_dpp = fields.Selection([
        ('upselling', 'Upselling Opportunity'),
        ('invoiced', 'Fully Invoiced'),
        ('to invoice', 'To Invoice'),
        ('no', 'Nothing to Invoice')
    ], string='Invoice Status DP', compute='_get_invoiced_dp', store=True, readonly=True)

    @api.multi
    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a purchase order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
        if not journal_id:
            raise UserError(_('Please define an accounting sale journal for this company.'))
        invoice_vals = {
            'name': self.partner_ref or '',
            'origin': self.name,
            'type': 'in_invoice',
            'account_id': self.partner_id.property_account_receivable_id.id,
            'partner_id': self.partner_id.id,
            'journal_id': journal_id,
            'currency_id': self.currency_id.id,
            'comment': self.notes,
            'payment_term_id': self.payment_term_id.id,
            'fiscal_position_id': self.fiscal_position_id.id or self.partner_id.property_account_position_id.id,
            'company_id': self.company_id.id,
        }
        return invoice_vals


    @api.multi
    def action_bill_create(self, grouped=False, final=False):
        inv_obj = self.env['account.invoice']
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        invoices = {}
        references = {}
        for order in self:
            group_key = order.id if grouped else (order.partner_id.id, order.currency_id.id)
            for line in order.order_line.sorted(key=lambda l: l.qty_to_invoice < 0):
                if float_is_zero(line.qty_to_invoice, precision_digits=precision):
                    continue
                if group_key not in invoices:
                    inv_data = order._prepare_invoice()
                    invoice = inv_obj.create(inv_data)
                    references[invoice] = order
                    invoices[group_key] = invoice
                elif group_key in invoices:
                    vals = {}
                    if order.name not in invoices[group_key].origin.split(', '):
                        vals['origin'] = invoices[group_key].origin + ', ' + order.name
                    if order.partner_ref and order.partner_ref not in invoices[group_key].name.split(
                            ', ') and order.client_order_ref != invoices[group_key].name:
                        vals['name'] = invoices[group_key].name + ', ' + order.client_order_ref
                    invoices[group_key].write(vals)
                if line.qty_to_invoice > 0:
                    line.invoice_line_create(invoices[group_key].id, line.qty_to_invoice)
                elif line.qty_to_invoice < 0 and final:
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
                invoice.type = 'in_refund'
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

    @api.multi
    def button_update_purchase(self):
        purchase_rec = self.env['purchase.order'].search([])
        for po in purchase_rec:
            if not po.invoice_status_dpp:
                po_line_rec = self.env['purchase.order.line'].search([('order_id','=', po.id),
                                                                      ('invoice_status_dp','not in',['invoiced'])])
                if po_line_rec:
                    po.invoice_status_dpp = 'to invoice';


class PurchaseOrderLine(models.Model):

    _inherit = 'purchase.order.line'

    @api.depends('state', 'order_id.state', 'product_qty', 'qty_received', 'qty_to_invoice', 'qty_invoiced')
    def _compute_invoice_status_dp(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for line in self:
            if line.state not in ('purchase', 'done'):
                line.invoice_status_dp = 'no'
            elif not float_is_zero(line.qty_to_invoice, precision_digits=precision):
                line.invoice_status_dp = 'to invoice'
            elif line.state == 'purchase' and line.product_id.invoice_policy == 'order' and \
                    float_compare(line.qty_received, line.product_qty, precision_digits=precision) == 1:
                line.invoice_status_dp = 'upselling'
            elif float_compare(line.qty_invoiced, line.product_qty, precision_digits=precision) >= 0:
                line.invoice_status_dp = 'invoiced'
            else:
                line.invoice_status_dp = 'no'

    invoice_status_dp = fields.Selection([
        ('upselling', 'Upselling Opportunity'),
        ('invoiced', 'Fully Invoiced'),
        ('to invoice', 'To Invoice'),
        ('no', 'Nothing to Invoice')
    ], string='Invoice Status', compute='_compute_invoice_status_dp', store=True, readonly=True, default='no')

    qty_to_invoice = fields.Float(
        compute='_get_to_invoice_qty', string='To Invoice', store=True, readonly=True,
        digits=dp.get_precision('Product Unit of Measure'))

    @api.depends('qty_invoiced', 'qty_received', 'product_qty', 'order_id.state')
    def _get_to_invoice_qty(self):
        """
        Compute the quantity to invoice. If the invoice policy is order, the quantity to invoice is
        calculated from the ordered quantity. Otherwise, the quantity delivered is used.
        """
        for line in self:
            if line.order_id.state in ['purchase', 'done']:
                if line.product_id.invoice_policy == 'order':
                    line.qty_to_invoice = line.product_qty - line.qty_invoiced
                else:
                    line.qty_to_invoice = line.qty_received - line.qty_invoiced
            else:
                line.qty_to_invoice = 0

    @api.multi
    def _prepare_invoice_line(self, qty):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        """
        self.ensure_one()
        res = {}
        account = self.product_id.property_account_income_id or self.product_id.categ_id.property_account_income_categ_id
        if not account:
            raise UserError(
                _('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') %
                (self.product_id.name, self.product_id.id, self.product_id.categ_id.name))

        fpos = self.order_id.fiscal_position_id or self.order_id.partner_id.property_account_position_id
        if fpos:
            account = fpos.map_account(account)

        res = {
            'name': self.name,
            'sequence': self.sequence,
            'origin': self.order_id.name,
            'account_id': account.id,
            'price_unit': self.price_unit,
            'quantity': qty,
            'uom_id': self.product_uom.id,
            'product_id': self.product_id.id or False,
            'invoice_line_tax_ids': [(6, 0, self.taxes_id.ids)],
            'account_analytic_id': self.account_analytic_id.id or False,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
        }
        return res

    @api.multi
    def invoice_line_create(self, invoice_id, qty):
        """
        Create an invoice line. The quantity to invoice can be positive (invoice) or negative
        (refund).

        :param invoice_id: integer
        :param qty: float quantity to invoice
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for line in self:
            if not float_is_zero(qty, precision_digits=precision):
                vals = line._prepare_invoice_line(qty=qty)
                vals.update({'invoice_id': invoice_id, 'purchase_line_ids': [(6, 0, [line.id])]})
                bill_line_id = self.env['account.invoice.line'].create(vals)
                bill_line_id.write({'purchase_line_id': line.id})
