# -*- coding: utf-8 -*-
from odoo import models, api

class AccountReportContextCommon(models.TransientModel):
    _inherit = 'account.report.context.common'

    @api.multi
    def get_html_and_data(self, given_context=None):
        result = super(AccountReportContextCommon, self).get_html_and_data(given_context)
        analytic_level_ids = self.env['account.analytic.level'].sudo().search([])
        data_list = []
        for record in analytic_level_ids:
            data_list.append((record.id, record.name))
        result['report_context']['analytic_levels'] = data_list
        try:
            result['report_context']['selected_analytic_level_id'] = self.analytic_level_id.id
        except:
            pass
        return result

AccountReportContextCommon()