# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from dateutil import relativedelta

from odoo import api, fields, models


class ClassSummaryWizard(models.TransientModel):
    _name = 'class.summary.wizard'
    _description = 'Class Summary Wizard'

    
    @api.multi
    def print_report(self):
        datas = {
             'ids': self.ids,
             'model': 'class.class',
             'form': self.read()[0]
        }
        return self.env['report'].get_action([], 'atts_class.report_class_summary', data=datas)