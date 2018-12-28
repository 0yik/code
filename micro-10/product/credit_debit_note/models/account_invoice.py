# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from dateutil.relativedelta import relativedelta
import datetime
import logging
from datetime import date
import time

from odoo import models, fields, api
from odoo.exceptions import except_orm
from odoo import tools
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    debit_note = fields.Boolean('Debit Note')
    ref_no = fields.Many2one('account.invoice','Invoice No')
    invoice_date = fields.Date('Invoice Date')
    reference_text = fields.Char('Ref No')
    reason = fields.Char('Reason')
    credit_note = fields.Boolean('Credit Note')

    @api.multi
    def onchange_invocie_ref(self, reference):
        invoice = None
        if reference:
            invoice = self.env['account.invoice'].browse(reference)
            return {'value': {
                'invoice_date': invoice and invoice.date_invoice or False,
            }}
        return {}

    @api.multi
    def action_move_create(self):
        values = super(AccountInvoice, self).action_move_create()
        for inv in self:
            if inv.debit_note:
                number = self.env['ir.sequence'].next_by_code('invocie.debit.note')
                inv.move_name = number
            if inv.type=='out_refund':
                number = self.env['ir.sequence'].next_by_code('invocie.credit.note')
                inv.move_name = number
            if inv.type=='in_refund':
                number = self.env['ir.sequence'].next_by_code('bill.debit.note')
                inv.move_name = number
            if inv.type=='in_invoice' and inv.credit_note:
                number = self.env['ir.sequence'].next_by_code('bill.credit.note')
                inv.move_name = number
        return values

class AccountMove(models.Model):
    _inherit = "account.move"

    @api.multi
    def post(self):
        values = super(AccountMove, self).post()
        new_name = False
        invoice = self._context.get('invoice', False)
        for move in self:
            if move.name == '/':
                new_name = False
            if invoice and invoice.debit_note and invoice.move_name != '/':
                new_name = self.env['ir.sequence'].next_by_code('invocie.debit.note')
            if invoice and invoice.type=='out_refund' and invoice.move_name != '/':
                new_name = self.env['ir.sequence'].next_by_code('invocie.credit.note')
            if invoice and invoice.type=='in_refund' and invoice.move_name != '/':
                new_name = self.env['ir.sequence'].next_by_code('bill.debit.note')
            if invoice and invoice.type=='in_invoice' and invoice.credit_note and invoice.move_name != '/':
                new_name = self.env['ir.sequence'].next_by_code('bill.credit.note')
            if new_name:
                move.name = new_name
        return values
