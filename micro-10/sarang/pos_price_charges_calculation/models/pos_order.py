
from odoo import api, fields, models, tools, _

class PosConfig(models.Model):
    _inherit = 'pos.config'

    branch_id = fields.Many2one('res.branch', 'Branch',  )

class PosSession(models.Model):
    _inherit = 'pos.session'

    @api.model
    def create(self, values):
        self = super(PosSession, self).create(values)
        self.branch_id = self.config_id.branch_id.id
        return self

class PosOrder(models.Model):
    _inherit = "pos.order"

    service_charge = fields.Boolean('Apply Service Charge?')
    tax_charge_value = fields.Boolean(string="Apply Tax Charge?")
    amount_service = fields.Float(compute='_compute_amount_all', string='Service Charge', digits=0)
    rounding = fields.Float(compute='_compute_amount_all', string='Rounding', digits=0)
    all_free = fields.Boolean('Apply All Free?')

    
    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        res['all_free'] = ui_order.get('all_free')
        res['service_charge'] = ui_order.get('service_charge')
        res['tax_charge_value'] = ui_order.get('tax_charge_value') > 0 and True or False
        res['branch_id'] = ui_order.get('pos_session_id') and self.env['pos.session'].browse(ui_order.get('pos_session_id')).branch_id.id or False 
        return res

    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a pos order.
        """
        result = super(PosOrder, self)._prepare_invoice()
        result['service_charge'] = self.service_charge
        result['pos_order_id'] = self.id
        return result 

    def _action_create_invoice_line(self, line=False, invoice_id=False):
        inv_line = super(PosOrder, self)._action_create_invoice_line(line=line, invoice_id=invoice_id)
        # inv_line.service_charge_value = line.service_charge_value
        # inv_line.subtotal_service_charge_value = line.subtotal_service_charge_value
        if line.is_complimentary:
            inv_line.price_unit = 0
            inv_line.invoice_line_tax_ids = False

        return inv_line

    @api.depends('statement_ids', 'lines.price_subtotal_incl', 'lines.discount', 'service_charge')
    def _compute_amount_all(self):
        super(PosOrder, self)._compute_amount_all()
        for order in self:
            sub_total_without_disc = sum(line.price_unit*line.qty for line in order.lines if not line.is_complimentary)
            sub_total = sum(line.price_subtotal for line in order.lines if not line.is_complimentary)
            '''sub_total_without_disc = sum(line.price_unit*line.qty for line in order.lines if not line.is_complimentary and line.state == 'Confirmed')
            sub_total = sum(line.price_subtotal for line in order.lines if not line.is_complimentary and line.state == 'Confirmed')'''
            currency = order.pricelist_id.currency_id
            order.amount_service = 0.0
            if order.service_charge and order.branch_id.service_charge_id:
                if order.branch_id.service_charge_id.service_charge_computation=='fixed':
                    order.amount_service = order.branch_id.service_charge_id.amount
                else:
                    order.amount_service = (sub_total*order.branch_id.service_charge_id.amount)/100
            order.amount_tax = 0
            if order.tax_charge_value:
                tax = self.env.ref('pos_price_charges_calculation.pb1_tax_template')
                if tax.amount_type=='fixed':
                    order.amount_tax = tax.amount
                else:
                    order.amount_tax = currency.round((sub_total+order.amount_service)*tax.amount/100)
            order.rounding = (sub_total+order.amount_service+order.amount_tax) % 500 if sub_total > 500 else 0
            order.amount_total = (sub_total+order.amount_service+order.amount_tax) - order.rounding

    def _create_account_move_line(self, session=None, move=None):
        # Tricky, via the workflow, we only have one id in the ids variable
        """Create a account move line of order grouped by products or not."""
        IrProperty = self.env['ir.property']
        ResPartner = self.env['res.partner']

        if session and not all(session.id == order.session_id.id for order in self):
            raise UserError(_('Selected orders do not have the same session!'))

        grouped_data = {}
        have_to_group_by = session and session.config_id.group_by or False
        rounding_method = session and session.config_id.company_id.tax_calculation_rounding_method

        for order in self.filtered(lambda o: not o.account_move or o.state == 'paid'):
            current_company = order.sale_journal.company_id
            account_def = IrProperty.get(
                'property_account_receivable_id', 'res.partner')
            order_account = order.partner_id.property_account_receivable_id.id or account_def and account_def.id
            partner_id = ResPartner._find_accounting_partner(order.partner_id).id or False
            if move is None:
                # Create an entry for the sale
                journal_id = self.env['ir.config_parameter'].sudo().get_param(
                    'pos.closing.journal_id_%s' % current_company.id, default=order.sale_journal.id)
                move = self._create_account_move(
                    order.session_id.start_at, order.name, int(journal_id), order.company_id.id)

            def insert_data(data_type, values):
                # if have_to_group_by:
                values.update({
                    'partner_id': partner_id,
                    'move_id': move.id,
                })

                if data_type == 'product':
                    key = ('product', values['partner_id'], (values['product_id'], tuple(values['tax_ids'][0][2]), values['name']), values['analytic_account_id'], values['debit'] > 0)
                elif data_type == 'tax':
                    key = ('tax', values['partner_id'], values['tax_line_id'], values['debit'] > 0)
                elif data_type == 'counter_part':
                    key = ('counter_part', values['partner_id'], values['account_id'], values['debit'] > 0)
                elif data_type == 'rounding':
                    key = ('counter_part', values['partner_id'], values['account_id'], values['debit'] > 0)
                elif data_type == 'service_charge':
                    key = ('counter_part', values['partner_id'], values['account_id'], values['debit'] > 0)
                else:
                    return

                grouped_data.setdefault(key, [])

                if have_to_group_by:
                    if not grouped_data[key]:
                        grouped_data[key].append(values)
                    else:
                        current_value = grouped_data[key][0]
                        current_value['quantity'] = current_value.get('quantity', 0.0) + values.get('quantity', 0.0)
                        current_value['credit'] = current_value.get('credit', 0.0) + values.get('credit', 0.0)
                        current_value['debit'] = current_value.get('debit', 0.0) + values.get('debit', 0.0)
                else:
                    grouped_data[key].append(values)

            # because of the weird way the pos order is written, we need to make sure there is at least one line,
            # because just after the 'for' loop there are references to 'line' and 'income_account' variables (that
            # are set inside the for loop)
            # TOFIX: a deep refactoring of this method (and class!) is needed
            # in order to get rid of this stupid hack
            assert order.lines, _('The POS order must have lines when calling this method')
            # Create an move for each order line
            cur = order.pricelist_id.currency_id
            for line in order.lines:
                amount = line.price_subtotal

                # Search for the income account
                if line.product_id.property_account_income_id.id:
                    income_account = line.product_id.property_account_income_id.id
                elif line.product_id.categ_id.property_account_income_categ_id.id:
                    income_account = line.product_id.categ_id.property_account_income_categ_id.id
                else:
                    raise UserError(_('Please define income '
                                      'account for this product: "%s" (id:%d).')
                                    % (line.product_id.name, line.product_id.id))

                name = line.product_id.name
                if line.notice:
                    # add discount reason in move
                    name = name + ' (' + line.notice + ')'

                # Create a move for the line for the order line
                insert_data('product', {
                    'name': name,
                    'quantity': line.qty,
                    'product_id': line.product_id.id,
                    'account_id': income_account,
                    'analytic_account_id': self._prepare_analytic_account(line),
                    'credit': ((amount > 0) and amount) or 0.0,
                    'debit': ((amount < 0) and -amount) or 0.0,
                    'tax_ids': [(6, 0, line.tax_ids_after_fiscal_position.ids)],
                    'partner_id': partner_id
                })

            if order.rounding:
                insert_data('rounding', {
                    'name': _('Rounding'),
                    'product_id': False,
                    'quantity': 1,
                    'account_id': order.sale_journal.rounding_account.id or income_account,
                    'credit': ((order.rounding < 0) and -order.rounding) or 0.0,
                    'debit': ((order.rounding > 0) and order.rounding) or 0.0,
                    # 'tax_line_id': tax['id'],
                    'partner_id': partner_id
                })
            if order.service_charge and order.amount_service:
                insert_data('service_charge', {
                    'name': _('Service Charge'),
                    'product_id': False,
                    'quantity': 1,
                    'account_id': order.branch_id.service_charge_id.service_charge_account_id.id or income_account,
                    'credit': ((order.amount_service > 0) and order.amount_service) or 0.0,
                    'debit': ((order.amount_service < 0) and -order.amount_service) or 0.0,
                    # 'tax_line_id': tax['id'],
                    'partner_id': partner_id
                })

            # Create the tax lines
            tax = self.env.ref('pos_price_charges_calculation.pb1_tax_template')
            if tax and order.amount_tax:
                insert_data('tax', {
                    'name': _('Tax') + ' ' + tax['name'],
                    'product_id': False,
                    'quantity': 1,
                    'account_id': tax.account_id.id or income_account,
                    'credit': ((order.amount_tax > 0) and order.amount_tax) or 0.0,
                    'debit': ((order.amount_tax < 0) and -order.amount_tax) or 0.0,
                    'tax_line_id': tax.id,
                    'partner_id': partner_id
                })

            # round tax lines per order
            if rounding_method == 'round_globally':
                for group_key, group_value in grouped_data.iteritems():
                    if group_key[0] == 'tax':
                        for line in group_value:
                            line['credit'] = cur.round(line['credit'])
                            line['debit'] = cur.round(line['debit'])

            # counterpart
            insert_data('counter_part', {
                'name': _("Trade Receivables"),  # order.name,
                'account_id': order_account,
                'credit': ((order.amount_total < 0) and -order.amount_total) or 0.0,
                'debit': ((order.amount_total > 0) and order.amount_total) or 0.0,
                'partner_id': partner_id
            })

            order.write({'state': 'done', 'account_move': move.id})

        all_lines = []
        for group_key, group_data in grouped_data.iteritems():
            for value in group_data:
                all_lines.append((0, 0, value),)
        if move:  # In case no order was changed
            move.sudo().write({'line_ids': all_lines})
            move.sudo().post()
        return True 


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"
           
    is_complimentary = fields.Boolean(string="Is Complimentary?")
    state = fields.Char(string="State")

    @api.multi
    def _get_tax_ids_after_fiscal_position(self):    
        res = super(PosOrderLine, self)._get_tax_ids_after_fiscal_position()
        for line in self:
            line.tax_ids_after_fiscal_position = False
        return res
