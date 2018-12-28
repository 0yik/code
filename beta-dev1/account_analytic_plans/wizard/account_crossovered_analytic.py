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

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class account_crossovered_analytic(models.TransientModel):
    _name = "account.crossovered.analytic"
    _description = "Print Crossovered Analytic"

    date1 = fields.Date('Start Date', required=True, default=lambda *a: time.strftime('%Y-01-01'))
    date2 = fields.Date('End Date', required=True, default=lambda *a: time.strftime('%Y-%m-%d'))
    journal_ids = fields.Many2many('account.journal', string='Analytic Journal')
    ref = fields.Many2one('account.analytic.account', 'Analytic Account Reference', required=True)
    empty_line = fields.Boolean('Dont show empty lines')

#     _defaults = {
#          'date1': lambda *a: time.strftime('%Y-01-01'),
#          'date2': lambda *a: time.strftime('%Y-%m-%d'),
#     }

    @api.multi
    def print_report(self):
        self.env.cr.execute('SELECT account_id FROM account_analytic_line')
        res = self.env.cr.fetchall()
        acc_ids = [x[0] for x in res]

        [data] = self.read()
        data['ref'] = data['ref']

        obj_acc = self.env['account.analytic.account'].browse(data['ref'])
        name = obj_acc.name

        account_ids = self.env['account.analytic.account'].search([('parent_id', 'child_of', [data['ref']])])

        flag = True
        for acc in account_ids:
            if acc in acc_ids:
                flag = False
                break
        if flag:
            raise UserError(_('User Error!'),_('There are no analytic lines related to account %s.' % name))

        datas = {
             'ids': [],
             'model': 'account.analytic.account',
             'form': data
        }
        return self.env['report'].get_action(account_ids, 'account_analytic_plans.report_crossoveredanalyticplans', data=datas)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
