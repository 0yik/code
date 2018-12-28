from datetime import datetime, timedelta

from odoo import api, fields, models, tools, _

class HrJobPosition(models.Model):

    _inherit = "hr.job"

    parent_id = fields.Many2one('hr.job', string="Parent Job Title")

    @api.multi
    def _compute_application_count(self):
        for job in self:
            read_group_result = self.env['hr.applicant'].read_group([('job_id', '=', job.id)], ['job_id'], ['job_id'])
            result = dict((data['job_id'][0], data['job_id_count']) for data in read_group_result)
            job.application_count = result.get(job.id, 0)