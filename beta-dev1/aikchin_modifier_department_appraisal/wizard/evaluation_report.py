
# -*- coding: utf-8 -*-
from odoo import fields,models,api

class EvaluationReport(models.Model):
    _inherit="evaluation.report"
    _rec_name = "emp_name"

    @api.multi
    def eval_report(self):
        res = super(EvaluationReport, self).eval_report()
        if self.report_type == 'dep_based':
            res['context'] = {'group_by_department': True}
        return res