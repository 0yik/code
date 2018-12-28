# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.report import report_sxw
import time

class POFabricReport(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(POFabricReport, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
        })

class po_fabric_report(models.AbstractModel):
    _name = 'report.modifier_teo_purchase_order_report.po_fabric_report'
    _inherit = 'report.abstract_report'
    _template = 'modifier_teo_purchase_order_report.po_fabric_report'
    _wrapped_report_class = POFabricReport

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: