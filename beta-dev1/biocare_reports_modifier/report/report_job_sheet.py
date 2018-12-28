# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _
from odoo.report import report_sxw
from datetime import date
import time
from itertools import groupby


class report_job_sheet_biocare(models.AbstractModel):
    _name = 'report.biocare_reports_modifier.report_job_sheet'


    @api.model
    def render_html(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        domain = [('actual_start', '>=', data['form']['date_start'] + ' 00:00:01'),
                  ('actual_end', '<=', data['form']['date_end']+ ' 23:59:59'),
                  ('is_booking', '=', True),
                  ('state', 'in', ['done']),
                  '|', ('team.team_leader', '=', data['form']['employee_id'][0]),
                  ('team_employees.employee_id', '=', data['form']['employee_id'][0])]
        obj_wos = self.env['stock.picking'].search(domain)
        if not obj_wos:
            raise exceptions.UserError(_("No Data found!!!"))
        partner_ids = [wo.partner_id.id for wo in obj_wos]
        partners = [wo.partner_id for wo in obj_wos]

        docargs = {
            'doc_ids': [1],
            'doc_model': self.env['stock.picking'],
            'data': data,
            'docs': obj_wos[0],
            'time': time,
            'work_orders':obj_wos,
            'vehicle': obj_wos[0].team.vehicle_new_id and obj_wos[0].team.vehicle_new_id.name or '',
            #'lines': self._lines,
            #'sum_partner': self._sum_partner,
        }
        return self.env['report'].render('biocare_reports_modifier.report_job_sheet', docargs)

    def _print_report(self, data):
        data['form'].update(self.read(['employee_id', 'date_start', 'date_end'])[0])
        return self.env['report'].get_action(self, 'biocare_reports_modifier.report_job_sheet', data=data)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
