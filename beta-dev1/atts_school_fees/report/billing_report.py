
# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
import time
from datetime import datetime
from odoo import models, api
from datetime import date


class BillingReport(models.AbstractModel):
    _name = 'report.school_fees.billing_report'


    def get_data(self,ans):
        data_report = []
        register_obj = self.env['student.fees.register']
        from_date = 0
        amt=0
        cur_date1=0
        for data in register_obj.search([],order='date ASC'):
            cur_date = date.today().strftime('%Y-%m-%d')
            cur_date1 = datetime.strptime(cur_date, '%Y-%m-%d').date()
            amt = 0
            for line in self.env['register.student.list'].search([('register_id','=',data.id),('student_id','=',ans.id)]):
                if line.status=='pending' and from_date==0:
                    amt += line.total-line.amount_paid
                    from_date = line.register_id.date
                if line.status=='pending' and from_date<>0:
                    amt += line.total-line.amount_paid
        return amt,from_date,cur_date1
    

    @api.model
    def render_html(self, docids, data=None):
        ans = self.env['student.student'].search([('id', 'in', docids)])
        amt,from_date,cur_date1 = self.get_data(ans)
        docargs = {
            'doc_ids': docids,
            'doc_model': ans,
            'docs': ans,
            'amt': amt,
            'from_date': from_date,
            'to_date': cur_date1,
        }
        render_model = 'school_fees.billing_report'
        return self.env['report'].render(render_model, docargs)