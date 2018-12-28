# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError
import xmlrpclib


class SyncServer(models.TransientModel):
    _name = 'sync.server'
    _rec_name = 'url'
    _order = 'id'

    url = fields.Char('URL')
    db = fields.Char('Database')
    username = fields.Char('User Name')
    password = fields.Char('Password')
    active = fields.Boolean('Active', default=True)

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    inv_sync = fields.Boolean('Already Sync', default=False)

    def update_invoice_sync(self):
        # server_conf = eval(self.env['ir.config_parameter'].get_param('inv_sync_server', default='{}'))
        server_conf = self.env['sync.server'].search([], limit=1)
        if not server_conf:
            raise UserError('Sync server not configured. Please contact system administrator')

        invoices = self.filtered(lambda r: not r.inv_sync and r.state == 'draft' and r.type == 'out_invoice')
        try:
            url = server_conf.url
            db = server_conf.db
            username = server_conf.username
            password = server_conf.password
            sock_common = xmlrpclib.ServerProxy(url + '/xmlrpc/common')
            uid = sock_common.login(db, username, password)
            sock = xmlrpclib.ServerProxy(url + '/xmlrpc/object')

            for invoice in invoices:
                invoice_data = {
                    'comment': invoice.comment,
                    'origin': invoice.origin,
                    'partner_bank_id': invoice.partner_bank_id.id,
                    'number': invoice.number,
                    'company_id': invoice.company_id.id,
                    'type': invoice.type,
                    'sent': invoice.sent,
                    'account_id': invoice.account_id.id,
                    'date_invoice': invoice.date_invoice,
                    'payment_term_id': invoice.payment_term_id.id,
                    'fiscal_position_id': invoice.fiscal_position_id.id,
                    'company_currency_id': invoice.company_currency_id.id,
                    'name': invoice.name,
                    'date_due': invoice.date_due,
                    'create_date': invoice.create_date,
                    'reference': invoice.reference,
                    'currency_id': invoice.currency_id.id,
                    'partner_id': invoice.partner_id.id,
                    'journal_id': invoice.journal_id.id,
                    'state': invoice.state,
                    'date': invoice.date,
                    'user_id': invoice.user_id.id,
                    'invoice_line_ids': [
                        (0, 0, {
                            'product_id': il.product_id.id,
                            'name': il.name,
                            'quantity': il.quantity,
                            'price_unit': il.price_unit,
                            'discount': il.discount,
                            'uom_id': il.uom_id.id,
                            'account_id': il.account_id.id,
                            'invoice_line_tax_ids': [(4, t.id) for t in il.invoice_line_tax_ids]
                        }) for il in invoice.invoice_line_ids],
                }
                sock.execute(db, uid, password, 'account.invoice', 'create', invoice_data)
                invoice.inv_sync = True
        except Exception as e:
            print e

class AccountJournal(models.Model):
    _inherit= "account.journal"

    customer = fields.Many2one('res.partner', string='Customer', domain=[('customer', '=', True)])
    receivable_product = fields.Many2one('product.product', 'Receivable Product')
    bank_charge_account = fields.Many2one('account.account', string='Bank Charges Account')
    bank_charge_product = fields.Many2one('product.product', string='Bank Charges Product')
    fixed_amount = fields.Integer('Fixed Amount')
    rate_amount = fields.Float('Rate', digits=(12, 2))

class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    move_id = fields.Many2one('account.move')

    @api.multi
    def button_journal_entries(self):
        context = dict(self._context or {})
        context['journal_id'] = self.journal_id.id
        return {
            'name': _('Journal Entries'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', [self.move_id.id])],
            'context': context,
        }


class PosSession(models.Model):
    _inherit = 'pos.session'

    @api.multi
    def action_pos_session_close(self):
        # Close CashBox
        super(PosSession, self).action_pos_session_close()

        # Create invoices for session
        product_bank_receivable = self.env.ref('invoice_for_bank_pos.product_bank_receivable')
        product_bank_charge = self.env.ref('invoice_for_bank_pos.product_bank_charge')
        current_time = datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        uom = self.env['product.uom'].search([('name', '=', 'Unit(s)')], limit=1)

        if not product_bank_receivable or not product_bank_charge:
            return
        for session in self:
            for st in session.statement_ids:
                bank_charges = st.balance_end_real*st.journal_id.rate_amount/100 + st.journal_id.fixed_amount*len(st.line_ids)
                price_unit = st.balance_end_real
                invoice_line = []
                if st.journal_id.type == 'bank':
                    invoice_line.append([0, 0, {
                            'product_id': st.journal_id.receivable_product.id,
                            'product_uom_qty': 1,
                            'quantity': 1,
                            'product_uom': uom.id,
                            'name': current_time + session.name,
                            'price_unit': price_unit,
                            'price_subtotal': price_unit,
                            'account_id': st.journal_id.bank_charge_account.id,
                        }
                    ])
                    invoice_line.append([0, 0, {
                        'product_id': st.journal_id.bank_charge_product.id,
                        'product_uom_qty': 1,
                        'quantity': 1,
                        'product_uom': uom.id,
                        'name': current_time + session.name,
                        'price_unit': - bank_charges,
                        'price_subtotal': - bank_charges,
                        'account_id': st.journal_id.bank_charge_account.id,
                    }
                    ])
                    invoices = {
                        'partner_id': st.journal_id.customer.id,
                        'date_invoice': datetime.now(),
                        'invoice_line_ids': invoice_line,
                        'reference_type': 'none',
                        'account_id': st.journal_id.customer.property_account_receivable_id.id,
                        'user_id' : session.user_id.id,
                        'company_id' : session.user_id.company_id.id,
                        'currency_id' : session.user_id.company_id.currency_id.id,
                        'type': 'out_invoice',
                        'state': 'draft',
                    }
                    invoice = self.env['account.invoice'].create(invoices)
                    invoice.update_invoice_sync()
                    invoice.write({'state' : 'draft'})

                # Merge journal entries
                account_invoice_line = []
                account_invoice_line.append([0, 0, {
                    'name': '',
                    'ref': st.name + '-' + st.name,
                    'journal_id': st.journal_id.id,
                    'date': st.date,
                    'date_maturity': st.date,
                    'debit': st.balance_end_real,
                    'credit': 0,
                    'quantity': 0,
                    'statement_id': st.id,
                    'account_id': st.journal_id.default_debit_account_id.id,
                }])
                account_invoice_line.append([0, 0, {
                    'name': '',
                    'ref': st.name + '-' + st.name,
                    'journal_id': st.journal_id.id,
                    'date': st.date,
                    'date_maturity': st.date,
                    'debit': 0,
                    'credit': st.balance_end_real,
                    'quantity': 0,
                    'statement_id': st.id,
                    'account_id': st.journal_id.default_credit_account_id.id,
                }])
                move_id = self.env['account.move'].create({
                    'name': st.name + '-' + st.name,
                    'date': st.date,
                    'line_ids': account_invoice_line,
                    'journal_id': st.journal_id.id,
                    'state': 'posted',
                })
                st.write({
                    'move_id': move_id.id
                })
