# -*- coding: utf-8 -*-

from odoo import api, fields, models

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    @api.model
    def create(self, vals):
        res = super(PaymentTransaction, self).create(vals)
        if res.sale_order_id:
            res.sale_order_id.action_confirm()
            booking_lines = res.sale_order_id.order_line.filtered('booking_line_id')
            deposit_lines = res.sale_order_id.order_line.filtered('is_deposit_for_rent')
            if booking_lines:
                vals = {'partner_id': res.sale_order_id.partner_id.id, 'booking_id': res.sale_order_id.booking_id.id}
                pos_order_lines = []
                for line in booking_lines:
                    pos_order_lines.append((0, 0, {
                        'product_id': line.product_id.id,
                        'qty': line.product_uom_qty,
                        'price_unit': line.price_unit,
                        'tax_ids': [(6, 0, line.tax_id.ids)],
                        'is_ordered': True,
                        'is_booked': True,
                    }))
                for line in deposit_lines:
                    pos_order_lines.append((0, 0, {
                        'product_id': line.product_id.id,
                        'qty': line.product_uom_qty,
                        'price_unit': line.price_unit,
                        'tax_ids': [(6, 0, line.tax_id.ids)],
                    }))

                if pos_order_lines:
                    pos_order = self.env['pos.order'].create({'partner_id': res.sale_order_id.partner_id.id, 'booking_id':res.sale_order_id.booking_id.id,'online_order':True, 'lines': pos_order_lines})
                    journal_to_check = res.acquirer_id.name
                    journal_env = self.env['account.journal']
                    statement_env = self.env['account.bank.statement']
                    journal = journal_env.search([('name','=',journal_to_check)])
                    if not journal:
                        journal = journal_env.create({
                        'name':journal_to_check,
                        'code':journal_to_check.replace(' ',''),
                        'type':'cash',
                        'journal_user':True
                        }).id
                    else:
                        journal = journal[0].id
                    statement_id = statement_env.search([
                                            ('name','=',pos_order.session_id.name),
                                            ('journal_id','=',journal)])
                    if not statement_id:
                        statement_id = statement_env.create({
                        'name':pos_order.session_id.name,
                        'journal_id':journal,
                        'date':fields.date.today(),
                        })
                    else:
                        statement_id = statement_id[0]
                    self.env['account.bank.statement.line'].create({
                    'statement_id':statement_id.id,
                    'amount':pos_order.amount_total,
                    'name':str(pos_order.name)+':',
                    'partner_id':pos_order.partner_id.id,
                    'ref':statement_id.name,
                    'pos_statement_id':pos_order.id,
                    })
                    pos_order.state = 'paid'
                    pos_order.action_pos_order_invoice()

        return res
