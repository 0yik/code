# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, SUPERUSER_ID
from odoo.tools.translate import _
import base64
import csv
import cStringIO


class POSImport(models.TransientModel):
    _name = 'pos.import'


    file = fields.Binary('File ', required=True)
    date = fields.Date(string="Order Date", required=True)

    @api.multi
    def import_pos_data(self):

        data = base64.b64decode(self.file)
        file_input = cStringIO.StringIO(data)
        file_input.seek(0)
        reader = csv.reader(file_input, delimiter=',',
                            lineterminator='\r\n')
        reader_info = []
        try:
            reader_info.extend(reader)
        except Exception:
            raise exceptions.Warning(_("Not a valid file!"))
        keys = reader_info[0]

        pos_session = self.env['pos.session']
        pos_config = self.env['pos.config']
        acc_journal_obj = self.env['account.journal']
        pos_order_obj = self.env['pos.order']
        product_obj = self.env['product.product']
        account_tax_obj = self.env['account.tax']
        bank_acc_statement_line = self.env['account.bank.statement.line']
        bank_acc_statement = self.env['account.bank.statement']
        ctx = self.env.context
        header = reader_info[0]
        uid = SUPERUSER_ID

        cash_statement_journal_id = None
        mcc_statement_journal_id = None
        bcc_statement_journal_id = None
        bni_statement_journal_id = None
        vc_statement_journal_id = None


        for i in range(1, len(reader_info)):
            try:
                field = map(str, reader_info[i])
            except ValueError:
                raise exceptions.Warning(_("Dont Use Charecter only use numbers"))
            
            # create session 
            pos_config_id = pos_config.search([('name', '=', field[0])])
            if field[0]:
                if not pos_config_id:
                    cash_journal = acc_journal_obj.search([('type', '=', 'cash')])
                    journal_id = acc_journal_obj.search([('type', '=', 'sale'), ('code', '=', 'INV')], limit=1)
                    pos_config_vals = {'name': field[0],
                        'journal_ids': [(6, 0, cash_journal.ids)] , 
                        'journal_id': journal_id.id , 
                    }
                    pos_config_id = pos_config.create(pos_config_vals)

                pos_session_id = pos_session.search([('config_id', '=', pos_config_id.id), ('state', '=', 'opened')])
                if not pos_session_id:
                    vals = {
                        'config_id': pos_config_id.id,
                    }
                    pos_session_id = pos_session.create(vals)
                product_id = product_obj.search([('name', '=', field[1])]) 
                if not product_id:
                    product_id = product_obj.create({'name': field[1],
                            'type': 'consu'})
                # /account_tax_id = None
                account_tax_id = account_tax_obj.search([('name', '=', 'PPN'),('amount_type', '=','percent')])

                if not account_tax_id:
                    account_tax_id = account_tax_obj.create({
                        'name' : 'PPN',
                        'amount_type' : 'percent',
                        'amount': 10,
                        })
                
                statement_data = []
                if field[10] and header[10] == 'Cash':
                    if not cash_statement_journal_id:
                        cash_statement_journal_id = acc_journal_obj.sudo().search([('type', '=','cash'), ('name', '=', 'Cash')], limit=1)
                    if not cash_statement_journal_id:
                        cash_statement_journal_id = acc_journal_obj.sudo().create({
                            'name': 'Cash',
                            'type':'bank',
                            'code': 'cash',
                            'journal_user': True,
                            })
                    statement_id = bank_acc_statement.search([('state', '=', 'open'), ('journal_id', '=', cash_statement_journal_id.id)])
                    pos_name = self.env['ir.sequence'].with_context(ctx).next_by_code('pos.session')
                    name = ''
                    if pos_session_id:
                        name = pos_name + '/' + pos_session_id.name
                    if not statement_id:
                        statement_id = bank_acc_statement.create({'name':name,'journal_id' : cash_statement_journal_id.id})
                    
                    st_values = {
                        'journal_id': cash_statement_journal_id.id,
                        'statement_id': statement_id.id,
                        'name': name,
                        'amount': field[10],
                    }
                    statement_data.append(bank_acc_statement_line.with_context(ctx).sudo(uid).create(st_values).id)
                if field[11] and header[11] == 'Mega CC':
                    if not mcc_statement_journal_id:
                        mcc_statement_journal_id = acc_journal_obj.sudo().search([('code', '=','MCC'), ('name', '=', 'Mega CC')], limit=1)
                    if not mcc_statement_journal_id:
                        mcc_statement_journal_id = acc_journal_obj.sudo().create({
                            'name': 'Mega CC',
                            'type':'bank',
                            'code': 'MCC',
                            'journal_user': True,
                            })
                    statement_id = bank_acc_statement.search([('state', '=', 'open'), ('journal_id', '=', mcc_statement_journal_id.id)])
                    pos_name = self.env['ir.sequence'].with_context(ctx).next_by_code('pos.session')
                    name = ''
                    if pos_session_id:
                        name = pos_name + '/' + pos_session_id.name
                    if not statement_id:
                        statement_id = bank_acc_statement.create({'name':name,'journal_id' : mcc_statement_journal_id.id})
                    st_values = {
                        'journal_id': mcc_statement_journal_id.id,
                        'statement_id': statement_id.id,
                        'name': name,
                        'amount': field[11],
                    }   
                    statement_data.append(bank_acc_statement_line.with_context(ctx).sudo(uid).create(st_values).id)
                if field[12] and header[12] == 'BCA CC':
                    if not bcc_statement_journal_id:
                        bcc_statement_journal_id = acc_journal_obj.sudo().search([('code', '=','BCC'), ('name', '=', 'BCA CC')], limit=1)
                    if not bcc_statement_journal_id:
                        bcc_statement_journal_id = acc_journal_obj.sudo().create({
                            'name': 'BCA CC',
                            'type':'bank',
                            'code': 'BCC',
                            'journal_user': True,
                            })
                    statement_id = bank_acc_statement.search([('state', '=', 'open'), ('journal_id', '=', bcc_statement_journal_id.id)])
                    pos_name = self.env['ir.sequence'].with_context(ctx).next_by_code('pos.session')
                    name = ''
                    if pos_session_id:
                        name = pos_name + '/' + pos_session_id.name
                    if not statement_id:
                        statement_id = bank_acc_statement.create({'name':name, 'journal_id' : bcc_statement_journal_id.id})
                    st_values = {
                        'journal_id': bcc_statement_journal_id.id,
                        'statement_id': statement_id.id,
                        'name': name,
                        'amount': field[12],
                    }
                    statement_data.append(bank_acc_statement_line.with_context(ctx).sudo(uid).create(st_values).id)
                if field[13] and header[13] == 'BNI':
                    if not bni_statement_journal_id:
                        bni_statement_journal_id = acc_journal_obj.sudo().search([('code', '=','BNI'), ('name', '=', 'BNI')], limit=1)
                    if not bni_statement_journal_id:
                        bni_statement_journal_id = acc_journal_obj.sudo().create({
                            'name': 'BNI',
                            'type':'bank',
                            'code': 'BNI',
                            'journal_user': True,
                            })
                    statement_id = bank_acc_statement.search([('state', '=', 'open'), ('journal_id', '=', bni_statement_journal_id.id)])
                    pos_name = self.env['ir.sequence'].with_context(ctx).next_by_code('pos.session')
                    name = ''
                    if pos_session_id:
                        name = pos_name + '/' + pos_session_id.name
                    if not statement_id:
                        statement_id = bank_acc_statement.create({'name':name, 'journal_id' : bni_statement_journal_id.id})
                    st_values = {
                        'journal_id': bni_statement_journal_id.id,
                        'statement_id': statement_id.id,
                        'name': name,
                        'amount': field[13],
                    }
                    statement_data.append(bank_acc_statement_line.with_context(ctx).sudo(uid).create(st_values).id)
                if field[14] and header[14] == 'Voucher':
                    if not vc_statement_journal_id:
                        vc_statement_journal_id = acc_journal_obj.sudo().search([('code', '=','VCH'), ('name', '=', 'Voucher')], limit=1)
                    if not vc_statement_journal_id:
                        vc_statement_journal_id = acc_journal_obj.sudo(uid).create({
                            'name': 'Voucher',
                            'type':'bank',
                            'code': 'VCH',
                            'journal_user': True,
                            })
                        jj = acc_journal_obj.sudo().search([('type', '=','VCH'), ('name', '=', 'Voucher')], limit=1)
                    statement_id = bank_acc_statement.search([('state', '=', 'open'), ('journal_id', '=', vc_statement_journal_id.id)])
                    pos_name = self.env['ir.sequence'].with_context(ctx).next_by_code('pos.session')
                    name = ''
                    if pos_session_id:
                        name = pos_name + '/' + pos_session_id.name
                    if not statement_id:
                        statement_id = bank_acc_statement.create({'name':name, 'journal_id' : vc_statement_journal_id.id})
                    st_values = {
                        'journal_id': vc_statement_journal_id.id,
                        'statement_id': statement_id.id,
                        'name': name,
                        'amount': field[14],
                    }
                    statement_data.append(bank_acc_statement_line.with_context(ctx).sudo(uid).create(st_values).id)
                pos_order_vals = {
                    'session_id' : pos_session_id.id,
                    'date_order': self.date,
                    'statement_ids': [(6, 0, statement_data)],
                    'state': 'paid',
                    'lines': [(0, 0, {
                        'product_id': product_id.id,
                        'qty': field[2],
                        'price_unit': field[3],
                        'discount' :  field[5] and float(field[5])/float(field[4]) * 100 or 0,
                        'tax_ids': account_tax_id and  [(6, 0, account_tax_id.ids)],
                        'tax_ids_after_fiscal_position': account_tax_id and  [(6, 0, account_tax_id.ids)],
                        })],
                }
                pos_order_id = pos_order_obj.create(pos_order_vals)