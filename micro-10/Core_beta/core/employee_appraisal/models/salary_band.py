# -*- coding: utf-8 -*- 
from odoo import fields,models,api
from odoo.osv import osv
from odoo.tools.translate import _
from odoo.exceptions import UserError, RedirectWarning, ValidationError



class SalaryBand(models.Model):
    _name="salary.band"


    @api.one
    @api.constrains('salaryrange_ids')
    def _check_validations(self):
	''' Method will validates the Salary ranges between From and To.'''
        to_list=[0]
        for x in self.salaryrange_ids:
            if x.max_increment == 0:
                raise ValidationError('Max Increment(%) cannot be zero.')
            if x.from_val < x.to_val and x.from_val == 0 and to_list[-1] == 0:
                to_list.append(x.to_val)                               
            elif x.from_val < x.to_val and x.from_val > to_list[-1]:
                to_list.append(x.to_val)            
            else:
                raise ValidationError('Ranges are improper.Declare proper ranges between From and To columns.')


    name=fields.Char(string="Sequence")
    department_id=fields.Many2one('hr.department',string="Department")
    salaryrange_ids=fields.One2many('salaryrange.lines','salaryrange_id',string="Salaray Range")

    _sql_constraints = [('name_uniq','unique(department_id)','The Department should be unique')]

    @api.model
    def create(self, vals):
        ''' Method overridden for updating the sequence.'''
        vals['name'] = self.env['ir.sequence'].next_by_code('salary.band') or '/'
        return  super(SalaryBand, self).create(vals)


class SalaryRangeLines(models.Model):
    _name="salaryrange.lines"

    from_val = fields.Integer(string="From (Per Annum)")
    to_val = fields.Integer(string="To (Per Annum)")
    max_increment=fields.Float(string="Max Increment(%)")
    salaryrange_id=fields.Many2one('salary.band',string="")

    @api.onchange('from_val','to_val','max_increment')
    def onchange_score(self):
        ''' On change func() over the fields 'From','To','max Increment' to restrict the user 
	    entering the negative values.
	'''
        context = self.env.context
        if context.has_key('from_val') and self.from_val < 0:
            self.from_val = 0
            return {'warning':{'title':('Warning!'),'message':('Value cannot be negative.')}}
        elif context.has_key('to_val') and self.to_val < 0:
            self.to_val = 0
            return {'warning':{'title':('Warning!'),'message':('Value cannot be negative.')}}
        elif context.has_key('max_increment'):
            if self.max_increment < 0:
                self.max_increment = 0
                return {'warning':{'title':('Warning!'),'message':('Value cannot be negative.')}}
            elif self.max_increment > 100:
                self.max_increment = 0
                return {'warning':{'title':('Warning!'),'message':('Max Increment should not exceed 100.')}}
        return {}




