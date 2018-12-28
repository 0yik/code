from odoo import models, fields, api

class stock_picking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def do_new_transfer(self):
        res = super(stock_picking, self).do_new_transfer()
        return res

    @api.multi
    def do_transfer(self):
        res = super(stock_picking, self).do_transfer()
        # purchase_id = self.env['purchase.order'].search([]).filtered(lambda a: self.id in a.picking_ids.ids)
        if self.state == 'done' and self.purchase_id:
            data = {
                'type'          : 'in_invoice',
                'credit_note'   : False,
                'partner_id'    : self.purchase_id.partner_id.id or False,
                'partner_ref'   : self.purchase_id.partner_ref or '',
                'purchase_id'   : self.purchase_id.id or False,
                'branch_id'     : self.purchase_id.branch_id.id or False,
                'date_invoice'  : self.purchase_id.date_order[0:10],
                'date_due'      : self.purchase_id.date_planned[0:10],
                'currency_id'   : self.purchase_id.currency_id.id or False,
                'company_id'    : self.purchase_id.company_id.id or False,
                'comment'       : self.purchase_id.notes or '',
                'invoice_line_ids'    : [(0,0,
                                          {
                                             'product_id'   : line.product_id.id or False,
                                             'name'         : line.name or '',
                                             'account_analytic_id' : line.account_analytic_id.id or False,
                                             'quantity'     : line.product_qty,
                                             'price_unit'   : line.price_unit,
                                             'uom_id'   : line.product_uom.id or False,
                                             'invoice_line_tax_ids'   : [(6,0,line.taxes_id.ids)],
                                             'analytic_tag_ids'   : [(6,0,line.analytic_tag_ids.ids)],
                                             'account_id'   : line.product_id.categ_id.property_account_expense_categ_id.id or self.env['account.account'].search([('name','=','Expenses')],limit=1).id,
                                          }) for line in self.purchase_id.order_line],
            }
            data.update(self.env['account.invoice'].default_get(['journal_id','reference_type']))
            vendor_bill_id = self.env['account.invoice'].create(data)
            if self.purchase_id.order_line:
                for line in self.purchase_id.order_line:
                    line.write({'invoice_lines':[(4,inl.id) for inl in vendor_bill_id.invoice_line_ids]})
        return res