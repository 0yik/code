# -*- coding: utf-8 -*-


from openerp import api, exceptions, fields, models, _
from dateutil import relativedelta
from datetime import datetime


class contract_report_custom(models.TransientModel):
    _name = 'contract.report.custom'
    _description = 'Contract Report export'

    start_date = fields.Date(
        string='Start Date', help='Start Date.')
    end_date = fields.Date(
        string='End Date', help='End Date.')

    def _build_contexts(self, data):
        result = {}
        result['start_date'] = data['form']['start_date'] or False
        result['end_date'] = data['form']['end_date'] or False
        result['from_wizard'] = True
        return result

    @api.constrains('start_date', 'end_date')
    def _check_end_date(self):
        for self_obj in self:
            date1 = fields.Date.from_string(self_obj.start_date)
            date2 = fields.Date.from_string(self_obj.end_date)
            diff = date2 - date1
            if self_obj.start_date > self_obj.end_date:
                raise exceptions.ValidationError(
                    _("End Date can not be less than Start Date."))
            if diff.days  > 365:
                raise exceptions.ValidationError(
                    _("Please select date only for 12 months duration."))

    def _print_report(self, data):
        data['form'].update(self.read(['start_date', 'end_date'])[0])
        return self.env['report'].get_action(self, 'biocare_reports_modifier.report_contract_wizard', data=data)

    @api.multi
    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model')
        data['form'] = self.read(['start_date', 'end_date'])[0]
        data['active_ids'] = self.env.context.get('active_ids', [])
        data['form']['id'] =  [data['ids'][0]]
        used_context = self._build_contexts(data)
        return self.env['report'].get_action(self, 'biocare_reports_modifier.report_contract_wizard', data=data)


contract_report_custom()
