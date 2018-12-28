# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _
from odoo.report import report_sxw
from datetime import date
import time
from itertools import groupby
from dateutil.relativedelta import relativedelta


class report_contract_wizard(models.AbstractModel):
    _name = 'report.biocare_reports_modifier.report_contract_wizard'

    @api.model
    def render_html(self, docids, data=None):
        data['context'].update({'active_ids': data['ids']})
        if not docids:
            docids = data['ids']

        model = self.env.context.get('active_model')
        docs = self.env[model].browse(data['ids'])
        ctx = self.env.context.copy()
        ctx.update({'active_ids': data['ids']})

        if not data.get('form'):
            raise exceptions.UserError(_("Form content is missing, this report cannot be printed."))
        obj_analytic = self.env['account.analytic.account'].browse(data['ids'])

        docargs = {
            'doc_ids': docids,
            'doc_model': self.env['account.analytic.account'],
            'data': data,
            'docs': self.env['account.analytic.account'].browse(data['ids']),
            'time': time,
            'doc_model': model,
        }

        return self.env['report'].render('biocare_reports_modifier.report_contract_wizard', docargs)

    def _print_report(self, data):
        data['form'].update(self.read(['start_date', 'end_date'])[0])
        return self.env['report'].get_action(self, 'biocare_reports_modifier.report_contract_wizard', data=data)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
