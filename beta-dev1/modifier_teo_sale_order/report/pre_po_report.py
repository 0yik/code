# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.report import report_sxw
import time

class PrePOReport(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(PrePOReport, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
        })

class pre_po_report(models.AbstractModel):
    _name = 'report.modifier_teo_sale_order.pre_po_report'
    _inherit = 'report.abstract_report'
    _template = 'modifier_teo_sale_order.pre_po_report'
    _wrapped_report_class = PrePOReport

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: