# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.report import report_sxw
import time

class SaleOrderLaboReport(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(SaleOrderLaboReport, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
        })

class sale_report_labo(models.AbstractModel):
    _name = 'report.laborindo_report_sales_order.sale_report_labo'
    _inherit = 'report.abstract_report'
    _template = 'laborindo_report_sales_order.sale_report_labo'
    _wrapped_report_class = SaleOrderLaboReport

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: