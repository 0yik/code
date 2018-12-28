# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from pygments.lexer import _inherit

class ClassClass(models.Model):
    _inherit = 'class.class'
    
    @api.multi
    def name_get(self):
        if 'master_list' in self._context:
            return [(rec.id, rec.class_level + ' ' + rec.class_no) for rec in self]
        else:
            return super(ClassClass,self).name_get()

class MasterList(models.Model):
    _name = 'master.list'
    _rec_name = "student_id"
    
    @api.depends('student_id')
    def compute_default_set(self):
        for rec in self:
            sp_list = []
            ot_list = []
            ap_list = []
            pc_list = []
            sw_list = []
            tc_list = []
            if rec.student_id:
                sp_ids = self.env['hr.employee'].search([('designation_id.name','=','Speech Therapist')])
                ot_ids = self.env['hr.employee'].search([('designation_id.name','=','Occupational Therapist')])
                ap_ids = self.env['hr.employee'].search([('designation_id.name','=','Art Psychotherapist')])
                pc_ids = self.env['hr.employee'].search([('designation_id.name','=','Psychologist')])
                sw_ids = self.env['hr.employee'].search([('designation_id.name','=','Social Worker')])
                tc_ids = self.env['hr.employee'].search([('designation_id.name','=','Teacher Counsellor')])
                
                for sp_id in sp_ids:
                    sp_ot = self.env['ot.ap.list'].search([('intervention_id.student_id','=',rec.student_id.id),('ap_id','=', sp_id.id)])
                    sp_st = self.env['st.ap.list'].search([('intervention_id.student_id','=',rec.student_id.id),('ap_id','=', sp_id.id)])
                    sp_cm = self.env['cm.ap.list'].search([('intervention_id.student_id','=',rec.student_id.id),('ap_id','=', sp_id.id)])
                    sp_dict = {'sp_id': sp_id.id,
                               'number': len(sp_ot) + len(sp_st) + len(sp_cm)}
                    sp_list.append(sp_dict)
                for ot_id in ot_ids:
                    ot_ot = self.env['ot.ap.list'].search([('intervention_id.student_id','=',rec.student_id.id),('ap_id','=', ot_id.id)])
                    ot_st = self.env['st.ap.list'].search([('intervention_id.student_id','=',rec.student_id.id),('ap_id','=', ot_id.id)])
                    ot_cm = self.env['cm.ap.list'].search([('intervention_id.student_id','=',rec.student_id.id),('ap_id','=', ot_id.id)])
                    ot_dict = {'ot_id': ot_id.id,
                               'number': len(ot_ot) + len(ot_st) + len(ot_cm)}
                    ot_list.append(ot_dict)
                for ap_id in ap_ids:
                    ap_ot = self.env['ot.ap.list'].search([('intervention_id.student_id','=',rec.student_id.id),('ap_id','=', ap_id.id)])
                    ap_st = self.env['st.ap.list'].search([('intervention_id.student_id','=',rec.student_id.id),('ap_id','=', ap_id.id)])
                    ap_cm = self.env['cm.ap.list'].search([('intervention_id.student_id','=',rec.student_id.id),('ap_id','=', ap_id.id)])
                    ap_dict = {'ap_id': ap_id.id,
                               'number': len(ap_ot) + len(ap_st) + len(ap_cm)}
                    ap_list.append(ap_dict)
                for pc_id in pc_ids:
                    pc_ot = self.env['ot.ap.list'].search([('intervention_id.student_id','=',rec.student_id.id),('ap_id','=', pc_id.id)])
                    pc_st = self.env['st.ap.list'].search([('intervention_id.student_id','=',rec.student_id.id),('ap_id','=', pc_id.id)])
                    pc_cm = self.env['cm.ap.list'].search([('intervention_id.student_id','=',rec.student_id.id),('ap_id','=', pc_id.id)])
                    pc_dict = {'pc_id': pc_id.id,
                               'number': len(pc_ot) + len(pc_st) + len(pc_cm)}
                    pc_list.append(pc_dict)
                for sw_id in sw_ids:
                    sw_ot = self.env['ot.ap.list'].search([('intervention_id.student_id','=',rec.student_id.id),('ap_id','=', sw_id.id)])
                    sw_st = self.env['st.ap.list'].search([('intervention_id.student_id','=',rec.student_id.id),('ap_id','=', sw_id.id)])
                    sw_cm = self.env['cm.ap.list'].search([('intervention_id.student_id','=',rec.student_id.id),('ap_id','=', sw_id.id)])
                    sw_dict = {'sw_id': sw_id.id,
                               'number': len(sw_ot) + len(sw_st) + len(sw_cm)}
                    sw_list.append(sw_dict)
                for tc_id in tc_ids:
                    tc_ot = self.env['ot.ap.list'].search([('intervention_id.student_id','=',rec.student_id.id),('ap_id','=', tc_id.id)])
                    tc_st = self.env['st.ap.list'].search([('intervention_id.student_id','=',rec.student_id.id),('ap_id','=', tc_id.id)])
                    tc_cm = self.env['cm.ap.list'].search([('intervention_id.student_id','=',rec.student_id.id),('ap_id','=', tc_id.id)])
                    tc_dict = {'tc_id': tc_id.id,
                               'number': len(tc_ot) + len(tc_st) + len(tc_cm)}
                    tc_list.append(tc_dict)
            self.sp_line = sp_list
            self.ot_line = ot_list
            self.ap_line = ap_list
            self.pc_line = pc_list
            self.sw_line = sw_list
            self.tc_line = tc_list
    
    student_id = fields.Many2one("student.student", string="Name of Student", required=True)
    class_id = fields.Many2one("class.class", string="Class", required=True)
    class_teacher_id = fields.Many2one("hr.employee", string="Class Teacher")
    class_teacher_related = fields.Many2one("hr.employee", related="class_teacher_id", string="Class Teacher")
    sp_line = fields.One2many('speech.therapist','sp_master_id', string="Speech Therapist", compute="compute_default_set", store=True)
    ot_line = fields.One2many('occupational.therapist','ot_master_id', string="Occupational Therapist", compute="compute_default_set", store=True)
    ap_line = fields.One2many('art.psychotherapist','ap_master_id', string="Art Psychotherapist", compute="compute_default_set", store=True)
    pc_line = fields.One2many('psychologist','pc_master_id', string="Psychologist", compute="compute_default_set", store=True)
    sw_line = fields.One2many('social.worker','sw_master_id', string="Social Worker", compute="compute_default_set", store=True)
    tc_line = fields.One2many('teacher.counsellor','tc_master_id', string="Teacher Counsellor", compute="compute_default_set", store=True)
    financial_assistance = fields.Integer("Financial Assistance")
    remarks = fields.Text("Remarks")
    default_set = fields.Boolean("Default Set", default=True)
    
    @api.onchange('class_id')
    def onchange_class_id(self):
        if self.class_id:
            self.class_teacher_id = self.class_id.class_teacher_id
            
class SpeechTherapist(models.Model):
    _name = 'speech.therapist'

    sp_master_id = fields.Many2one("master.list", string="Master List")
    sp_id = fields.Many2one("hr.employee", string="Speech Therapist")
    number = fields.Integer("Number")
    
class OccupationalTherapist(models.Model):
    _name = 'occupational.therapist'
 
    ot_master_id = fields.Many2one("master.list", string="Master List")
    ot_id = fields.Many2one("hr.employee", string="Occupational Therapist")
    number = fields.Integer("Number")
     
class ArtPsychotherapist(models.Model):
    _name = 'art.psychotherapist'
 
    ap_master_id = fields.Many2one("master.list", string="Master List")
    ap_id = fields.Many2one("hr.employee", string="Art Psychotherapist")
    number = fields.Integer("Number")
     
class Psychologist(models.Model):
    _name = 'psychologist'
 
    pc_master_id = fields.Many2one("master.list", string="Master List")
    pc_id = fields.Many2one("hr.employee", string="Psychologist")
    number = fields.Integer("Number")
     
class SocialWorker(models.Model):
    _name = 'social.worker'
 
    sw_master_id = fields.Many2one("master.list", string="Master List")
    sw_id = fields.Many2one("hr.employee", string="Social Worker")
    number = fields.Integer("Number")
     
class TeacherCounsellor(models.Model):
    _name = 'teacher.counsellor'
 
    tc_master_id = fields.Many2one("master.list", string="Master List")
    tc_id = fields.Many2one("hr.employee", string="Teacher Counsellor")
    number = fields.Integer("Number")