# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.report import report_sxw
import time

class SOLineReport(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(SOLineReport, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
        })

class so_line_report(models.AbstractModel):
    _name = 'report.modifier_teo_sale_order.so_line_report'
    _inherit = 'report.abstract_report'
    _template = 'modifier_teo_sale_order.so_line_report'
    _wrapped_report_class = SOLineReport

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: