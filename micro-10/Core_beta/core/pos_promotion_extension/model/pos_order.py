from odoo import fields, models, api,  _
from odoo.exceptions import UserError
from functools import partial

class pos_order(models.Model):
    _inherit = 'pos.order'

    @api.depends('lines')
    def _get_promotion(self):
        for record in self:
            for line in record.lines:
                if line and line.promotion:
                    record.is_promotion = True
                else:
                    record.is_promotion = False

    @api.depends('lines')
    def _get_discounted_amount(self):
        for record in self:
            promotion_product_id = self.env['product.product'].search([('name', '=', 'Promotion service')])
            for line in record.lines:
                if record.is_promotion and record.config_id and record.config_id.allow_promotion and record.config_id.promotion_ids:
                    for program in record.config_id.promotion_ids:
                        if promotion_product_id and promotion_product_id == line.product_id and program.type == '8_payment_method_discount':
                            record.total_discounted_amount = -(line.price_unit)

    @api.depends('config_id')
    def _get_promotion_values(self):
        for record in self:
            if record.is_promotion and record.config_id and record.config_id.allow_promotion and record.config_id.promotion_ids:
                for program in record.config_id.promotion_ids:
                    if program.type == '8_payment_method_discount':
                        record.promotion_id = program.id

    is_promotion = fields.Boolean(compute='_get_promotion', string='Promotion', store=True)
    promotion_id = fields.Many2one('pos.promotion', compute='_get_promotion_values', string='Promotion', store=True)
    promotion_type = fields.Selection(related="promotion_id.type", string='Promotion Type', readonly=True, store=True)
    payment_id = fields.Many2one('account.journal', related='promotion_id.payment_method_id', string='Payment Method', store=True, readonly=True)
    total_discounted_amount = fields.Float(compute='_get_discounted_amount', string='Total Discounted Amount', store=True)
    is_promo_invoice = fields.Boolean(string='Is create promotion invoice', default=False)
    promo_invoice_id = fields.Many2one('account.invoice', 'Promo Invoice', readonly=True)

    @api.multi
    def action_pos_order_promo_invoice(self):
        Invoice = self.env['account.invoice']

        partner_id = False
        currency_id = False

        for order in self:
            if order.state != 'paid':
                raise UserError(
                    _('Please create Promo Invoice for the same Partner, Currency and orders with Paid status.'))
            if partner_id and order.partner_id.id != partner_id:
                raise UserError(_('Please create Promo Invoice for the same Partner, Currency and orders with Paid status.'))
            elif not partner_id:
                partner_id = order.partner_id.id

            if order.is_promotion and not order.is_promo_invoice:
                # Force company for all SUPERUSER_ID action
                local_context = dict(self.env.context, force_company=order.company_id.id, company_id=order.company_id.id)
                if order.invoice_id:
                    Invoice += order.invoice_id
                    continue

                if not order.partner_id:
                    raise UserError(_('Please provide a partner for the sale.'))

                invoice = Invoice.new(order._prepare_invoice())
                invoice._onchange_partner_id()
                invoice.fiscal_position_id = order.fiscal_position_id

                inv = invoice._convert_to_write({name: invoice[name] for name in invoice._cache})
                if order.promotion_id and order.promotion_id.type == '8_payment_method_discount':
                    inv['partner_id'] = order.promotion_id.partner_id.id
                new_invoice = Invoice.with_context(local_context).sudo().create(inv)
                message = _("This invoice has been created from the point of sale session: <a href=# data-oe-model=pos.order data-oe-id=%d>%s</a>") % (order.id, order.name)
                new_invoice.message_post(body=message)
                order.write({'promo_invoice_id': new_invoice.id, 'is_promo_invoice': True})
                Invoice += new_invoice

                for line in order.lines:
                    if line.promotion:
                        self.with_context(local_context)._action_create_invoice_line(line, new_invoice.id)

                new_invoice.with_context(local_context).sudo().compute_taxes()
                # this workflow signal didn't exist on account.invoice -> should it have been 'invoice_open' ? (and now method .action_invoice_open())
                # shouldn't the created invoice be marked as paid, seing the customer paid in the POS?
                # new_invoice.sudo().signal_workflow('validate')

        if not Invoice:
            return {}

        return {
            'name': _('Promo Invoice'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('account.invoice_form').id,
            'res_model': 'account.invoice',
            'context': "{'type':'out_invoice'}",
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': Invoice and Invoice.ids[0] or False,
        }

    @api.multi
    def action_view_promo_invoice(self):
        return {
            'name': _('Promo Invoice'),
            'view_mode': 'form',
            'view_id': self.env.ref('account.invoice_form').id,
            'res_model': 'account.invoice',
            'context': "{'type':'out_invoice'}",
            'type': 'ir.actions.act_window',
            'res_id': self.promo_invoice_id.id,
        }

    # @api.multi
    # def action_pos_order_invoice(self):
    #     super(pos_order, self).action_pos_order_invoice()
    #     for order in self:
    #         if order.promotion_id and order.promotion_id.type == '8_payment_method_discount':
    #             order.invoice_id.write({
    #                 'partner_id' : order.promotion_id.partner_id.id
    #             })

pos_order()