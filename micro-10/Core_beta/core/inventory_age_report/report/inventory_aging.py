# -*- coding: utf-8 -*-
##############################################################################
#
#    DevIntelle Solution(Odoo Expert)
#    Copyright (C) 2015 Devintelle Soluation (<http://devintelle.com/>)
#
##############################################################################

from odoo.report import report_sxw
from odoo import models


class stock_ageing_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(stock_ageing_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_lines': self.get_lines,
        })
        self.context = context

    def get_lines(self, form):
        result = []
        for o in self.objects:
            result += o.get_lines(form)
        return result

class report_stockageing(models.AbstractModel):
    _name     = 'report.inventory_age_report.report_stockageing'
    _inherit  = 'report.abstract_report'
    _template = 'inventory_age_report.report_stockageing'
    _wrapped_report_class = stock_ageing_report

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
