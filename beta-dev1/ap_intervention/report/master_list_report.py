# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.report import report_sxw
import time

class MasterListReport(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(MasterListReport, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
        })

class master_list_report(models.AbstractModel):
    _name = 'report.ap_intervention.master_list_report'
    _inherit = 'report.abstract_report'
    _template = 'ap_intervention.master_list_report'
    _wrapped_report_class = MasterListReport

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: