# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, SUPERUSER_ID
from odoo.tools.translate import _
import base64
import csv
import cStringIO
from odoo.tools import float_is_zero
from datetime import datetime

class POSImport(models.TransientModel):
    _inherit = 'pos.import'
    
    branch_id = fields.Many2one('res.branch', 'Branch')

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
        Move = self.env['stock.move']
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
                        name = pos_name + '/' + pos_session_id[0].name
                    if not statement_id:
                        statement_id = bank_acc_statement.create({'name':name,'journal_id' : cash_statement_journal_id.id})
                    
                    st_values = {
                        'journal_id': cash_statement_journal_id.id,
                        'statement_id': statement_id[0].id,
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
                        name = pos_name + '/' + pos_session_id[0].name
                    if not statement_id:
                        statement_id = bank_acc_statement.create({'name':name,'journal_id' : mcc_statement_journal_id.id})
                    st_values = {
                        'journal_id': mcc_statement_journal_id.id,
                        'statement_id': statement_id[0].id,
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
                        name = pos_name + '/' + pos_session_id[0].name
                    if not statement_id:
                        statement_id = bank_acc_statement.create({'name':name, 'journal_id' : bcc_statement_journal_id.id})
                    st_values = {
                        'journal_id': bcc_statement_journal_id.id,
                        'statement_id': statement_id[0].id,
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
                        name = pos_name + '/' + pos_session_id[0].name
                    if not statement_id:
                        statement_id = bank_acc_statement.create({'name':name, 'journal_id' : bni_statement_journal_id.id})
                    st_values = {
                        'journal_id': bni_statement_journal_id.id,
                        'statement_id': statement_id[0].id,
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
                        name = pos_name + '/' + pos_session_id[0].name
                    if not statement_id:
                        statement_id = bank_acc_statement.create({'name':name, 'journal_id' : vc_statement_journal_id.id})
                    st_values = {
                        'journal_id': vc_statement_journal_id.id,
                        'statement_id': statement_id[0].id,
                        'name': name,
                        'amount': field[14],
                    }
                    statement_data.append(bank_acc_statement_line.with_context(ctx).sudo(uid).create(st_values).id)
                pos_order_vals = {
                    'session_id' : pos_session_id[0].id,
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
                pos_session_id.action_pos_session_closing_control()
                self.reduce_bom_stock(pos_order_id, pos_config_id)
                if pos_order_id.partner_id:
                    destination_id = pos_order_id.partner_id.property_stock_customer.id
                else:
                    customerloc, supplierloc = self.env['stock.warehouse']._get_partner_locations()
                    destination_id = customerloc.id
                moves = Move
                for line in  pos_order_id.lines.filtered(lambda l: l.product_id.type in ['product', 'consu'] and not float_is_zero(l.qty, precision_digits=l.product_id.uom_id.rounding)):
                    bom = self.env['mrp.bom'].search([('product_id','=',line.product_id.id)])
                    if not bom or bom.included_bom:
                        moves |= Move.create({
                            'name': line.name,
                            'product_uom': line.product_id.uom_id.id,
#                             'picking_id': order_picking.id if line.qty >= 0 else return_picking.id,
#                             'picking_type_id': picking_type.id if line.qty >= 0 else return_pick_type.id,
                            'product_id': line.product_id.id,
                            'product_uom_qty': abs(line.qty),
                            'state': 'draft',
                            'location_id': pos_order_id.location_id.id,
                            'location_dest_id': destination_id if line.qty >= 0 else return_pick_type != picking_type and return_pick_type.default_location_dest_id.id or location_id,
                        })
                        if moves:
                            tracked_moves = moves.filtered(lambda move: move.product_id.tracking != 'none')
                            untracked_moves = moves - tracked_moves
                            tracked_moves.action_confirm()
                            untracked_moves.action_assign()
                            moves.filtered(lambda m: m.state in ['confirmed', 'waiting']).force_assign()
                            moves.filtered(lambda m: m.product_id.tracking == 'none').action_done()

    def _generate_finished_moves(self):
        move = self.env['stock.move'].create({
            'name': 'bom_move',
            'date': self.date_planned_start,
            'date_expected': self.date_planned_start,
            'product_id': self.product_id.id,
            'product_uom': self.product_uom_id.id,
            'product_uom_qty': self.product_qty,
            'location_id': self.product_id.property_stock_production.id,
            'location_dest_id': self.location_dest_id.id,
            'move_dest_id': self.procurement_ids and self.procurement_ids[0].move_dest_id.id or False,
            'procurement_id': self.procurement_ids and self.procurement_ids[0].id or False,
            'company_id': self.company_id.id,
            'production_id': self.id,
            'origin': self.name,
            'group_id': self.procurement_group_id.id,
            'propagate': self.propagate,
        })
        move.action_confirm()
        return move

    @api.multi
    def reduce_bom_stock(self, pos_order_id, pos_config_id):
        def check_bom(bom, qty):
            bom_obj = self.env['mrp.bom']
            for line in bom.bom_line_ids:
                inner_bom = bom_obj.search([('product_id', '=', line.product_id.id)])
                if not inner_bom:
                    amount = line.product_uom_id._compute_quantity(float(float(line.product_qty) * float(qty)), line.product_id.uom_id, round=True, rounding_method='UP')
                    move = self.env['stock.move'].create({
                        'name': pos_order_id.name,
                        'date': datetime.now(),
                        'date_expected': datetime.now(),
                        'product_id': line.product_id.id,
                        'product_uom': line.product_id.uom_id.id,
                        'product_uom_qty': float(amount),
                        'location_id': pos_config_id.stock_location_id.id,
                        'location_dest_id': self.env.ref('stock.stock_location_customers').id,
                        'company_id': pos_config_id.company_id.id,
                        'origin': pos_order_id.name,
                    })
                    move.action_confirm()
                    move.action_done()
                else:
                    qty = line.product_uom_id._compute_quantity(float(float(line.product_qty) * float(qty)), line.product_id.uom_id, round=True, rounding_method='UP')
                    check_bom(inner_bom, qty)
            return
        for pos_line in pos_order_id.lines:
            qty = pos_line.qty
            bom = self.env['mrp.bom'].search([('product_id','=',pos_line.product_id.id)])
            check_bom(bom, qty)
        return True
