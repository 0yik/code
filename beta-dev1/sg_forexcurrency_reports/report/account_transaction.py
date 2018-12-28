# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import UserError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF

class ReportAccounTtransaction(models.AbstractModel):

    _name = 'report.sg_forexcurrency_reports.report_accounttransaction'

    @api.model
    def render_html(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        date_from = data['form'].get('date_from') and datetime.strptime(data['form']['date_from'], DF) or False
        data['form']['date_from'] = date_from and date_from.strftime('%d/%m/%Y') or False
        date_to = data['form'].get('date_to', False) and datetime.strptime(data['form']['date_to'], DF) or False
        data['form']['date_to'] = date_to and date_to.strftime('%d/%m/%Y') or False
        invoices = self.env['account.transaction.report']._get_invoices(data['form']['partner_ids'], date_from, date_to, data['form']['invoice_state'],data['form']['result_selection'])
        docargs = {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'type': data['form']['result_selection'],
            'invoices':invoices,
        }
        return self.env['report'].render('sg_forexcurrency_reports.report_accounttransaction', docargs)
