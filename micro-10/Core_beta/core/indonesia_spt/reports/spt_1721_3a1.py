from odoo import models,fields,api,_

class indonesia_spt_3a1_report(models.AbstractModel):
    _name = 'report.indonesia_spt.report_1721_3a1'

    @api.model
    def render_html(self, docids, data=None):
        docargs = {
            # 'docs': self.env['hr.employee'].sudo().search([('id', 'in', data['emp_ids'])]),
            'docs': self.env['hr.employee'].sudo().search([],limit=1),
            # 'doc_ids': data.get('ids', data.get('active_ids')),
            # 'doc_model': 'wizard.1721.1.report',
            'data': dict(
                data,
            ),
        }
        return self.env['report'].render('indonesia_spt.report_1721_3a1', docargs)

