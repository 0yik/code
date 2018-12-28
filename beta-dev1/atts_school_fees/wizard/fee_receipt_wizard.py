# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from dateutil import relativedelta

from odoo import api, fields, models


class FeeReceiptWizard(models.TransientModel):
    _name = 'fee.receipt.wizard'
    _description = 'Fee Receipt Wizard'

    isued_by = fields.Many2one('hr.employee','Issued By')
    receipt_id = fields.Many2one('student.payslip','Receipt Id')
    
    @api.model
    def default_get(self,fields):
        context = self._context or {}
        ret = super(FeeReceiptWizard,self).default_get(fields)
        receipt_id = context.get('active_id',False)
        if receipt_id:
            ret['receipt_id'] = receipt_id
        return ret
    
    @api.multi
    def print_report(self):
        datas = {
             'ids': self.ids,
             'model': 'student.payslip',
             'form': self.read([])[0]
        }
        return self.env['report'].get_action([], 'atts.school_fees.fee_receipt', data=datas)