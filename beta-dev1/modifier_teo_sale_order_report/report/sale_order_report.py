# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.report import report_sxw
import time

class SaleOrderReport(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(SaleOrderReport, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
        })

class sale_order_report(models.AbstractModel):
    _name = 'report.modifier_teo_sale_order_report.sale_order_report'
    _inherit = 'report.abstract_report'
    _template = 'modifier_teo_sale_order_report.sale_order_report'
    _wrapped_report_class = SaleOrderReport

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: