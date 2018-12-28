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

import time
from odoo import fields, models, api


class account_analytic_journal_report(models.TransientModel):
    _name = 'account.analytic.journal.report'
    _description = 'Account Analytic Journal'

    date1 = fields.Date('Start of period', required=True)
    date2 = fields.Date('End of period', required=True)
    analytic_account_journal_id = fields.Many2many('account.analytic.journal', 'account_analytic_journal_name',
                                                   'journal_line_id', 'journal_print_id', 'Analytic Journals',
                                                   required=True)

    _defaults = {
        'date1': lambda *a: time.strftime('%Y-01-01'),
        'date2': lambda *a: time.strftime('%Y-%m-%d')
    }

    def check_report(self, context=None):
        if context is None:
            context = {}
        data = self.read()[0]
        ids_list = []
        if context.get('active_id',False):
            ids_list.append(context.get('active_id',False))
        else:
            record = self
            for analytic_record in record.analytic_account_journal_id:
                ids_list.append(analytic_record.id)
        datas = {
            'ids': ids_list,
            'model': 'account.analytic.journal',
            'form': data
        }
        context2 = context.copy()
        context2['active_model'] = 'account.analytic.journal'
        context2['active_ids'] = ids_list
        return self.env['report'].get_action([], 'report_analyticjournal', data=datas)

    @api.model
    def default_get(self):
        context = {}
        res = super(account_analytic_journal_report, self).default_get()
        if not context.has_key('active_ids'):
            journal_ids = self.env['account.analytic.journal'].search([])
        else:
            journal_ids = context.get('active_ids')
        if 'analytic_account_journal_id' in fields:
            res.update({'analytic_account_journal_id': journal_ids})
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
