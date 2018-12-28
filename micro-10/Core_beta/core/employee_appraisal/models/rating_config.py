# -*- coding: utf-8 -*- 
from odoo import fields,models,api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError

class RatingLines(models.Model):
    _name="rating.lines"
    _description = "Rating Lines"

    department_id=fields.Many2one('hr.department',string="Department")
    score=fields.Integer(string="Full Score",default=3)
    comment=fields.Text(string="Note")
    rating_config_id=fields.Many2one('rating.config')

    @api.onchange('score')
    def onchange_score(self):
	''' On change func() over the field 'Full Score' to restrict entering the zero/negative values.'''
	if self.score <= 0:
	    self.score = 3
	    return {'warning':{'title':('Warning!'),'message':('Value cannot be zero/negative.')}}
        return {}


class RatingConfig(models.Model):
    _name="rating.config"
    _description ="Rating Config"
    
    rating_seq=fields.Char(string="Rating Sequence No")
    name = fields.Char(string="Rating Name")
    rating_ids = fields.One2many('rating.lines','rating_config_id',string="Ratings")

    _sql_constraints = [ ( 'name_uniq','unique(name)','Rating name should be unique.')]

    @api.model
    def create(self,vals):
        ''' Method Overridden to
	    1) Creates the weightage lines of the related department.
	    2) Creates the Rating values.
	'''
        vals['rating_seq']=self.env['ir.sequence'].next_by_code('rating.config') or '/'
        obj = super(RatingConfig,self).create(vals)
        lst = []
        lis= []
	### Creates the weightage lines of the related department.
        for line in obj.rating_ids:
            if line.department_id.id in lst:
                raise ValidationError(_("No duplication of department selection"))
            else:
                lst.append(line.department_id.id)

            dep_obj = self.env['hr.department'].search([('name','=',line.department_id.name)])
            dic = {
                  'weightage_line_ids':[ (0,0,{'rating_id':obj.id}) ]
                  }
            dep_obj.write(dic)
            lis.append((obj.id, line.department_id.id, line.score))

	### Creates the sequence of Rating values.
        rating_val_pool = self.env['rating.values']
        for tup in lis:
            if tup[2] != 0:
                rating_val_pool.create({'department_id':tup[1], 'rating_id':tup[0], 'name':'0'})
                for i in range(0, tup[2]):
                    rating_val_pool.create({'department_id':tup[1], 'rating_id':tup[0], 'name':i+0.5})
                    rating_val_pool.create({'department_id':tup[1], 'rating_id':tup[0], 'name':i+1})                    
        return obj


    @api.multi
    def write(self,vals):
        ''' Method Overridden to
            1) Creates the weightage lines of the related department.
            2) Creates/Updates the  Rating values.
        '''
        dep_list=[]
        for line in self.rating_ids:
            dep_list.append(line.department_id.id)

        obj = super(RatingConfig,self).write(vals)
        lst = []
        lis= []
        new_dep_list = []
	### Creates the weightage lines of the related department.
        for line in self.rating_ids:
            new_dep_list.append(line.department_id.id)
            if line.department_id.id in lst:
                raise ValidationError(_("No duplication of department selection"))
            else:
                lst.append(line.department_id.id)
            if line.department_id.id not in dep_list:
                dep_obj = self.env['hr.department'].search([('name','=',line.department_id.name)])
                dic = {
                     'weightage_line_ids':[ (0,0,{'rating_id':self.id}) ]
                      }
                dep_obj.write(dic)
            lis.append((self.id, line.department_id.id, line.score))

	### Creates/Updates the  Rating values.
        if vals.has_key('rating_ids'):
            rating_val_pool = self.env['rating.values']
            for tup in lis:
                rating_value = rating_val_pool.search([('department_id','=',tup[1]),('rating_id','=',tup[0])], limit=1, order = "name desc") or False
                if rating_value: 
                    if tup[2] > float(rating_value.name):
                        for i in range(int(float(rating_value.name)), tup[2]):
                            rating_val_pool.create({'department_id':tup[1], 'rating_id':tup[0], 'name':i+0.5})
                            rating_val_pool.create({'department_id':tup[1], 'rating_id':tup[0], 'name':i+1})   
                else:
                    if tup[2] != 0:
                        rating_val_pool.create({'department_id':tup[1], 'rating_id':tup[0], 'name':'0'})
                        for i in range(0, tup[2]):
                            rating_val_pool.create({'department_id':tup[1], 'rating_id':tup[0], 'name':i+0.5})
                            rating_val_pool.create({'department_id':tup[1], 'rating_id':tup[0], 'name':i+1})     
        for x in dep_list:
            if x not in new_dep_list:
                dep_obj = self.env['hr.department'].browse(x)
                for line in dep_obj.weightage_line_ids:
                    if line.rating_id.id == self.id:
                        dic = {
                                'weightage_line_ids':[ (2,line.id,0) ]
                              }
                        dep_obj.write(dic)
        return obj

    @api.multi
    def unlink(self):
        ''' To restrict the deletion of records which are been referencing from other objects.'''
        for obj in self:
            obj_found = self.env['emp.rating.lines'].search([('rating_label_id','=',obj.id),('emp_rating_id','!=',False)], limit=1) or False
            if obj_found:
                raise ValidationError("You cannot delete the rating, as it is tagged in the Evaluation Process.")
        return super(RatingConfig,self).unlink()


    
class RatingValues(models.Model):
    _name = "rating.values"
    _description = "Rating Values"
    
    name = fields.Char('Value')
    department_id = fields.Many2one('hr.department', 'Department')
    rating_id = fields.Many2one('rating.config', 'Rating')
    
    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        ''' Method Overridden to populate the Rating values in the Evaluation Form lines.'''
        if args is None:
            args = []
	context = self.env.context
        if context is None:
            context={}
        if context.has_key('eval_department_id') and context.has_key('eval_rating_id') and context.has_key('full_score'):
	    full_score = self.env['rating.values'].browse(context['full_score']).name
            if float(full_score) > 0:
                score_ids = self.env['rating.values'].search([('department_id','=',context['eval_department_id']),('rating_id','=',context['eval_rating_id']),('name','<=',str(full_score))]) or False
		if score_ids:
                    args += [('id','in',score_ids.ids)]
		else:
		    args = [('id','=',False)]
            else:
                args = [('id','=',False)]


        return super(RatingValues, self).name_search(name, args=args, operator=operator, limit=limit)

