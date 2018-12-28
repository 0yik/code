# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _
from itertools import groupby


class ExportBODone(models.TransientModel):
    _name = 'export.bo.done'
    _description = 'Export BO Done'

    date_start = fields.Date(
        string='Start Date',
        help='Select start date for done booking orders.')
    date_end = fields.Date(
        string='End Date',
        help='Select end date for done booking orders.')
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Worker', help='Select employee.')

    def _build_contexts(self, data):
        result = {}
        result['employee_id'] = 'employee_id' in data['form'] and data['form']['employee_id'] or False
        result['date_start'] = data['form']['date_start'] or False
        result['date_end'] = data['form']['date_end'] or False
        return result

    def _print_report(self, data):
        data['form'].update(self.read(['employee_id', 'date_start', 'date_end'])[0])
        return self.env['report'].get_action(self, 'biocare_reports_modifier.report_job_sheet', data=data)

    @api.constrains('date_start', 'date_end')
    def _check_end_date(self):
        for self_obj in self:
            if self_obj.date_start > self_obj.date_end:
                raise exceptions.ValidationError(_("End Date can not be less than Start Date."))

    @api.multi
    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_start', 'date_end', 'employee_id'])[0]
        used_context = self._build_contexts(data)
        return self.env['report'].get_action(self, 'biocare_reports_modifier.report_job_sheet', data=data)


ExportBODone()
