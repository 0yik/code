# -*- coding: utf-8 -*- 

from odoo import models, fields, api
from odoo.osv import osv
from odoo.tools.translate import _
from odoo.exceptions import UserError, RedirectWarning, ValidationError

class hr_department(models.Model):

    _inherit = "hr.department"


    @api.multi
    def _get_total_employees(self):
	'''(Method called from a Computed Field 'total_employees').
	   For calculating total number of employees present in the department. '''
	for obj in self:
	    employees = self.env['hr.employee'].search([('department_id','=',obj.id)])
	    count = [1 for emp in employees]
	    obj.total_employees = sum(count) 


    @api.one
    @api.constrains('weightage_line_ids')
    def _check_weightage(self):
        ''' To check the total weightage and raises validation error, if total is not 100.'''
        total = [x.weightage for x in self.weightage_line_ids if x.weightage != 0]
        if (total and sum(total) != 100):
	    raise ValidationError('Total weightage should be equal to 100.')



    weightage_line_ids = fields.One2many('weightage.lines','weightage_line_id',string="Weightages")
    total_employees = fields.Integer(compute = _get_total_employees,string='Total Employees')

    _sql_constraints = [('name_uniq','unique(name)','The department name must be unique.')]


class WeightageLines(models.Model):
    _name = "weightage.lines"
    _description = 'Weightage Lines'

    rating_id = fields.Many2one('rating.config',"Rating")
    weightage = fields.Integer(string="Weightage")
    weightage_line_id = fields.Many2one('hr.department',"weightage_line_id")

    @api.onchange('weightage')
    def onchange_score(self):
        ''' On change func() over the field 'Weightage' to restrict entering the negative values.'''
        if self.weightage < 0:
            self.weightage = 0
            return {'warning':{'title':('Warning!'),'message':('Value cannot be negative.')}}
        return {}
