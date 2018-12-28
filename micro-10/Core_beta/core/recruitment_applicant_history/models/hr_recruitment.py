from datetime import datetime

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.exceptions import UserError

class Applicant(models.Model):
    _inherit = "hr.applicant"

    @api.multi
    def action_get_past_applicant(self):
        action = self.env.ref('hr_recruitment.action_hr_job_applications')
        result = action.read()[0]
        result.pop('id', None)
        result['context'] = {}
        application_ids = self.search([('identification_no','=',self.identification_no), ('id','!=', self.id)])
        result['domain'] = "[('id','in',[" + ','.join(map(str, application_ids.ids)) + "])]"
        return result
