from odoo import models, fields, api
import math
import datetime

class work_order(models.Model):
    _inherit = 'work.order'

    @api.multi
    def button_validate(self):
        tax_ids = self.env['account.tax'].search([('pph_option', 'in', [22, 23, 24, 25])])
        tax_list = self.purchase_id and self.purchase_line_id and self.purchase_line_id.mapped('taxes_id') or False
        if self.purchase_id and tax_list and any( tax.id in tax_ids.ids for tax in tax_list):
            tax_total = 0
            #create vendor invoice
            vals = {}
            line_vals = {}
            journal_id = self.env['account.invoice']._default_journal()
            vals['partner_id'] = self.partner_id.id
            vals['date_invoice'] = datetime.datetime.now().date()
            vals['account_id'] = self.partner_id.property_account_receivable_id.id
            vals['name'] = self.name
            vals['currency_id'] = self.currency_id.id
            vals['type'] = 'in_invoice'
            vals['journal_id'] = journal_id.id
            vals['purchase_id'] = self.purchase_id.id
            vals['work_order_id'] = self.id
            vals['reference'] = self.purchase_id.partner_ref
            vals['pph_total'] = self.purchase_line_id.product_qty*self.cost*sum((tax_ids & self.purchase_line_id.taxes_id).mapped('amount'))/100
            vals['po_total'] = self.purchase_line_id.product_qty*self.cost*(1+sum((self.purchase_line_id.taxes_id - tax_ids).mapped('amount'))/100) - self.purchase_line_id.product_qty*self.cost*(1+sum((self.purchase_line_id.taxes_id & tax_ids).mapped('amount'))/100)

            line_vals['product_id'] = self.product_id.id
            line_vals['name'] = self.product_id.name
            line_vals['account_id'] = journal_id.default_credit_account_id.id
            line_vals['quantity'] = 1
            line_vals['price_unit'] = self.cost
            line_vals['invoice_line_tax_ids'] = [(6, 0, (self.purchase_line_id.taxes_id-tax_ids).ids)]
            vals['invoice_line_ids'] = [(0, 0, line_vals)]
            invoice_id1 = self.env['account.invoice'].create(vals)
            self.write({'invoice_ids': [(4, invoice_id1.id)]})
            # create pph vendor invoice
            vals = {}
            line_vals = {}
            journal_id = self.env['account.invoice']._default_journal()
            vals['partner_id'] = (tax_ids & self.purchase_line_id.taxes_id).partner_id.id or False
            vals['date_invoice'] = datetime.datetime.now().date()
            vals['account_id'] = self.env['account.tax'].search([('type_tax_use', '=', 'purchase'), ('pph_option', '!=', False)])[-1].account_id.id or False
            vals['name'] = self.name
            vals['currency_id'] = self.currency_id.id
            vals['type'] = 'in_invoice'
            vals['journal_id'] = journal_id.id
            vals['purchase_id'] = self.purchase_id.id
            vals['work_order_id'] = self.id
            vals['reference'] = self.purchase_id.partner_ref
            line_vals['product_id'] = self.env['product.product'].search([('name','=','Customer Tax Payment')],limit=1).id or False
            line_vals['name'] = '%s Customer Tax Payment'%self.purchase_id.name
            line_vals['account_id'] = self.env['account.tax'].search([('type_tax_use', '=', 'purchase'), ('pph_option', '!=', False)])[-1].account_id.id or False
            line_vals['quantity'] = 1
            line_vals['price_unit'] = self.purchase_line_id.product_qty*self.cost*sum((tax_ids & self.purchase_line_id.taxes_id).mapped('amount'))/100
            # line_vals['invoice_line_tax_ids'] = [(6, 0, (tax_ids & self.purchase_line_id.taxes_id).ids)]
            vals['invoice_line_ids'] = [(0, 0, line_vals)]
            invoice_id2 = self.env['account.invoice'].create(vals)

            self.write({'state': 'done', 'invoice_ids': [(4, invoice_id2.id)], 'done_date': datetime.datetime.now().date()})
            # for record in self.purchase_id.order_line:
            #     if any(tax.id in tax_ids.ids for tax in record.taxes_id):
            #         tax_total += record.qty_received*record.price_unit*sum((tax_ids & record.taxes_id).mapped('amount'))/100
            # data = {
            #         'type'          : 'in_invoice',
            #         'partner_id'    : self.purchase_id.partner_id.id or False,
            #         'reference'     : self.purchase_id.partner_ref or '',
            #         'purchase_id'   : self.purchase_id.id or False,
            #         'branch_id'     : self.purchase_id.branch_id.id or False,
            #         'date_invoice'  : self.purchase_id.date_order[0:10],
            #         'currency_id'   : self.purchase_id.currency_id.id or False,
            #         'company_id'    : self.purchase_id.company_id.id or False,
            #         'comment'       : self.purchase_id.notes or 'PPH and %s'%self.purchase_id.name,
            #         'origin'        : self.purchase_id.name,
            #         'pph_total'     : tax_total,
            #         'po_total'      : self.purchase_id.amount_total,
            #         'invoice_line_ids'    : [(0,0,
            #                               {
            #                                  'product_id'   : line.product_id.id or False,
            #                                  'name'         : line.name or '',
            #                                  'quantity'     : line.qty_received,
            #                                  'price_unit'   : line.price_unit,
            #                                  'uom_id'   : line.product_uom.id or False,
            #                                  # 'invoice_line_tax_ids'   : [(6,0,(line.taxes_id - tax_ids).ids )],
            #                                  'invoice_line_tax_ids'   : [(6,0,line.taxes_id.ids )],
            #                                  'analytic_tag_ids'   : [(6,0,line.analytic_tag_ids.ids)],
            #                                  'account_id'   : line.product_id.categ_id.property_account_expense_categ_id.id or self.env['account.account'].search([('name','=','Expenses')],limit=1).id,
            #                                  # 'account_id'   : self.env['account.tax'].search([('type_tax_use', '=', 'purchase'), ('pph_option', '!=', False)])[-1].account_id.id or False,
            #
            #                               }) for line in self.purchase_id.order_line],
            # }
            #
            # data2 = {
            #     'type': 'in_invoice',
            #     'partner_id': self.env['res.partner'].search([('name','=','Kantor Pajak')]).id or False,
            #     'reference': self.purchase_id.partner_ref or '',
            #     'purchase_id': self.purchase_id.id or False,
            #     'branch_id': self.purchase_id.branch_id.id or False,
            #     'date_invoice': self.purchase_id.date_order[0:10],
            #     'currency_id': self.purchase_id.currency_id.id or False,
            #     'company_id': self.purchase_id.company_id.id or False,
            #     'comment': self.purchase_id.notes or 'PPH and %s' % self.purchase_id.name,
            #     'origin': self.purchase_id.name,
            #     'invoice_line_ids': [(0, 0,
            #                           {
            #                               'product_id': self.env['product.product'].search([('name','=','Customer Tax Payment')])[0].id or False,
            #                               'name': '%s Customer Tax Payment'%self.purchase_id.name,
            #                               'quantity': 1,
            #                               'price_unit': tax_total,
            #                               'uom_id': 1,
            #                               # 'account_id'   : line.product_id.categ_id.property_account_expense_categ_id.id or self.env['account.account'].search([('name','=','Expenses')],limit=1).id,
            #                               'account_id': self.env['account.tax'].search([('type_tax_use', '=', 'purchase'), ('pph_option', '!=', False)])[-1].account_id.id or False,
            #
            #                           }) ],
            # }
            # data.update(self.env['account.invoice'].default_get(['journal_id','reference_type','account_id']))
            # if not data.get('account_id',False):
            #     data.update({'account_id': self.env['account.account'].search([('name','=','Hutang Usaha')]).id})
            # data2.update(self.env['account.invoice'].default_get(['journal_id', 'reference_type', 'account_id']))
            # if not data2.get('account_id', False):
            #     # data2.update({'account_id': self.env['account.account'].search([('name', '=', 'Hutang Usaha')]).id})
            #     data2.update({'account_id': self.env['account.tax'].search([('type_tax_use', '=', 'purchase'), ('pph_option', '!=', False)])[-1].account_id.id})
            #
            # vendor_bill_id = self.env['account.invoice'].create(data)
            # vendor_pph_id = self.env['account.invoice'].create(data2)
            # if self.purchase_id.order_line:
            #     for line in self.purchase_id.order_line:
            #         line.write({'invoice_lines':[(4,inl.id) for inl in (vendor_bill_id + vendor_pph_id).mapped('invoice_line_ids')]})
        else:
            vals = {}
            line_vals = {}
            journal_id = self.env['account.invoice']._default_journal()
            vals['partner_id'] = self.partner_id.id
            vals['date_invoice'] = datetime.datetime.now().date()
            vals['account_id'] = self.partner_id.property_account_receivable_id.id
            vals['name'] = self.name
            vals['currency_id'] = self.currency_id.id
            vals['type'] = 'out_invoice'
            vals['journal_id'] = journal_id.id
            vals['purchase_id'] = self.purchase_id.id
            vals['work_order_id'] = self.id
            vals['reference'] = self.purchase_id.partner_ref
            line_vals['product_id'] = self.product_id.id
            line_vals['name'] = self.product_id.name
            line_vals['account_id'] = journal_id.default_credit_account_id.id
            line_vals['quantity'] = 1
            line_vals['price_unit'] = self.cost
            # line_vals['invoice_line_tax_ids'] = [(6,0,self.taxes_id.ids)]
            vals['invoice_line_ids'] = [(0, 0, line_vals)]
            invoice_id = self.env['account.invoice'].create(vals)
            self.write({'state': 'done', 'invoice_ids': [(4, invoice_id.id)], 'done_date': datetime.datetime.now().date()})
        return True

class account_invoice(models.Model):
    _inherit = 'account.invoice'

    pph_total   = fields.Float(string='PPH')
    po_total    = fields.Float(string='Original PO')

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id', 'date_invoice','type')
    def _compute_amount(self):
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(line.amount for line in self.tax_line_ids.filtered(lambda record: not record.tax_id.pph_option))
        self.amount_total = self.amount_untaxed + self.amount_tax
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign

class account_tax(models.Model):
    _inherit ='account.tax'

    partner_id = fields.Many2one('res.partner', 'Parnter', domain=[('supplier', '=', True)])

    def _compute_amount(self, base_amount, price_unit, quantity=1.0, product=None, partner=None):
        """ Returns the amount of a single tax. base_amount is the actual amount on which the tax is applied, which is
            price_unit * quantity eventually affected by previous taxes (if tax is include_base_amount XOR price_include)
        """
        self.ensure_one()
        if self.amount_type == 'fixed':
            # Use copysign to take into account the sign of the base amount which includes the sign
            # of the quantity and the sign of the price_unit
            # Amount is the fixed price for the tax, it can be negative
            # Base amount included the sign of the quantity and the sign of the unit price and when
            # a product is returned, it can be done either by changing the sign of quantity or by changing the
            # sign of the price unit.
            # When the price unit is equal to 0, the sign of the quantity is absorbed in base_amount then
            # a "else" case is needed.
            if base_amount:
                return math.copysign(quantity, base_amount) * self.amount
            else:
                return quantity * self.amount
        if (self.amount_type == 'percent' and not self.price_include) or (self.amount_type == 'division' and self.price_include):
            return base_amount * self.amount / 100
        # if self.amount_type == 'percent' and self.price_include:
        #     return base_amount - (base_amount / (1 + self.amount / 100))
        if self.amount_type == 'percent' and self.price_include:
            return base_amount * self.amount / 100
        if self.amount_type == 'division' and not self.price_include:
            return base_amount / (1 - self.amount / 100) - base_amount