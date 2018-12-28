# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

import time
from datetime import date, datetime
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.modules import get_module_resource
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, \
    DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import except_orm, Warning as UserError
from openerp.exceptions import ValidationError
# added import statement in try-except because when server runs on
# windows operating system issue arise because this library is not in Windows.
try:
    from odoo.tools import image_colorize, image_resize_image_big
except:
    image_colorize = False
    image_resize_image_big = False


class ResPartner(models.Model):
    '''Defining a address information '''
    _inherit = 'res.partner'
    _description = 'Address Information'
#    _inherits = {'res.partner': 'parent_school'}
    
#    parent_school = fields.Boolean('Is A Parent', default=True)
    father = fields.Boolean('Is Father')  
    mother = fields.Boolean('Is Mother')
    occupation_id = fields.Many2one('occupation','Occupation')
    occupation = fields.Char('Occupation')
    nric = fields.Char('NRIC/FIN')
    father_mobile_ids = fields.One2many('father.multiple.contact', 'parent_id', 'Mobile Number')
    mother_mobile_ids = fields.One2many('mother.multiple.contact', 'parent_id', 'Mobile Number')
    home_mob_no = fields.Char('Home Number')
    office_no = fields.Char('Office Number')
    citizenship = fields.Char('Citizenship')
    dob = fields.Date('Birth Date')
    country_of_birth = fields.Many2one('res.country.state', 'Country of Birth')
    marital_status = fields.Selection([('single', 'Single'), ('married', 'Married'), ('separated', 'Separated'), ('divorced', 'Divorced'), ('widowed', 'Widowed'), ('deceased', 'Deceased')], "Marital Status")
    race_id = fields.Many2one('student.race','Race')
    religion_id = fields.Many2one('student.cast','Religion')
    race = fields.Char('Race')
    religion = fields.Char('Religion')
    
    qualification = fields.Selection([('no_formal_education', 'No formal education'), ('primary', 'Primary'), ('secondary', 'Secondary'), ('postsecondary', 'Postsecondary (A levels, Diploma, ITE)'), ('graduate', 'Graduate/Postgraduate')], "Qualification", default="postsecondary")
    language = fields.One2many('res.lang', 'student_id', 'Language(s) Spoken')
    ownership_of_accomodation = fields.Selection([('rented', 'Rented'), ('owned', 'Owned'), ('others', 'Others')], 'ownership of Accomodation')
    accomodation = fields.Selection([('1_room', '1-room'), ('2_room', '2-room'), ('3_room', '3-room'), ('4_room', '4-room'), ('5_room', '5-room'), ('6_room', '6-room'), ('executive', 'Executive'), ('condominium', 'Condominium'), ('landed_property', 'Landed property')], "Type of Accommodation (if differ from child)")
    other_accomodation = fields.Char('Other Accomodation')
    student_father_id = fields.Many2one('student.student', 'Student')
    student_mother_id = fields.Many2one('student.student', 'Student')
    parent_relation_with_student_id = fields.Many2one('student.relation','Relationship to Student')
#     street = fields.Char('Street')
#     street2 = fields.Char('Street2')
#     city = fields.Char('city')
#     state_id = fields.Many2one('res.country.state', 'State')
#     zip = fields.Char('zip')
#     country_id = fields.Many2one('res.country', 'Country')


    @api.model
    def create(self, vals):
        '''Method creates parents assign group parents'''
        res = super(ResPartner, self).create(vals)
        print "============",vals
        if res:
            self.update_student_sibling(vals,res.id)
#         # Create user
#         if res and res.parent_school:
#             user_vals = {'name': vals.get('name'),
#                          'login': vals.get('email', False),
#                          'password': vals.get('email', False),
#                          'partner_id': res.id}
#             user = self.env['res.users'].create(user_vals)
#             # Assign group of parents to user created
#             emp_grp = self.env.ref('base.group_user')
#             parent_group = self.env.ref('atts_course.group_school_parent')
#             if user:
#                 user.write({'groups_id': [(6, 0, [emp_grp.id, parent_group.id]
#                                            )]})
        return res


    def update_student_sibling(self,vals,res_id):

        father_list=[]
        mother_list=[]
        student_list=[]
        student_id=0
        obj_sibling=self.env["sibling.line"]
        obj_student=self.env["student.student"]
        obj_partner=self.env["res.partner"]
        if vals.get("mother") == True:
            student_id=obj_partner.browse(res_id).student_mother_id.id
        elif vals.get("father") == True:
            student_id=obj_partner.browse(res_id).student_father_id.id
        if student_id:
            for rec in obj_student.browse(student_id):
                father_line=rec.father_line
                mother_line=rec.mother_line
                if father_line:
                    for line in father_line:
                        father_list.append(line.nric)
                if mother_line:
                    for line in mother_line:
                        mother_list.append(line.nric)
            parent_nric=father_list+mother_list
            parent_nric=list(set(parent_nric))            
            parents=self.env["res.partner"].search([('nric','in',parent_nric)])
            for parent in parents:
                if parent.student_father_id:
                    student_id=parent.student_father_id and parent.student_father_id.id
                    student_list.append(student_id)
                if parent.student_mother_id:
                    student_id=parent.student_mother_id and parent.student_mother_id.id
                    student_list.append(student_id)
            student_list=list(set(student_list)) 
            for  student_id in student_list: 
                sibling_list=[]  
                student_sibling_list=student_list
                for line in obj_student.browse(student_id).sibling_line:
                    sibling_list.append(line.student_id.id)
                #student_sibling_list.remove(student_id)
                for sibling in student_sibling_list:
                    if sibling != student_id:
                            if sibling not in sibling_list:
                                obj_sibling.create({'student':student_id,'student_id':sibling})
                #student_sibling_list=list(set(student_sibling_list))
                    #rec.sibling_line =[(0, 0, {'student_id':sibling_id,'student':rec.id}) for sibling_id in student_list]
#             student_sibling_list=student_list   
#             for student_sibling in student_sibling_list:
#                 print "===============",student_sibling_list,student_sibling
        

class Occupation(models.Model):
    '''Occupation '''
    _name = 'occupation'
    _description = 'Occupation'
    
    name = fields.Char('Occupation',required=True)
