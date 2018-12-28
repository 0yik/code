# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _
from odoo.report import report_sxw
from datetime import date
import time


class report_workorder_biocare(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(report_workorder_biocare, self).__init__(
            cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'date': date,
        })


class report_workorder(models.AbstractModel):
    _name = 'report.biocare_reports_modifier.report_workorder'
    _inherit = 'report.abstract_report'
    _template = 'biocare_reports_modifier.report_workorder'
    _wrapped_report_class = report_workorder_biocare



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
