# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from dateutil import relativedelta

from odoo import api, fields, models


class OutstandingReport(models.Model):
    _name = 'outstanding.report'
     
    student_id = fields.Integer('Student Id')
    student_name = fields.Char('Student Name')
    class_no = fields.Char('Class No')
    one_mth = fields.Float('One mth')
    two_mth = fields.Float('Two mth')
    three_mth = fields.Float('Three mth')
    four_mth = fields.Float('Four mth')
    five_mth = fields.Float('Five mth')
    six_mth = fields.Float('Six mth')
    six_grt = fields.Float('Six grt')
    total = fields.Float('Total')


class OutstandingReportWizard(models.TransientModel):
    _name = 'outstanding.report.wizard'
    _description = 'Outstanding Fee Report Wizard'

    
    @api.multi
    def print_report(self):
        datas = {
             'ids': self.ids,
             'model': 'outstanding.report',
             'form': self.read([])[0]
        }
        return self.env['report'].get_action([], 'school_fees.outstanding_fee_report', data=datas)