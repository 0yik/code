# -*- coding: utf-8 -*- 
from odoo import fields,models,api 
from openerp.exceptions import ValidationError


class AttendancePercentage(models.Model):
    _name = 'attendance.percentage'
    _rec_name = 'rating'
    

    @api.one
    @api.constrains('from_val','to_val')
    def _check_validations(self):
	''' Method will check the following
	    1) From, To fields values validations
	    2) No case of Percentage overlapping.
	'''
	if self.from_val == 0 and self.to_val == 0:
            raise ValidationError('Please enter values. From and To Values are zero')            
        if self.from_val >= self.to_val:
            raise ValidationError(" 'From' value should be less than 'To' value")
        att_objs = self.env['attendance.percentage'].search([])         
        to_list = [0]
        for obj in att_objs:
            if obj.from_val < obj.to_val and obj.from_val == 0 and to_list[-1] == 0:
                to_list.append(obj.to_val)
            elif obj.from_val < obj.to_val and obj.from_val > to_list[-1]:
                to_list.append(obj.to_val)
            else:
                raise ValidationError('No percentage range can be overlapped.')

    from_val = fields.Float(string="FROM (%)")
    to_val = fields.Float(string="To (%)")
    rating = fields.Float(string="Rating")
	
    @api.onchange('rating')
    def onchange_rating(self):
        ''' Onchange over the Rating field to restrict the user entering irregular formats.'''
        if self.rating and (self.rating < 0 or str(self.rating).split('.')[1] not in ['0','5']):
            self.rating = 0
            return {'warning':{'title':('Warning'),'message':('Rating should be in the Proper format (For eg. 0,0.5,1,1.5,2,2.5,.....). It should not be negative.')}}


    @api.onchange('from_val','to_val')
    def onchange_ranges(self):
        ''' Onchange over the fields From(%), To (%) to restrict the user entering improper values.'''
        context = self.env.context
        if context.has_key('from_val'):
            if self.from_val < 0:
                self.from_val = 0
                return {'warning':{'message':('Value cannot be zero/negative.')}}
        elif context.has_key('to_val'):
            if self.to_val < 0:
                self.to_val = 0
                return {'warning':{'message':('Value cannot be zero/negative.')}}
            elif self.to_val > 100:
                self.to_val = 0
                return {'warning':{'message':('To value should not exceed 100.')}}

