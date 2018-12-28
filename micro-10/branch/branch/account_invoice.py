# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2014-Today BrowseInfo (<http://www.browseinfo.in>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from openerp import api, fields, models, _


class account_move(models.Model):
    _inherit  = 'account.move'

    branch_id=fields.Many2one('res.branch', 'Branch',  )
#     def _create_account_move_line(self, move, credit_account_id, debit_account_id, journal_id):
#         quant_cost_qty = defaultdict(lambda: 0.0)
#         for quant in self:
#             quant_cost_qty[quant.cost] += quant.qty
#     
#         AccountMove = self.env['account.move']
#         for cost, qty in quant_cost_qty.iteritems():
#             move_lines = move._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id)
#             if move_lines:
#                 date = self._context.get('force_period_date', fields.Date.context_today(self))
#                 new_account_move = AccountMove.create({
#                     'journal_id': journal_id,
#                     'line_ids': move_lines,
#                     'date': date,
#                     'ref': move.picking_id.name})
#                 new_account_move.post()
 

class account_move_line(models.Model):
 	_inherit  = 'account.move.line'

 	branch_id=fields.Many2one('res.branch', 'Branch',  )

class account_invoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_move_create(self):
        """ Creates invoice related analytics and financial move lines """
        account_move = self.env['account.move']
        for inv in self:
            if not inv.journal_id.sequence_id:
                raise UserError(_('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line_ids:
                raise UserError(_('Please create some invoice lines.'))
            if inv.move_id:
                continue

            ctx = dict(self._context, lang=inv.partner_id.lang)

            if not inv.date_invoice:
                inv.with_context(ctx).write({'date_invoice': fields.Date.context_today(self)})
            date_invoice = inv.date_invoice
            company_currency = inv.company_id.currency_id

            # create move lines (one per invoice line + eventual taxes and analytic lines)
            iml = inv.invoice_line_move_line_get()
            iml += inv.tax_line_move_line_get()

            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, iml)

            name = inv.name or '/'
            if inv.payment_term_id:
                totlines = inv.with_context(ctx).payment_term_id.with_context(currency_id=inv.currency_id.id).compute(total, date_invoice)[0]
                res_amount_currency = total_currency
                ctx['date'] = date_invoice
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
                    else:
                        amount_currency = False

                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency
			
                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': inv.account_id.id,
						'branch_id': inv.branch_id.id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
					'branch_id'	:inv.branch_id.id,
                    'account_id': inv.account_id.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'invoice_id': inv.id
                })
            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
            line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
            line = inv.group_lines(iml, line)

            journal = inv.journal_id.with_context(ctx)
            line = inv.finalize_invoice_move_lines(line)

            date = inv.date or date_invoice
            move_vals = {
                'ref': inv.reference,
                'line_ids': line,
                'journal_id': journal.id,
                'date': date,
                'branch_id': inv.branch_id.id,
                'narration': inv.comment,
            }
            ctx['company_id'] = inv.company_id.id
            ctx['invoice'] = inv
            ctx_nolang = ctx.copy()
            ctx_nolang.pop('lang', None)
            move = account_move.with_context(ctx_nolang).create(move_vals)
            for line in move.line_ids:
                if inv.branch_id.id:
                    line.branch_id = inv.branch_id.id
            #---------------------------------------- for line in move.line_ids:
 				#----------------------------------------- if inv.branch_id.id:
				    #------------------------- line.branch_id = inv.branch_id.id
           # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post()
            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'date': date,
                'move_name': move.name,
            }
            inv.with_context(ctx).write(vals)
            return True
        
    @api.multi
    def action_invoice_open(self):
		# lots of duplicate calls to action_invoice_open, so we remove those already open
        to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
        '''if to_open_invoices.filterd(lambda inv: inv.state not in ['proforma2', 'draft']):
			raise UserError(_("Invoice must be in draft or Pro-forma state in order to validate it."))
		to_open_invoices.action_date_assign()
	    to_open_invoices.action_move_create()
		#to write branch of account invoice in account invoice line 
		for inv in self:
		    if inv.branch_id:
		        for line in inv.invoice_line_ids:
			    line.branch_id = inv.branch_id.id'''
        return to_open_invoices.invoice_validate()


class account_invoice_line(models.Model):
    _inherit = 'account.invoice.line'

    @api.model
    def get_move_line_default_branch(self):
        user_pool = self.env['res.users']
        branch_id = user_pool.browse(self.env.uid).branch_id.id  or False
        return branch_id




    branch_id=fields.Many2one('res.branch', 'Branch', default = get_move_line_default_branch )
    


  
       

