#-*- coding:utf-8 -*-

# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from odoo import api, fields, models
from odoo import exceptions, _


class LcReport(models.AbstractModel):
    _name = 'report.printout_work_order.report_wo' #report.modulename.your_modelname of report


    @api.multi
    def render_html(self, docids, data=None):
        comp_sales = self.env["res.company"].search([])
        
#         pid =comp_sales.partner_id
        data = self.env["mrp.workorder"].search([("id","=",docids)])
        hours, rest = divmod(data.duration * 60, 3600)  # obtain the hours and the rest
        minutes,seconds  = divmod(rest, 60)  # 
        duration = "{:02.0f}:{:02.0f}:{:02.0f}".format(hours, minutes, seconds)
        
        hours, rest1 = divmod(data.duration_expected * 60, 3600)  # obtain the hours and the rest
        seconds, minutes = divmod(rest1, 60)  # 
        duration_expected = "{:02.0f}:{:02.0f}:{:02.0f}".format(hours, minutes, seconds)
        
        
                
        docargs = {
            'docs':data,
            'duration':duration,
            'comp':comp_sales,
        }

        return self.env['report'].render('printout_work_order.report_wo',docargs)
        

     
     
     
