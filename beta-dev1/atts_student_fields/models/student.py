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

from collections import defaultdict

class StudentStudent(models.Model):
    ''' Defining a student information '''
    _inherit = 'student.student'
    _description = 'Student Information'
    
    
    @api.multi
    @api.depends('father_line','mother_line')
    def _compute_sibling(self):
        '''Method to calculate student sibling'''
        father_list=[]
        mother_list=[]
        student_list=[]
        obj=self.env["sibling.line"]
        for rec in self:
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
        if self.id in student_list:   
            student_list.remove(self.id)
        for rec in self:
            rec.sibling_line =[(0, 0, {'student_id':sibling_id,'student':rec.id}) for sibling_id in student_list]
        student_sibling_list=student_list   
        for student_sibling in student_sibling_list:
            print "===============",student_sibling_list,student_sibling
            #obj.create({'student':student_sibling,'student_id':student_sibling})
#             student_sibling_list.remove(student_sibling)
#             student_sibling_list.append(self.id)
            #for new_sibling in student_sibling_list:
                #obj.sibling_line =[(0, 0, {'student_id':sibling,'student':new_sibling}) for sibling in student_sibling_list]
#             student_sibling_list.append(student_sibling)
#             student_sibling_list=list(set(student_sibling_list))
#             print "-------------",student_sibling_list
    
           
    @api.multi
    @api.depends('date_of_birth')
    def _compute_student_age_1st_jan(self):
        '''Method to calculate student age'''
        current_dt = datetime.today()
        current_dt.replace(month=01, day=01)
        for rec in self:
            if rec.date_of_birth:
                start = datetime.strptime(rec.date_of_birth,
                                          DEFAULT_SERVER_DATE_FORMAT)
                age_calc = ((current_dt - start).days / 365)
                # Age should be greater than 0
                if age_calc > 0.0:
                    rec.age_1st_of_Jan = age_calc
    
    
    # #Student General Information
    active = fields.Boolean(default=True, help="If the active field is set to False, it will allow you to hide the payment term without removing it.")
    class_id = fields.Many2one('standard.standard', 'Class Admitted')
    admitted = fields.Selection([('yes', 'Yes'), ('no', 'NO')], 'Admitted')
    admissionDate = fields.Date('Admission Date')
    offer_letter_date = fields.Date('Letter Of Offer Sent Out On')
    class_history_line = fields.One2many('class.history', 'student_id', 'Class History')
    english_level_history_line = fields.One2many('english.level.history', 'student_id', 'English Level History')
    math_level_history_line = fields.One2many('math.level.history', 'student_id', 'Math Level History')
    transport_mode_history_line = fields.One2many('transport.mode.history', 'student_id', 'Transport Mode History')
    class_level = fields.Selection([('love', 'Love'), ('joy', 'Joy'), ('peace', 'Peace'), ('hope', 'Hope'), ('kindness', 'Kindness'), ('victory', 'Victory'), ('glory', 'Glory')],
                              'Class Level')
    class_number = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10')], "Class Number", default="5")
    date_of_integration = fields.Date('Date of Integration')
    programme = fields.Selection([('MID', 'MID'), ('ASD', 'ASD'), ('Integrated', 'Integrated')],
                              'Programme')
    last_change_programme = fields.Date('Last Change Programme')
    race_id = fields.Many2one('student.race', 'Race')
    race_selection = fields.Selection([('chinese', 'Chinese'), ('malay', 'Malay'), ('indian', 'Indian'), ('others', 'Others')],
                              'Race')
    age_1st_of_Jan = fields.Integer(compute='_compute_student_age_1st_jan', string='Age 1st of Jan',
                         readonly=True)
    
    birth_place_id = fields.Many2one('res.country', 'Place Of Birth')
    nationality_id = fields.Many2one('res.nationality', 'Nationality')
    citizenship_id = fields.Many2one('res.country', 'Citizenship')
    language_ids = fields.One2many('res.lang', 'lang_student_id', 'Language(s) Spoken')
    child_presently_staying = fields.Selection([('father', 'Father'), ('mother', 'Mother'), ('guardian', 'Guardian'), ('caregiver', 'Caregiver'), ('children_home', 'Children’s Home'), ('both parents', 'Both Parents'), ('others', 'Others')],
                              'Child Presently staying with')
    child_staying_with_whome = fields.Char('Presently Staying with')
    de_registration = fields.Selection([('graduation', 'Graduation'), ('transfer_school', 'Transfer school (SPED to SPED)'), ('premature_school', 'Premature School Leaver – Dropout'), ('others', 'Others')],
                             'De-Registration')
    de_registration_graduation = fields.Selection([('18_years_old', '18 years old'), ('further_education', 'Further education: DSS/MS/MVS'), ('aps_nl', 'APS/NL')], 'De-Registration Graduation')
                                  
    de_reg_comment = fields.Char("Others De-Registration")
    reason_of_withdrawal = fields.Char('Reason of Withdrawal')
    withdraw_date = fields.Date('Withdrawal Date')
    exit_qualifications = fields.Selection([('yes', 'Yes'), ('no', 'NO')],
                              'Exit Qualifications with WPLN (2-2-1)')
    type_of_accommodation = fields.Selection([('room_1', '1-room'), ('room_2', '2-room'), ('room_3', '3-room'), ('room_4', '4-room'), ('room_5', '5-room'), ('room_6', '6-room'), ('executive', 'Executive'), ('condominium', 'Condominium'), ('landed_property', 'Landed property')],
                              'Type of Accommodation')
    ownership_of_accommodation = fields.Selection([('rented', 'Rented'), ('owned', 'Owned'), ('others', 'Others')],
                              'Ownership of Accommodation')
    accommodation = fields.Char("Other Accommodation")
    
    nric_fin = fields.Char("NRIC/FIN")
    current_level = fields.Selection([('junior', 'Junior Level'), ('senior', 'Senior Level')], "Level")
    session = fields.Selection([('am', 'AM'), ('pm', 'PM')], "Session")
    # family section
    child_custody = fields.Selection([('father', 'Father'), ('mother', 'Mother'), ('parents', 'Parents'), ('guardian', 'Guardian'), ('caregiver', 'Caregiver'), ('other', 'Other')], "Child LEGAL Custody")
    other_caretaker = fields.Char('Child Caregiver Name', child_custody='other')
    birth_order = fields.Selection([('1', '1st'), ('2', '2nd'), ('3', '3rd'), ('4', '4th'), ('5', '5th'), ('6', '6th'), ('7', '7th'), ('8', '8th'), ('9', '9th'), ('10', '10th'), ('11', '11th'), ('12', '12th'), ('13', '13th'), ('14', '14th'), ('15', '15th')], "Child Birth Order")
    no_of_family_member = fields.Char('No. of Family Members (including the student)', help="No. of Family Members (including the student)")
    no_of_brother = fields.Char('No. of brother(s)', help="Relationship to client No. Of Brother(s)")
    no_of_sister = fields.Char('No. of sister(s)', help="Relationship to client No. of Sister(s)")
    sibling_in_school = fields.Char('Pupil with sibling in school ', help="Pupil with sibling in school (same family/same children’s home)")
    father_name = fields.Char('Father Name')
    father_occupation = fields.Char('Father Occupation')
    father_nric = fields.Char('NIRC')
    father_mobile_ids = fields.One2many('father.multiple.contact', 'student_id', 'Mobile Number')
    father_home_mob_no = fields.Char('Home Number')
    father_office_no = fields.Char('Office Number')
    father_citizenship = fields.Char('Citizenship')
    father_email = fields.Char('Email')
    father_dob = fields.Date('Birth Date')
    father_country_of_birth = fields.Many2one('res.country.state', 'Country of Birth')
    father_marital_status = fields.Selection([('single', 'Single'), ('married', 'Married'), ('separated', 'Separated'), ('divorced', 'Divorced'), ('widowed', 'Widowed'), ('deceased', 'Deceased')], "Marital Status")
    father_race_selection = fields.Selection([('chinese', 'Chinese'), ('malay', 'Malay'), ('indian', 'Indian'), ('others', 'Others')],
                              'Father Race')
    father_religion = fields.Char('Father Religion')
    father_qualification = fields.Selection([('no_formal_education', 'No formal education'), ('primary', 'Primary'), ('secondary', 'Secondary'), ('postsecondary', 'Postsecondary (A levels, Diploma, ITE)'), ('graduate', 'Graduate/Postgraduate')], "Qualification", default="postsecondary")
    father_language = fields.One2many('res.lang', 'student_id', 'Language')
    father_postal_code = fields.Char('Postal Code')
    father_ownership_of_accomodation = fields.Selection([('rented', 'Rented'), ('owned', 'Owned'), ('others', 'Others')], 'Father ownership of Accomodation')
    father_accomodation = fields.Selection([('1_room', '1-room'), ('2_room', '2-room'), ('3_room', '3-room'), ('4_room', '4-room'), ('5_room', '5-room'), ('6_room', '6-room'), ('executive', 'Executive'), ('condominium', 'Condominium'), ('landed_property', 'Landed property')], "Type of Accommodation(if differ from child)")
    father_other_accomodation = fields.Char('Other Accomodation')
    father_street = fields.Char('Street')
    father_street2 = fields.Char('Street2')
    father_city = fields.Char('city')
    father_state_id = fields.Many2one('res.country.state', 'State')
    father_zip = fields.Char('zip')
    father_country_id = fields.Many2one('res.country', 'Country')
    mother_name = fields.Char('Mother Name')
    mother_occupation = fields.Char('Mother Occupation')
    mother_nric = fields.Char('NIRC')
    mother_mobile_ids = fields.One2many('mother.multiple.contact', 'student_id', 'Mobile Number')
    mother_office_no = fields.Char('Office Number')
    mother_citizenship = fields.Char('Citizenship')
    mother_email = fields.Char('Email')
    mother_dob = fields.Date('Birth Date')
    mother_country_of_birth = fields.Many2one('res.country', 'Country of Birth')
    mother_marital_status = fields.Selection([('single', 'Single'), ('married', 'Married'), ('separated', 'Separated'), ('divorced', 'Divorced'), ('widowed', 'Widowed'), ('deceased', 'Deceased')], "Marital Status")
    mother_race_selection = fields.Selection([('chinese', 'Chinese'), ('malay', 'Malay'), ('indian', 'Indian'), ('others', 'Others')],
                              'Mother Race')
    mother_religion = fields.Char('Mother Religion')
    mother_qualification = fields.Selection([('no_formal_education', 'No formal education'), ('primary', 'Primary'), ('secondary', 'Secondary'), ('postsecondary', 'Postsecondary (A levels, Diploma, ITE)'), ('graduate', 'Graduate/Postgraduate')], "Qualification", default="postsecondary")
    mother_language = fields.One2many('res.lang', 'mother_id', 'Language')
    mother_postal_code = fields.Char('Postal Code')
    mother_accomodation = fields.Selection([('1_room', '1-room'), ('2_room', '2-room'), ('3_room', '3-room'), ('4_room', '4-room'), ('5_room', '5-room'), ('6_room', '6-room'), ('executive', 'Executive'), ('condominium', 'Condominium'), ('landed_property', 'Landed property')], "Type of Accommodation(if differ from child)")
    mother_ownership_of_accomodation = fields.Selection([('rented', 'Rented'), ('owned', 'Owned'), ('others', 'Others')], 'Mother ownership of Accommodation')
    mother_other_accomodation = fields.Char('Other Accomodation')
    mother_street = fields.Char('Street')
    mother_street2 = fields.Char('Street2')
    mother_city = fields.Char('city')
    mother_state_id = fields.Many2one('res.country.state', 'State')
    mother_zip = fields.Char('zip')
    mother_country_id = fields.Many2one('res.country', 'Country')
    # Guardian section
    guardian_ids = fields.One2many('guardian.line', 'student_id', 'Guardian')
    # caregiver section
    caregiver_ids = fields.One2many('caregiver.line', 'student_id', 'Caregiver')
    # Medical Information
    primary_disabilities = fields.Selection([('mild', 'Mild Intellectual'), ('autism_spectrum_disorder', 'Autism Spectrum Disorder'), ('other', 'Other Disability')], "Primary Disabilities")
    other_primary_disability = fields.Char('Specify Other Primary Disability')
    secondory_disability = fields.Char('Secondary Disabilities')
    medical_condition_background = fields.Char('Diagnosis Relevant to Referral/Medical Conditions Background')
    birth_history = fields.Char('Birth History & Development Milestones')
    development_milestone = fields.Char('Development Milestone')
    have_any_disability = fields.Boolean('Does the applicant have any Disabilities')
    mdd_disability = fields.Boolean('MDD')
    mdd_comment = fields.Char('MDD Comment')
    adhd_disability = fields.Boolean('ADHD')
    adhd_comment = fields.Char('ADHD Comment')
    anxiety_disorder_disability = fields.Boolean('Anxiety Disorder')
    anxiety_comment = fields.Char('Anxiety Disorder Comment')
    ocd_disability = fields.Boolean('OCD')
    ocd_comment = fields.Char('OCD Comment')
    other_disability = fields.Boolean('Other')
    specify_other_disability = fields.Char('Specify Other Condition')
    # medical condition fields
    diabetes = fields.Boolean('Diabetes')
    diabetes_comment = fields.Char('Diabetes Comment')
    seizure_disorder = fields.Boolean('Seizure Disorder (Epilepsy)')
    seizure_comment = fields.Char('Seizure Comment')
    asthma_disorder_disability = fields.Boolean('Asthma (Lungs)')
    asthma_comment = fields.Char('Asthma Comment')
    heart_disability = fields.Boolean('Heart Conditions')
    heart_comment = fields.Char('Heart Conditions Comment')
    cancer_disability = fields.Boolean('Cancer')
    cancer_comment = fields.Char('Cancer Comment')
    haemophilia_disorder = fields.Boolean('Haemophilia')
    haemophilia_comment = fields.Char('Haemophilia Comment')
    physical_disability = fields.Boolean('Physical Disability')
    physical_comment = fields.Char('Physical Disability Comment')
    dysmorphic_disability = fields.Boolean('Dysmorphic Features')
    dysmorphic_comment = fields.Char('Dysmorphic Comment')
    Others_disability = fields.Boolean('Others')
    Others_comment = fields.Char('Other')
    G6PD_deficiency = fields.Selection([('yes', 'Yes'), ('no', 'No')], "G6PD Deficiency")
    g6pd_comment = fields.Char('G6PD Comment')
    list_of_major_injury = fields.Selection([('yes', 'Yes'), ('no', 'No')],'List of major injuries and illnesses that require medical treatment, long – term therapy or hospitalizations')
    injury_comment = fields.Char('Injury Comment')
    currently_child_medication = fields.Selection([('yes', 'Yes'), ('no', 'No')], "Is the child currently on medication")
    medication = fields.Char('Medication')
    reason = fields.Char('Reason')
    dose = fields.Char('Dose')
    frequency = fields.Char('Frequency')
    medication_needed_in_school = fields.Selection([('yes', 'Yes'), ('no', 'No')], "Medications needed in School")
    medication_comment = fields.Char('Medication Comment')
    is_child_have_side_effect = fields.Selection([('yes', 'Yes'), ('no', 'No')], "Side effect of Medication on Child")
    side_effect_comment = fields.Char('Medication Side Effect')
    
    medicine_allergy = fields.Boolean('Medicine')
    medicine_allergy_comment = fields.Char('Medicine Comment')
    food_allergy = fields.Boolean('Food')
    food_allergy_comment = fields.Char('Food Comment')
    other_allergy = fields.Boolean('Other')
    other_allergy_comment = fields.Char('Allergy Comment')
    
    medical_precaution = fields.Char('Medical Precaution')
    medical_remarks = fields.Char('Remarks/Recommendations/Prognosis')
    
    musculoskeletal_system = fields.Boolean('Musculoskeletal System')
    musculoskeletal_system_comment = fields.Char('Musculoskeletal Comment')
    hearing_condition = fields.Boolean('Hearing Condition')
    hearing_condition_comment = fields.Char('Hearing Comment')
    vision_condition = fields.Boolean('Vision Condition')
    vision_comment = fields.Char('Vision Comment')
    head_circumference = fields.Selection([('normal', 'Normal'), ('microcephaly', 'Microcephaly'), ('macrocephaly', 'Macrocephaly')], "Head Circumference")
    
    unfit_pe = fields.Boolean('Unfit PE')
    unfit_pe_comment = fields.Char('Unfit PE Comment')
    unfit_swimming = fields.Boolean('Unfit Swimming')
    unfit_swimming_comment = fields.Char('Unfit Swimming Comment')
    hydrotherapy = fields.Boolean('Hydrotherapy')
    hydrotherapy_comment = fields.Char('Hydrotherapy Comment')
    horse_riding = fields.Boolean('Horse Riding')
    horse_riding_comment = fields.Char('Horse Riding Comment')
    other_physical_restriction = fields.Boolean('Others')
    other_physical_restriction_comment = fields.Char('Other Physical Restriction Comment')
    
    temporary_precaution = fields.Boolean('Temporary Precaution')
    temporary_precaution_comment = fields.Char('Precaution Comment')
    special_precaution = fields.Boolean('Special Precaution')
    special_precaution_comment = fields.Char('Special Precaution Comment')
    precaution_type = fields.Boolean('Precaution Type')
    
    low_intensity = fields.Boolean('LI – Exempt from low – intensity physical activities')
    contact_sport = fields.Boolean('CT – Exempt from contact sports and games')
    competive_sport = fields.Boolean('CS – Exempt from Competitive Sports')
    preferential_seating = fields.Boolean('PS – Preferential Seating')
    other_physical_precaution = fields.Boolean('OTH – Others')
    oth_comment = fields.Char('OTH Comment')
    physical_activity = fields.Boolean('MI – Exempt from moderate – intensity physical activities')
    physical_excercise = fields.Boolean('PE – Exempt from Physical Exercise')
    competitive_game = fields.Boolean('CG – Exempt from Competitive Games')
    subject = fields.Boolean('SC – Special Choice of subjects/Careers')
    intense_activity = fields.Boolean('EPL – Allow Watersports, Cycling on Roads, Climbing Heights, Gymnastics only under supervision')
    intense_physical = fields.Boolean('HI – Exempt from high – intensity physical activities')
    fitness_test = fields.Boolean('PFT – Exempt from Physical Fitness Test')
    graded_excercise = fields.Boolean('GPE – Requires modified/graded Physical Exercise')
    ast = fields.Boolean('AST – Exempt from PE during asthmatic attacks')
    pre_snacks = fields.Boolean('DM – Ensure extra snack before exercise, watch for symptoms/signs of hypoglycaemia')
    
    
    # wpln.line
    wpln_ids = fields.One2many('wpln.line', 'student_id', 'WPLN')
    # student Address
    address_line = fields.One2many('student.address', 'student_id', 'Address')
    studentId = fields.Char('Student ID', default=lambda obj:
                      obj.env['ir.sequence'].next_by_code('student.student'))
    applicationId = fields.Char('Application ID')
    middle = fields.Char('Middle Name', required=False, states={'done': [('readonly', True)]})
    last = fields.Char('Surname', required=False, states={'done': [('readonly', True)]})
    
    year = fields.Many2one('academic.year', 'Academic Year', required=False,
                           states={'done': [('readonly', True)]})
    
    
    father_line = fields.One2many('res.partner', 'student_father_id', 'Father Name')
    mother_line = fields.One2many('res.partner', 'student_mother_id', 'Mother Name')
    state = fields.Selection([('draft', 'Draft'),
                              ('done', 'Done'),
                              ('terminate', 'Terminate'),
                              ('alumni', 'Alumni')],
                             'State', readonly=True, default="draft")
    state_custom = fields.Selection([('de_register', 'De-register'),('withdraw', 'Withdraw'),('draft', 'Draft')],'Custom State',default='draft')
    
    sibling_line = fields.One2many('sibling.line','student', 'Sibling')
    
    
#     @api.multi
#     @api.onchange('father_line','mother_line')
#     def onchange_sibling(self):
#         '''Method to calculate student sibling'''
#         father_list=[]
#         mother_list=[]
#         student_list=[]
#         student_sibling_list=[]
#         res_other=[]
#         obj=self.env['sibling.line']
#         student_obj=self.env['student.student']
#         for rec in self:
#             father_line=rec.father_line
#             mother_line=rec.mother_line
#             if father_line:
#                 for line in father_line:
#                     father_list.append(line.nric)
#             if mother_line:
#                 for line in mother_line:
#                     mother_list.append(line.nric)
#         parent_nric=father_list+mother_list
#         parent_nric=list(set(parent_nric))            
#         parents=self.env["res.partner"].search([('nric','in',parent_nric)])
#         for parent in parents:
#             if parent.student_father_id:
#                 student_id=parent.student_father_id and parent.student_father_id.id
#                 student_list.append(student_id)
#             if parent.student_mother_id:
#                 student_id=parent.student_mother_id and parent.student_mother_id.id
#                 student_list.append(student_id)
#         student_list=list(set(student_list)) 
#         if self.id in student_list:   
#             student_list.remove(self.id)
# #         student_sibling_list=student_list
# #         res1=[]   
# #         for student_sibling in student_sibling_list:
# #             student_sibling_list.remove(student_sibling)
# #             student_sibling_list.append(self.id)
# #             res1=[(0, 0, {'student_id':sibling,'student':self.id}) for sibling in student_sibling_list]
# #             print"========res1==========",res1
# # #             for new_sibling in student_sibling_list:
# # #                 obj.create({'student':student_sibling,'student_id':new_sibling})
#                 
#         res=[(0, 0, {'student_id':sibling_id,'student':self.id}) for sibling_id in student_list]
#         print "----------res----------",res
#         #res=[(0, 0, {'student_id':sibling_id,'student':self.id}) for sibling_id in student_list]
#         return {'value': {'sibling_line':res}}
# #         for student in student_list:
# #             print "===student=====",student
# #             id=obj.create({'student':self.id,'student_id':student})
    
    
    
    """This onchange function is to select the level of student i.e senior or junior"""
    @api.multi
    @api.onchange('date_of_birth')
    def on_change_dob(self):
        current_dt = datetime.today()
        for rec in self:
            if rec.date_of_birth:
                start = datetime.strptime(rec.date_of_birth,
                                          DEFAULT_SERVER_DATE_FORMAT)
                age_calc = ((current_dt - start).days / 365)
                # Age should be greater than 0
                if age_calc > 0.0:
                    if age_calc >= 7 and age_calc <= 12:
                        rec.current_level = 'junior'
                    elif age_calc > 12 :
                        rec.current_level = 'senior'  
                        
    """This onchange function is to record date when was programme changed"""
    @api.multi
    @api.onchange('programme')
    def on_change_programme(self):
        today_date = datetime.now().date()
        self.last_change_programme = today_date
    
    @api.multi
    @api.onchange('de_registration','withdraw_date')
    def onchange_deactivation(self):
        if self.de_registration:
            for rec in self:
                rec.state_custom = 'de_register'
        if self.withdraw_date:
            for rec in self:
                rec.state_custom = 'withdraw'
        return {}
    
    
class StudentPreviousSchool(models.Model):
    '''Defining a student previous school information '''
    _inherit = "student.previous.school"
    _description = "Student Previous School" 
    registration_no = fields.Char('Registration No.', required=False)
    course_id = fields.Many2one('standard.standard', 'Course', required=False)
    
    
class class_history(models.Model):
    ''' Defining a student Class History '''
    _name = "class.history"
    _description = "Class History" 
    
    class_code = fields.Char('Class Code')
    class_level = fields.Char('Class Level')
    class_number = fields.Char('Class Number')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    teacher_id = fields.Many2one('hr.employee', 'Teacher’s Name')
    student_id = fields.Many2one('student.student', 'Student')
    
class english_level_history(models.Model):
    ''' Defining a student English Level History '''
    _name = "english.level.history"
    _description = "Defining a student English Level History" 
    
    level_name = fields.Char('Level Name')
    english_level_number = fields.Char('English Level Number')
    english_score = fields.Char('English Score')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    teacher_id = fields.Many2one('hr.employee', 'Teacher’s Name')
    student_id = fields.Many2one('student.student', 'Student')
    
    
class math_level_history(models.Model):
    ''' Defining a student Math Level History '''
    _name = "math.level.history"
    _description = "Defining a student Math Level History" 
    
    level_name = fields.Char('Level Name')
    math_level_number = fields.Char('Math Level Number')
    math_score = fields.Char('Math Score')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    teacher_id = fields.Many2one('hr.employee', 'Teacher’s Name')
    student_id = fields.Many2one('student.student', 'Student')
    
class transport_mode_history(models.Model):
    ''' Defining a student Transport Mode History '''
    _name = "transport.mode.history"
    _description = "Defining a student Transport Mode History" 
    
    transport_mode_in = fields.Selection([('private_transport', 'Private transport arrangement'), ('public_transport', 'Public transport'), ('school_bus', 'School Bus')], "Transport Mode–In")
    ##### mode in
    car = fields.Boolean('Car')
    comments_car = fields.Char('Comments')
    walk_home = fields.Boolean('Walk home')
    comments_walk_home = fields.Char('Comments')
    others_private = fields.Boolean('Others')
    comments_private_others = fields.Char('Comments')
    mtr = fields.Boolean('MRT')
    public_bus = fields.Boolean('Public Bus')
    taxi = fields.Boolean('Taxi')
    comments_taxi = fields.Char('Comments')
    others_public = fields.Boolean('Others')
    comments_public_other = fields.Char('Comments')
    a_to_z = fields.Boolean('A-Z')
    a_to_z_school_bus = fields.Selection([('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E'), ('F', 'F'), ('G', 'G'), ('H', 'H'), ('I', 'I'), ('J', 'J'), ('K', 'K'), ('L', 'L'), ('M', 'M'), ('N', 'N'), ('O', 'O'), ('P', 'P'), ('Q', 'Q'), ('R', 'R'), ('S', 'S'), ('T', 'T'), ('U', 'U'), ('V', 'V'), ('W', 'W'), ('X', 'X'), ('Y', 'Y'), ('Z', 'Z')], "Select")
    others_school_bus = fields.Boolean('Others')
    comments_school_bus_other = fields.Char('Comments')
    ###### Model Out
    transport_mode_out = fields.Selection([('private_transport', 'Private transport arrangement'), ('public_transport', 'Public transport'), ('school_bus', 'School Bus')], "Transport Mode-Out")
    car_out = fields.Boolean('Car')
    comments_car_out = fields.Char('Comments')
    walk_home_out = fields.Boolean('Walk home')
    comments_walk_home_out = fields.Char('Comments')
    others_private_out = fields.Boolean('Others')
    comments_private_others_out = fields.Char('Comments')
    mtr_out = fields.Boolean('MRT')
    public_bus_out = fields.Boolean('Public Bus')
    taxi_out = fields.Boolean('Taxi')
    comments_taxi_out = fields.Char('Comments')
    others_public_out = fields.Boolean('Others')
    comments_public_other_out = fields.Char('Comments')
    a_to_z_out = fields.Boolean('A-Z')
    a_to_z_school_bus_out = fields.Selection([('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E'), ('F', 'F'), ('G', 'G'), ('H', 'H'), ('I', 'I'), ('J', 'J'), ('K', 'K'), ('L', 'L'), ('M', 'M'), ('N', 'N'), ('O', 'O'), ('P', 'P'), ('Q', 'Q'), ('R', 'R'), ('S', 'S'), ('T', 'T'), ('U', 'U'), ('V', 'V'), ('W', 'W'), ('X', 'X'), ('Y', 'Y'), ('Z', 'Z')], "Select")
    others_school_bus_out = fields.Boolean('Others')
    comments_school_bus_other_out = fields.Char('Comments')
   
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    student_id = fields.Many2one('student.student', 'Student')
       

class transport_mode(models.Model):
    ''' Defining a student Transport Mode '''
    _name = "transport.mode"
    _description = "Defining a student Transport Mode" 
    name = fields.Char('Transport Mode' , required=True)

class StudentRace(models.Model):
    ''' Defining a student Race '''
    _name = "student.race"
    _description = "Defining a student Race" 
    _order = 'sort'
    
    name = fields.Char('Race' , required=True)
    sort = fields.Integer('Sort')
    


class Res_Lang(models.Model):
    '''This Class is inherited to add lang in student form'''
    _inherit = 'res.lang'
    
    student_id = fields.Many2one('student.student', 'Student')
    lang_student_id = fields.Many2one('student.student', 'Student')
    mother_id = fields.Many2one('student.student', 'Student')
    guardian_id = fields.Many2one('student.student', 'Student')
    caregiver_id = fields.Many2one('student.student', 'Student')
    
    
class student_guardian_line(models.Model):
    _name = 'student.guardian.line'
    _description = 'Details of Gaurdians'
    
    name = fields.Char('Name')
    guardian_id = fields.Many2one('guardian.line', 'Guardian')
    student_id = fields.Many2one('student.student', 'Student')
    
    
class guardian_line(models.Model):
    _name = 'guardian.line'
    _description = 'Details of Gaurdians'
    
    student_id = fields.Many2one('student.student', 'Student')
    name = fields.Char('Guardian Name')
    guardian_nric = fields.Char('NRIC/FIN')
    guardian_home_no = fields.Char('Guardian Home Number')
    guardian_mobile_ids = fields.One2many('guardian.multiple.contact', 'student_id', 'Guardian Mobile Number')
    guardian_office_no = fields.Char('Office Number')
    guardian_citizenship = fields.Char('Citizenship')
    guardian_email = fields.Char('Email')
    guardian_dob = fields.Date('Birth Date')
    guardian_country_of_birth = fields.Many2one('res.country', 'Country of Birth')
    guardian_marital_status = fields.Selection([('single', 'Single'), ('married', 'Married'), ('separated', 'Separated'), ('divorced', 'Divorced'), ('widowed', 'Widowed'), ('deceased', 'Deceased')], "Marital Status")
    guardian_race_selection = fields.Selection([('chinese', 'Chinese'), ('malay', 'Malay'), ('indian', 'Indian'), ('others', 'Others')],
                              'Guardian Race')
    guardian_religion = fields.Char('Guardian Religion')
    guardian_qualification = fields.Selection([('no_formal_education', 'No formal education'), ('primary', 'Primary'), ('secondary', 'Secondary'), ('postsecondary', 'Postsecondary (A levels, Diploma, ITE)'), ('graduate', 'Graduate/Postgraduate')], "Qualification", default="postsecondary")
    guardian_language = fields.One2many('res.lang', 'guardian_id', 'Language(s) Spoken')
    guardian_postal_code = fields.Char('Postal Code')
    guardian_accomodation = fields.Selection([('1_room', '1-room'), ('2_room', '2-room'), ('3_room', '3-room'), ('4_room', '4-room'), ('5_room', '5-room'), ('6_room', '6-room'), ('executive', 'Executive'), ('condominium', 'Condominium'), ('landed_property', 'Landed property')], "Type of Accommodation")
    guardin_ownership_of_accomodation = fields.Selection([('rented', 'Rented'), ('owned', 'Owned'), ('others', 'Others')], 'Ownership of Accommodation')
    guardian_other_accomodation = fields.Char('Other Accomodation')
    guardian_street = fields.Char('Street')
    guardian_street2 = fields.Char('Street2')
    guardian_city = fields.Char('city')
    guardian_state_id = fields.Many2one('res.country.state', 'State')
    guardian_zip = fields.Char('zip')
    guardian_country_id = fields.Many2one('res.country', 'Country')
    guardian_gender = fields.Selection([('male', 'Male'), ('female', 'Female')], "Guardian Gender")
    guardian_relation_with_student_id = fields.Many2one('student.relation','Relationship to Student')
    occupation_id = fields.Many2one('occupation','Occupation')
    occupation = fields.Char('Occupation')
    race_id = fields.Many2one('student.race','Race')
    religion_id = fields.Many2one('student.cast','Religion')
    
    
class caregiver_line(models.Model):
    _name = 'caregiver.line'
    _description = 'Details of Caregiver'
    
    student_id = fields.Many2one('student.student', 'Student')
    name = fields.Char('Caregiver Name')
    caregiver_nric = fields.Char('NRIC/FIN')
    caregiver_mobile_ids = fields.One2many('caregiver.multiple.contact', 'student_id', 'Caregiver Mobile Number')
    caregiver_office_no = fields.Char('Office Number')
    caregiver_citizenship = fields.Char('Citizenship')
    caregiver_email = fields.Char('Email')
    caregiver_dob = fields.Date('Birth Date')
    caregiver_country_of_birth = fields.Many2one('res.country', 'Country of Birth')
    caregiver_marital_status = fields.Selection([('single', 'Single'), ('married', 'Married'), ('separated', 'Separated'), ('divorced', 'Divorced'), ('widowed', 'Widowed'), ('deceased', 'Deceased')], "Marital Status")
    caregiver_race_selection = fields.Selection([('chinese', 'Chinese'), ('malay', 'Malay'), ('indian', 'Indian'), ('others', 'Others')],
                              'Caregiver Race')
    caregiver_religion = fields.Char('Caregiver Religion')
    caregiver_qualification = fields.Selection([('no_formal_education', 'No formal education'), ('primary', 'Primary'), ('secondary', 'Secondary'), ('postsecondary', 'Postsecondary (A levels, Diploma, ITE)'), ('graduate', 'Graduate/Postgraduate')], "Qualification", default="postsecondary")
    caregiver_language = fields.One2many('res.lang', 'caregiver_id', 'Language(s) Spoken')
    caregiver_postal_code = fields.Char('Postal Code')
    caregiver_accomodation = fields.Selection([('1_room', '1-room'), ('2_room', '2-room'), ('3_room', '3-room'), ('4_room', '4-room'), ('5_room', '5-room'), ('6_room', '6-room'), ('executive', 'Executive'), ('condominium', 'Condominium'), ('landed_property', 'Landed property')], "Type of Accommodation")
    caregiver_ownership_of_accomodation = fields.Selection([('rented', 'Rented'), ('owned', 'Owned'), ('others', 'Others')], 'Ownership of Accommodation')
    caregiver_other_accomodation = fields.Char('Other Accomodation')
    caregiver_street = fields.Char('Street')
    caregiver_street2 = fields.Char('Street2')
    caregiver_city = fields.Char('city')
    caregiver_state_id = fields.Many2one('res.country.state', 'State')
    caregiver_zip = fields.Char('zip')
    caregiver_country_id = fields.Many2one('res.country', 'Country')
    caregiver_relation_with_student_id = fields.Many2one('student.relation','Relationship to Student')
    occupation_id = fields.Many2one('occupation','Occupation')
    occupation = fields.Char('Occupation')
    race_id = fields.Many2one('student.race','Race')
    religion_id = fields.Many2one('student.cast','Religion')
    
    
class StudentDescription(models.Model):
    ''' Defining a Student Description and adding related columns in description'''
    _inherit = 'student.description'

    emer_relation_with_student = fields.Char('Emergency Relationship')
    relation_selection = fields.Selection([('parent', 'Parents'), ('caregiver', 'Caregivers'), ('guardian', 'Guardians'),('others', 'Others')], "Relation")
    parent_id = fields.Many2one('res.partner', 'Parent')
    caregiver_id = fields.Many2one('caregiver.line', 'Caregiver')
    guardian_id = fields.Many2one('guardian.line', 'Guardian') 
    
#     @api.model 
#     def default_get(self, fields):
#         rec = super(StudentDescription, self).default_get(fields)
#         print"=============",self.id
#         context = dict(self._context or {})
#         rec.update({
#             'name':context.get('name'),
#         })
#         return rec
    
    
    
    @api.multi
    @api.onchange('relation_selection')
    def relation_selection_change(self):
        try:
            parent_list, father_list, mother_list, caregiver_list, guardian_list = [], [], [], [], []
            student_id = self.des_id
            if student_id:
                if self.relation_selection == 'parent':
                    father_line = student_id.father_line
                    mother_line = student_id.mother_line
                    if father_line:
                        for father_id in father_line:
                            father_id.father = True
                            father_list.append(father_id.id)
                    if mother_line:
                        for mother_id in mother_line:
                            mother_id.mother = True
                            mother_list.append(mother_id.id)
                    if father_list or mother_list:
                        parent_list = father_list + mother_list
                        if parent_list:
                            return {'value': {'parent_id':parent_list}, 'domain':{'parent_id':[('id', 'in', parent_list)]}}
                    else:
                        return {'value': {'parent_id':parent_list}, 'domain':{'parent_id':[('id', 'in', [])]}}
                if self.relation_selection == 'caregiver':
                    caregiver_line = student_id.caregiver_ids
                    for caregiver_id in caregiver_line:
                        caregiver_list.append(caregiver_id.id)
                    return {'value': {'caregiver_id':caregiver_list}, 'domain':{'caregiver_id':[('id', 'in', caregiver_list)]}} 
                if self.relation_selection == 'guardian':
                    guardian_line = student_id.guardian_ids
                    for guardian_id in guardian_line:
                        guardian_list.append(guardian_id.id)
                    return {'value': {'guardian_id':guardian_list}, 'domain':{'guardian_id':[('id', 'in', guardian_list)]}}  
            else:   
                return True
        except TypeError:
            return True
            pass
        
    @api.multi
    @api.onchange('parent_id')
    def parent_id_change(self):
        father_contact = ''
        mother_contact = ''
        mother_list = []
        father_list = []
        parent_id = self.parent_id
        name = parent_id.name
        mobile = parent_id.mobile
        is_father = parent_id.father
        is_mother = parent_id.mother
        self.name = name
        if is_father:
            mobile_ids = parent_id.father_mobile_ids
            for mobile_id in mobile_ids:
                father_list.append(mobile_id.father_no)
            if father_list:
                father_contact = ",".join(str(x) for x in father_list)
            self.description = father_contact
            self.emer_relation_with_student = 'Father'
        elif is_mother:
            mobile_ids = parent_id.mother_mobile_ids
            for mobile_id in mobile_ids:
                mother_list.append(mobile_id.mother_no)
            if mother_list:
                mother_contact = ",".join(str(x) for x in mother_list)
            self.description = mother_contact
            self.emer_relation_with_student = 'Mother'
            
    @api.multi
    @api.onchange('caregiver_id')
    def caregiver_id_change(self):
        contact_list = []
        caregiver_id = self.caregiver_id
        name = caregiver_id.name
        mobile_ids = caregiver_id.caregiver_mobile_ids
        for mobile_id in mobile_ids:
            contact_list.append(mobile_id.caregiver_no)
        if contact_list:
            contact = ",".join(str(x) for x in contact_list)
            self.description = contact
        caregiver_relation_with_student = caregiver_id.caregiver_relation_with_student_id.id
        self.name = name
        self.emer_relation_with_student = caregiver_relation_with_student
        
    @api.multi
    @api.onchange('guardian_id')
    def guardian_id_change(self):
        contact_list = []
        guardian_id = self.guardian_id
        name = guardian_id.name
        mobile_ids = guardian_id.guardian_mobile_ids
        for mobile_id in mobile_ids:
            contact_list.append(mobile_id.guardian_no)
        if contact_list:
            contact = ",".join(str(x) for x in contact_list)
            self.description = contact
        guardian_relation_with_student = guardian_id.guardian_relation_with_student_id.name
        self.name = name
        self.emer_relation_with_student = guardian_relation_with_student
        
class wpln_line(models.Model):
    _name = "wpln.line"
    _description = "Contains details of child's Analytical Skill"
    
    name = fields.Char('Name')
    student_id = fields.Many2one('student.student', 'Student')
    year = fields.Date('Year') 
    reading = fields.Char('Reading')
    listening = fields.Char('Listening')
    numeracy = fields.Char('Numeracy')
    speaking = fields.Char('Speaking')
    writing = fields.Char('Writing')
    
        
        
        
class father_multiple_contact(models.Model):
    _name = 'father.multiple.contact'     
    _description = 'Multiple contact of parents are managed here'
    
    _rec_name = "father_no"
    
    student_id = fields.Many2one('student.student', 'Student')
    parent_id = fields.Many2one('res.partner', 'Father')
    father_no = fields.Char('Father Contact')

class guardian_multiple_contact(models.Model):
    _name = 'guardian.multiple.contact'     
    _description = 'Multiple contact of guardian are managed here'
    
    _rec_name = "guardian_no"
    
    student_id = fields.Many2one('student.student', 'Student')
    guardian_no = fields.Char('Guardian Contact')

class caregiver_multiple_contact(models.Model):
    _name = 'caregiver.multiple.contact'     
    _description = 'Multiple contact of caregiver are managed here'
    
    _rec_name = "caregiver_no"
    
    student_id = fields.Many2one('student.student', 'Student')
    caregiver_no = fields.Char('Caregiver Mobile Number')
    
class mother_multiple_contact(models.Model):
    _name = 'mother.multiple.contact'     
    _description = 'Multiple contact of parents are managed here'
    
    _rec_name = "mother_no"
    
    student_id = fields.Many2one('student.student', 'Student')
    parent_id = fields.Many2one('res.partner', 'Mother')
    mother_no = fields.Char('Mother Contact')
    
class student_address(models.Model):
    _name = 'student.address'     
    _description = 'Student Address'
    
    living_independently = fields.Boolean('Live Independently', default='True')
    # other_contact_numbers = fields.Char('Other Contact Numbers')
    # phone_home = fields.Char('Telephone Home')
    street = fields.Char('Street')
    street = fields.Char('Street2')
    zip = fields.Char('Zip', size=24)
    city = fields.Char('City')
    state_id = fields.Many2one("res.country.state", 'State')
    country_id = fields.Many2one("res.country", 'Country')
    # phone = fields.Char('Phone')
    # email = fields.Char('Email')
    # mobile = fields.Char('Mobile')
    student_id = fields.Many2one('studnt.student', 'Student')
    
        
class rescountry(models.Model):
    _inherit = 'res.country'
    _order = 'sort'
    
    sort = fields.Integer('Sort') 
    
    
class resnationality(models.Model):
    _name = 'res.nationality'
    
    name = fields.Char('Nationality', required="True")
    student_ids = fields.One2many('student.student', 'nationality_id' , 'Student')
    
class student_cast(models.Model):
    _inherit = 'student.cast'
    
    student_ids = fields.One2many('student.student', 'cast_id' , 'Student')
    
class student_relation(models.Model):
    _name = 'student.relation'
    
    name = fields.Char('Relationship', required="True")
    

class sibling_line(models.Model):
    _name = 'sibling.line'
    
    student = fields.Many2one('student.student', 'Student')
    student_id = fields.Many2one('student.student', 'Student')



