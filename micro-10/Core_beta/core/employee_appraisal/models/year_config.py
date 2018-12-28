# -*- coding: utf-8 -*-
from odoo import fields,models,api
from datetime import datetime
from odoo.osv import osv
from odoo.tools.translate import _
from odoo.exceptions import UserError, RedirectWarning, ValidationError
import re

class YearConfig(models.Model):
    _name="year.config"
    _rec_name="year"

    year = fields.Char(string="Year",size=4)
    quarter_line = fields.One2many('quarter.line', 'quarter_id', string="quarter", readonly=True)


    _sql_constraints = [('name_uniq','unique(year)',"The 'Year' should be unique")]
    
    
    @api.multi
    @api.onchange('year')
    def on_change_year(self):
        ''' On change func() on the field Year. Method performs
	    1) Auto populates the Quarters on the basis of Year.
	    2) Validates the entered value for the Year field according to the conditions.
	'''
        if not self.year:
            self.quarter_line = []
            return
        if (self.year and re.search(r'[^0-9]', self.year)):
	    self.year = False
	    return {'warning':{'title':'Warning!','message':"Year must be integer"}}
        elif (self.year and int(self.year) <1900):
	    self.year = False
	    return {'warning':{'title':'Warning!','message':"Year should be greater than or equal to 1900"}}

        quarter_lines = self.env['quarter.line'].search([('quarter_startdate', '>=', self.year+'-01-01'), ('quarter_enddate', '<=', self.year+'-12-31')])
        if not quarter_lines.ids:
            self.quarter_line = [(5,)]
            self.quarter_line = [      
                              (0, 0, {'name': 'Q1', 'quarter_startdate': datetime.strptime(self.year+'-01-01',"%Y-%m-%d"), 'quarter_enddate': datetime.strptime(self.year+'-03-31',"%Y-%m-%d")}),
                              (0, 0, {'name': 'Q2', 'quarter_startdate': datetime.strptime(self.year+'-04-01',"%Y-%m-%d"), 'quarter_enddate': datetime.strptime(self.year+'-06-30',"%Y-%m-%d")}),
                              (0, 0, {'name': 'Q3', 'quarter_startdate': datetime.strptime(self.year+'-07-01',"%Y-%m-%d"), 'quarter_enddate': datetime.strptime(self.year+'-09-30',"%Y-%m-%d")}),
                              (0, 0, {'name': 'Q4', 'quarter_startdate': datetime.strptime(self.year+'-10-01',"%Y-%m-%d"), 'quarter_enddate': datetime.strptime(self.year+'-12-31',"%Y-%m-%d")})
                            ]
                
        else:
            self.quarter_line = [(6,0, quarter_lines.ids)]
            

class Quarterline(models.Model):
    _name = "quarter.line"
    _description = "Quarter Information"
    
    quarter_id = fields.Many2one('year.config', string='Quarter ID', required=True, ondelete='cascade')
    name = fields.Char(string='Quarter', required=True, readonly=True)
    quarter_startdate = fields.Date(string='Start Date', required=True, readonly=True)
    quarter_enddate = fields.Date(string='End Date', required=True, readonly=True)
    
