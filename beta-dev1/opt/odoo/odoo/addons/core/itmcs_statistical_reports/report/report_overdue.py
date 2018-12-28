import time
from odoo import api, models


# overdue reports for customer
class ReportOverdueReport(models.AbstractModel):
    _name = 'report.itmcs_statistical_reports.report_overduereport'

    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        overdue_obj = self.env['overdue.report']
        partner_obj = self.env['res.partner']
        user = self.env["res.users"].browse(self._uid)
        docs = []
        for partner in self.env.context.get('overdues'):
            docs.append(
                (partner_obj.browse(partner[0]).name, overdue_obj.browse(partner[1])))
        color = {'company_header_bgcolor1' : user.company_id.company_header_bgcolor1,
        'company_header_fontcolor1' : user.company_id.company_header_fontcolor1,
        'report_header_bgcolor1' : user.company_id.report_header_bgcolor1,
        'report_header_fontcolor1' : user.company_id.report_header_fontcolor1,
        'title_bgcolor1' : user.company_id.title_bgcolor1,
        'title_fontcolor1' : user.company_id.title_fontcolor1,
        'subtitle_bgcolor1' : user.company_id.subtitle_bgcolor1,
        'subtitle_fontcolor1' : user.company_id.subtitle_fontcolor1,
        'text_bgcolor1' : user.company_id.text_bgcolor1,
        'text_fontcolor1' : user.company_id.text_fontcolor1,
            
            }
        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'time': time,
            'data': data,
            'doc' :user,
            'color' : color,
        }
        return self.env['report'].render('itmcs_statistical_reports.report_overduereport', values=docargs)
