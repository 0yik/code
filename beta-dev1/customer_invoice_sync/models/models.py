# -*- coding: utf-8 -*-

from odoo import models, fields, api
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
        url = server_conf.url
        db = server_conf.db
        username = server_conf.username
        password = server_conf.password
        sock_common = xmlrpclib.ServerProxy(url + '/xmlrpc/common')
        uid = sock_common.login(db, username, password)
        sock = xmlrpclib.ServerProxy(url + '/xmlrpc/object')

        for invoice in invoices:
            # invoice_data = {}
            # if invoice.partner_bank_id:
            #     if invoice.partner_id:
            #         partner = sock.execute(db, uid, password, 'res.partner', 'search',
            #                                [('name', '=', invoice.partner_id.name)])
            #         if partner:
            #             invoice_data['partner_id'] = partner[0]
            #         else:
            #             partner_data = {
            #                 'name': invoice.partner_id.name,
            #                 'email': invoice.partner_id.email,
            #                 'phone': invoice.partner_id.phone,
            #                 'mobile': invoice.partner_id.mobile,
            #             }
            #             partner_id = sock.execute(db, uid, password, 'res.partner', 'create', partner_data)
            #             invoice_data['partner_id'] = partner_id
            #
            #     if invoice.partner_bank_id:
            #         partner_bank_id = sock.execute(db, uid, password, 'res.partner.bank', 'search',
            #                                        [('acc_number', '=', invoice.partner_bank_id.acc_number)])
            #         if partner_bank_id:
            #             invoice_data['partner_bank_id'] = partner_bank_id[0]
            #         else:
            #             raise UserError('Bank Account: %s not found in %' % (invoice.partner_bank_id.acc_number, url))
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
                'uom_id': invoice.uom_id.id,
                'invoice_line_ids': [
                    (0, 0, {
                        'product_id': il.product_id.id,
                        'name': il.name,
                        'quantity': il.quantity,
                        'price_unit': il.price_unit,
                        'discount': il.discount,
                        'account_id': il.account_id.id,
                        'invoice_line_tax_ids': [(4, t.id) for t in il.invoice_line_tax_ids]
                    }) for il in invoice.invoice_line_ids],
            }
            sock.execute(db, uid, password, 'account.invoice', 'create', invoice_data)
            invoice.inv_sync = True
