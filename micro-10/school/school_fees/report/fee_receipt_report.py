
# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
import time
from datetime import datetime
from odoo import models, api


class ReportFeeReceipt(models.AbstractModel):
    _name = 'report.school_fees.fee_receipt'


    def get_data(self,isued_by,receipt_id):
        data_receipt = []
        receipt_obj = self.env['student.payslip']
        act_domain = [('id','=', receipt_id[0])]
        receipt_id = receipt_obj.search(act_domain)
        for data in self.env['student.payslip.line'].search([('slip_id','=',receipt_id.id)]):
            data_receipt.append({
                                     'name': data.fee_head_id.name,
                                     'start_date':data.start_date,
                                     'end_date':data.end_date,
                                     'amount':data.amount_paid,
                                     
                               })
        return data_receipt
    def get_issued(self,isued_by,receipt_id):
        return isued_by[1]
    

    @api.model
    def render_html(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        isued_by = data['form'].get('isued_by')
        receipt_id = data['form'].get('receipt_id')
        res_data = self.get_data(isued_by,receipt_id)
        res_data_issue = self.get_issued(isued_by,receipt_id)
        docargs = {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'data_receipt': res_data,
            'data_issued':res_data_issue,
            }
        render_model = 'school_fees.fee_receipt'
        return self.env['report'].render(render_model, docargs)