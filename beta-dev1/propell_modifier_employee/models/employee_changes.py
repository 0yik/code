# -*- coding: utf-8 -*-

from odoo import models, fields, api



class propell_modifier_employee(models.Model):
  
    _inherit = "hr.employee"
    identification_id = fields.Char(string='Identification No', groups='hr.group_hr_user', required=True)
    date_of_issue=fields.Date(string='Date of Issue')
    
    @api.multi
    def _get_country_default(self):
	    country_id = self.env['res.country'].search([('code','=','SG')]).id
	    return country_id

    emp_country_id = fields.Many2one('res.country', string="Country", default=_get_country_default)
    @api.multi
    def _get_state_default(self):
	    state_id = self.env['res.country.state'].search([('name','=','Singapore'),('code','=','SG')]).id
	    return state_id

        
    emp_state_id = fields.Many2one('res.country.state', 'State',default=_get_state_default)
    country=fields.Many2one('res.country', string="Home Country")
    state=fields.Many2one('res.country.state', 'State')
    home_address=fields.Many2one('res.partner', string='Home Address')
    city=fields.Many2one('employee.city', string='City')
    

   