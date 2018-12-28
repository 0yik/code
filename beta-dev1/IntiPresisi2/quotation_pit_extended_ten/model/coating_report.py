# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-Today  (<http://www..in>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from datetime import date
from datetime import datetime
from odoo.osv import osv
from odoo.report import report_sxw
import calendar
from odoo import api, fields, models, SUPERUSER_ID, _

class coating_part_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        super(coating_part_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            # 'get_order_line':self.get_order_line,
            })


class coating_view_report_template_id(osv.AbstractModel):
    _name = 'report.quotation_pit_extended_ten.coating_report_template'
    _inherit = 'report.abstract_report'
    _template = 'quotation_pit_extended_ten.coating_report_template'
    _wrapped_report_class = coating_part_report

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: