
from odoo import api, fields, models, tools, _


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def _amount_line_tax(self, line, fiscal_position_id):
        res = super(PosOrder, self)._amount_line_tax(line, fiscal_position_id)
        if line and line.is_complimentary:
            return False
        else:
            return res

    def _action_create_invoice_line(self, line=False, invoice_id=False):
        if line and not line.is_complimentary:
            return super(PosOrder, self)._action_create_invoice_line(line, invoice_id)
        InvoiceLine = self.env['account.invoice.line']
        inv_name = line.product_id.name_get()[0][1]
        inv_line = {
            'invoice_id': invoice_id,
            'product_id': line.product_id.id,
            'quantity': line.qty,
            'account_analytic_id': self._prepare_analytic_account(line),
            'name': inv_name,
        }
        # Oldlin trick
        invoice_line = InvoiceLine.sudo().new(inv_line)
        invoice_line._onchange_product_id()
        invoice_line.invoice_line_tax_ids = invoice_line.invoice_line_tax_ids.filtered(lambda t: t.company_id.id == line.order_id.company_id.id).ids
        fiscal_position_id = line.order_id.fiscal_position_id
        if fiscal_position_id:
            invoice_line.invoice_line_tax_ids = fiscal_position_id.map_tax(invoice_line.invoice_line_tax_ids, line.product_id, line.order_id.partner_id)
        invoice_line.invoice_line_tax_ids = invoice_line.invoice_line_tax_ids.ids
        # We convert a new id object back to a dictionary to write to
        # bridge between old and new api
        inv_line = invoice_line._convert_to_write({name: invoice_line[name] for name in invoice_line._cache})
        inv_line.update(price_unit=0, discount=0)
        inv_line.update({'invoice_line_tax_ids': False})
        # invoice_line_tax_ids
        inv = InvoiceLine.sudo().create(inv_line)
        return inv

class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    is_complimentary = fields.Boolean(string="Is Complimentary?")

    @api.multi
    def _get_tax_ids_after_fiscal_position(self):    
        res = super(PosOrderLine, self)._get_tax_ids_after_fiscal_position()
        for line in self:
            if line.is_complimentary:
                line.tax_ids_after_fiscal_position = False
        return res
    

    @api.depends('price_unit', 'tax_ids', 'qty', 'discount', 'product_id')
    def _compute_amount_line_all(self):
        res = super(PosOrderLine, self)._compute_amount_line_all()
        for line in self:
            if line.is_complimentary:
                fpos = line.order_id.fiscal_position_id
                tax_ids_after_fiscal_position = fpos.map_tax(line.tax_ids, line.product_id, line.order_id.partner_id) if fpos else line.tax_ids
                # price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                price = 0
                taxes = tax_ids_after_fiscal_position.compute_all(price, line.order_id.pricelist_id.currency_id, line.qty, product=line.product_id, partner=line.order_id.partner_id)
                line.update({
                    'price_subtotal_incl': taxes['total_excluded'],
                    'price_subtotal': taxes['total_excluded'],
                })
        return res 