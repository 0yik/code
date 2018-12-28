# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import UserError
from datetime import datetime
from odoo.tools import float_is_zero
from dateutil.relativedelta import relativedelta
import time
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF

class ReportAccounTtransaction(models.AbstractModel):

    _name = 'report.sg_ageingreport_forex.report_agedforeigncurrency'

    
    @api.model
    def render_html(self, docids, data=None):

        if not data.get('form') or not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        date_from = data['form'].get('date_from') and datetime.strptime(data['form']['date_from'], DF) or False
        
        date_to = data['form'].get('date_to', False) and datetime.strptime(data['form']['date_to'], DF) or False
        

        if data['form']['result_selection'] == 'customer':
            account_type = ['receivable']
        elif data['form']['result_selection'] == 'supplier':
            account_type = ['payable']
        else:
            account_type = ['payable', 'receivable']

        target_move = data['form'].get('target_move', 'all')
        partner_ids = data['form']['partner_ids']
        if not partner_ids:
            dom = []
            if data['form']['result_selection'] == 'customer':
                dom.append(('customer', '=', True))
            if data['form']['result_selection'] == 'supplier':
                dom.append(('supplier', '=', True))

            partner_ids = self.env['res.partner'].search(dom).ids
        invoices, periods = self.env['account.aged.forex.report']._get_invoices(partner_ids, date_from, date_to,data['form']['result_selection'], data['form']['period_length'], target_move, account_type)
        date_from_move = data['form'].get('date_from', time.strftime('%Y-%m-%d'))
        docargs = {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'type': data['form']['result_selection'],
            'invoices':invoices,
            'periods': periods,
        }
        return self.env['report'].render('sg_ageingreport_forex.report_agedforeigncurrency', docargs)
