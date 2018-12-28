# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError

class APIntervention(models.Model):
    _name = 'ap.intervention'
    _rec_name = 'student_id'

    @api.multi
    def _related_hod(self):
        for rec in self:
            hod_id = self.env['hr.employee'].search([('user_id', '=', self.env.user.id), ('designation_id.name', '=', 'HOD')])
            if hod_id:
                rec.hod_id = hod_id[0].id
    @api.multi
    def _related_teacher(self):
        for rec in self:
            teacher_id = self.env['hr.employee'].search([('user_id', '=', self.env.user.id), ('designation_id.name', '=', 'Teacher')])
            if teacher_id:
                rec.teacher_id = teacher_id[0].id  
    @api.multi
    def _related_principal(self):
        for rec in self:
            principal_id = self.env['hr.employee'].search([('user_id', '=', self.env.user.id), ('designation_id.name', '=', 'Principal')])
            if principal_id:
                rec.principal_id = principal_id[0].id
                         
    referrel_type = fields.Selection([
        ('ot', 'OT'),
        ('st', 'ST'),
        ('cm', 'CM')], string='Referral Type')

    date_referrel = fields.Date("Date of Referral")
    attachment = fields.Binary('Referral Form')
    file_name = fields.Char('File Name')
    student_id = fields.Many2one("student.student", string="Student")
    hod_id = fields.Many2one("hr.employee", string="HOD", compute='_related_hod')
    principal_id = fields.Many2one("hr.employee", string="Principal", compute='_related_principal')
    teacher_id = fields.Many2one("hr.employee", string="Teacher", compute='_related_teacher')
    ap_assigned = fields.Many2one("hr.employee", string="AP Assigned")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('ap_assigned', 'AP Assigned'),
        ('assessment_uploaded', 'Assessment Uploaded'),
        ('approved', 'Approved'),], string='State', default='draft')
    # OT FIELDS
    
    ot_assessment = fields.Binary('Assessment')
    ot_assessment_file_name = fields.Char('File Name')
    ot_presenting_issue = fields.Char('Presenting Issue')
    ot_underlying_issue = fields.Char('Underlying Issue')
    ot_intervention_summary = fields.Binary('Intervention Summary')
    ot_intervention_summary_file_name = fields.Char('File Name')
    ot_miscellaneous = fields.Binary('Miscellaneous')
    ot_miscellaneous_file_name = fields.Char('File Name')
    ot_termly_updates = fields.Text('Termly Updates')
    ot_ap_list_line = fields.One2many('ot.ap.list', 'intervention_id', string='AP List')
    ot_discharge_transfer = fields.Binary('Case Discharge / Transfer')
    ot_discharge_transfer_file_name = fields.Char('File Name')
    
    # ST FIELDS
    
    st_assessment = fields.Binary('Assessment')
    st_assessment_file_name = fields.Char('File Name')
    st_presenting_issue = fields.Char('Presenting Issue')
    st_underlying_issue = fields.Char('Underlying Issue')
    st_intervention_summary = fields.Binary('Intervention Summary')
    st_intervention_summary_file_name = fields.Char('File Name')
    st_miscellaneous = fields.Binary('Miscellaneous')
    st_miscellaneous_file_name = fields.Char('File Name')
    st_termly_updates = fields.Text('Termly Updates')
    st_ap_list_line = fields.One2many('st.ap.list', 'intervention_id', string='AP List')
    st_discharge_transfer = fields.Binary('Case Discharge / Transfer')
    st_discharge_transfer_file_name = fields.Char('File Name')
    
    # CM FIELDS
    
    cm_assessment = fields.Binary('Assessment')
    cm_assessment_file_name = fields.Char('File Name')
    cm_pre_sdq_score = fields.Char("Pre-SDQ Score")
    cm_post_sdq_score = fields.Char("Post-SDQ Score")
    cm_presenting_issue = fields.Char('Presenting Issue 1')
    cm_presenting_issue2 = fields.Char('Presenting Issue 2')
    cm_presenting_issue3 = fields.Char('Presenting Issue 3')
    cm_underlying_issue = fields.Char('Underlying Issue 1')
    cm_underlying_issue2 = fields.Char('Underlying Issue 2')
    cm_underlying_issue3 = fields.Char('Underlying Issue 3')
    cm_intervention_goal = fields.Char('Intervention Goal 1')
    cm_intervention_goal2 = fields.Char('Intervention Goal 2')
    cm_intervention_goal3 = fields.Char('Intervention Goal 3')
    cm_intervention_summary = fields.Binary('Intervention Summary')
    cm_intervention_summary_file_name = fields.Char('File Name')
    cm_miscellaneous = fields.Binary('Miscellaneous')
    cm_miscellaneous_file_name = fields.Char('File Name')
    cm_termly_updates = fields.Text('Termly Updates')
    cm_pre_sdq_score = fields.Float('Pre-SDQ Score')
    cm_post_sdq_score = fields.Float('Post-SDQ Score')
    cm_ap_list_line = fields.One2many('cm.ap.list', 'intervention_id', string='AP List')
    cm_discharge_transfer = fields.Binary('Case Discharge / Transfer')
    cm_discharge_transfer_file_name_cm = fields.Char('File Name')
    
    # Out Of Session Report Line
    
    report_line = fields.One2many('session.report.line', 'intervention_id', string='AP List')

    @api.model
    def create(self, vals):
        
        user_obj=self.env['res.users'].browse(self._context.get('uid'))
        staff_id=self.env['hr.employee'].search([('address_home_id','=',user_obj.partner_id.id)])
        staff_obj=self.env['hr.employee'].browse(staff_id.id)
        staff_designation=staff_obj.designation_id.name
        if staff_designation or user_obj.id == 1:
            if staff_designation:
                staff_designation = staff_designation.upper()
            if staff_designation =='HOD' or staff_designation =='ALLIED PROFESSIONAL ASSOCIATE' or staff_designation =='CONTRACT SENIOR OCCUPTIONAL THERAPIST' or staff_designation =='SENIOR OCCUPATIONAL THERAPIST' or staff_designation =='OCCUPATIONAL THERAPIST' or staff_designation =='PASTORAL GUIDANCE OFFICER' or staff_designation =='SENIOR PSYCHOLOGIST' or staff_designation =='PSYCHOLOGIST' or staff_designation =='SENIOR SPEECH THERAPIST' or staff_designation =='SPEECH THERAPIST' or staff_designation =='SENIOR SOCIAL WORKER' or staff_designation =='SOCIAL WORKER' or staff_designation =='SENIOR ART PSYCHOTHERAPIST' or user_obj.id == 1 or staff_designation =='TEACHER':
                res = super(APIntervention, self).create(vals)
                if vals.get('file_name', False):
                    mail_ids=[]
                    hod_ids = self.env['hr.employee'].search([('designation_id.name', '=', 'HOD')])
                    mail_server=self.env["ir.mail_server"].search([])
                    mail_mail_obj=self.env["mail.mail"]
                    email_server=self.env["ir.mail_server"].search([])
                    email=email_server[0].smtp_user
                    subject='A new Referral Form has been uploaded'
                    class_codes=res.student_id.class_history_line
                    student_class_codes=''
                    for class_code in class_codes:
                        student_class_codes=student_class_codes+' '+str(class_code.class_code)
                    body="<br>"+"Name:"+str(res.student_id.name)+"<br>"+"NRIC/FIN:"+str(res.student_id.nric_fin)+"<br>"+"Class:"+student_class_codes
                    for hod in hod_ids:
                        values = {
                                        'body_html': body,
                                        'subject': subject,
                                        'email_to':hod.work_email,
                                        'email_from':email or '',
                                        }
                        mail_ids.append(mail_mail_obj.create(values))
                        mail_mail_obj.send(mail_ids)
                        values={}
                    
                if vals.get('st_assessment_file_name', False) or vals.get('ot_assessment_file_name', False) or vals.get('cm_assessment_file_name', False):
                    mail_ids=[]
                    hod_ids = self.env['hr.employee'].search([('designation_id.name', '=', 'Principal')])
                    mail_server=self.env["ir.mail_server"].search([])
                    mail_mail_obj=self.env["mail.mail"]
                    email_server=self.env["ir.mail_server"].search([])
                    email=email_server[0].smtp_user
                    subject='Waiting for Approval'
                    class_codes=res.student_id.class_history_line
                    student_class_codes=''
                    for class_code in class_codes:
                        student_class_codes=student_class_codes+' '+str(class_code.class_code)
                    body="<br>"+"Name:"+str(res.student_id.name)+"<br>"+"NRIC/FIN:"+str(res.student_id.nric_fin)+"<br>"+"Class:"+student_class_codes
                    for hod in hod_ids:
                        values = {
                                        'body_html': body,
                                        'subject': subject,
                                        'email_to':hod.work_email,
                                        'email_from':email or '',
                                        }
                        mail_ids.append(mail_mail_obj.create(values))
                        mail_mail_obj.send(mail_ids)
                        values={}
                    res.state = 'assessment_uploaded'
                return res
            else:
                raise UserError(_('You do not have access right to create/modify.'))
        else:
            raise UserError(_('You do not have access right to create/modify.')) 
    @api.multi
    def write(self, vals):
        user_obj=self.env['res.users'].browse(self._context.get('uid'))
        staff_id=self.env['hr.employee'].search([('address_home_id','=',user_obj.partner_id.id)])
        staff_obj=self.env['hr.employee'].browse(staff_id.id)
        staff_designation=staff_obj.designation_id.name
        if staff_designation or user_obj.id == 1:
            if staff_designation:
                staff_designation = staff_designation.upper()
            if staff_designation =='HOD' or staff_designation =='ALLIED PROFESSIONAL ASSOCIATE' or staff_designation =='CONTRACT SENIOR OCCUPTIONAL THERAPIST' or staff_designation =='SENIOR OCCUPATIONAL THERAPIST' or staff_designation =='OCCUPATIONAL THERAPIST' or staff_designation =='PASTORAL GUIDANCE OFFICER' or staff_designation =='SENIOR PSYCHOLOGIST' or staff_designation =='PSYCHOLOGIST' or staff_designation =='SENIOR SPEECH THERAPIST' or staff_designation =='SPEECH THERAPIST' or staff_designation =='SENIOR SOCIAL WORKER' or staff_designation =='SOCIAL WORKER' or staff_designation =='SENIOR ART PSYCHOTHERAPIST' or user_obj.id == 1 or staff_designation =='TEACHER':
                if staff_designation.upper()=='TEACHER':
                    new_vals={}
                    new_vals['attachment']=vals.get('attachment')
                    res = super(APIntervention, self).write(vals)
                else:
                    res = super(APIntervention, self).write(vals)

                if vals.get('attachment'):
                    mail_ids = []
                    hod_ids = self.env['hr.employee'].search([('designation_id.name', '=', 'HOD')])
                    mail_server = self.env["ir.mail_server"].search([])
                    mail_mail_obj = self.env["mail.mail"]
                    email_server = self.env["ir.mail_server"].search([])
                    email = email_server[0].smtp_user
                    subject = 'Teacher Upload referral Form please fill APassign'
                    class_codes = self.student_id.class_history_line
                    student_class_codes = ''
                    for class_code in class_codes:
                        student_class_codes = student_class_codes + ' ' + str(class_code.class_code)
                    body = "<br>" + "Name:" + str(self.student_id.name) + "<br>" + "NRIC/FIN:" + str(
                        self.student_id.nric_fin) + "<br>" + "Class:" + student_class_codes
                    for hod in hod_ids:
                        values = {
                            'body_html': body,
                            'subject': subject,
                            'email_to': hod.work_email,
                            'email_from': email or '',
                        }
                        mail_ids.append(mail_mail_obj.create(values))
                        mail_mail_obj.send(mail_ids)
                        values = {}

                if vals.get('file_name', False):
                    mail_ids=[]
                    hod_ids = self.env['hr.employee'].search([('designation_id.name', '=', 'HOD')])
                    mail_server=self.env["ir.mail_server"].search([])
                    mail_mail_obj=self.env["mail.mail"]
                    email_server=self.env["ir.mail_server"].search([])
                    email=email_server[0].smtp_user
                    subject='A new Referral Form has been uploaded'
                    class_codes=self.student_id.class_history_line
                    student_class_codes=''
                    for class_code in class_codes:
                        student_class_codes=student_class_codes+' '+str(class_code.class_code)
                    body="<br>"+"Name:"+str(self.student_id.name)+"<br>"+"NRIC/FIN:"+str(self.student_id.nric_fin)+"<br>"+"Class:"+student_class_codes
                    for hod in hod_ids:
                        values = {
                                        'body_html': body,
                                        'subject': subject,
                                        'email_to':hod.work_email,
                                        'email_from':email or '',
                                        }
                        mail_ids.append(mail_mail_obj.create(values))
                        mail_mail_obj.send(mail_ids)
                        values={}
                    
                if vals.get('ap_assigned', False):
                    mail_ids=[]
                    user_obj=self.env['hr.employee'].browse(self.ap_assigned.id)
                    email_server=self.env["ir.mail_server"].search([])
                    mail_mail_obj=self.env["mail.mail"]
                    email=email_server[0].smtp_user
                    subject='AP Intervention Assigned'
                    body="<br>"+"Name:"+str(self.student_id.name)+"<br>"+"Referrel Type:"+str(self.referrel_type)
                    values = {
                                        'body_html': body,
                                        'subject': subject,
                                        'email_to':user_obj.work_email,
                                        'email_from':email or '',
                                        }
                    mail_ids.append(mail_mail_obj.create(values))
                    mail_mail_obj.send(mail_ids)
                    self.state = 'ap_assigned'
                    
                if vals.get('st_assessment_file_name', False) or vals.get('ot_assessment_file_name', False) or vals.get('cm_assessment_file_name', False):
                    mail_ids=[]
                    hod_ids = self.env['hr.employee'].search([('designation_id.name', '=', 'Principal')])
                    mail_server=self.env["ir.mail_server"].search([])
                    mail_mail_obj=self.env["mail.mail"]
                    email_server=self.env["ir.mail_server"].search([])
                    email=email_server[0].smtp_user
                    subject='Waiting for Approval'
                    class_codes=self.student_id.class_history_line
                    student_class_codes=''
                    for class_code in class_codes:
                        student_class_codes=student_class_codes+' '+str(class_code.class_code)
                    body="<br>"+"Name:"+str(self.student_id.name)+"<br>"+"NRIC/FIN:"+str(self.student_id.nric_fin)+"<br>"+"Class:"+student_class_codes
                    for hod in hod_ids:
                        values = {
                                        'body_html': body,
                                        'subject': subject,
                                        'email_to':hod.work_email,
                                        'email_from':email or '',
                                        }
                        mail_ids.append(mail_mail_obj.create(values))
                        mail_mail_obj.send(mail_ids)
                        values={}
                    self.state = 'assessment_uploaded'
                return res
            else:
                raise UserError(_('You do not have access right to create/modify.')) 
        else:
            raise UserError(_('You do not have access right to create/modify.')) 
    @api.multi
    def approved_by_principal(self):
        if self.state == 'assessment_uploaded':
            self.state = 'approved'
        else:
            raise UserError(_('Before Approval first upload the Assessment'))

class SessionReportLine(models.Model):
    _name = 'session.report.line'
    
    @api.model
    def default_get(self, fields):
        res = {}
        context = self._context
        if context:
            context_keys = context.keys()
            next_sequence = 1
            if 'report_line' in context_keys:
                if len(context.get('report_line')) > 0:
                    next_sequence = len(context.get('report_line')) + 1
        res.update({'sr_no': next_sequence})
        return res
    
    intervention_id = fields.Many2one("ap.intervention", string="Intervention")
    sr_no = fields.Integer("Sr No.")
    date_time = fields.Datetime("Date & Time")
    people_involved = fields.Char("People Involved (excluding recorder)")
    remarks = fields.Char("Remarks")
    miscellaneous = fields.Binary('Miscellaneous')
    miscellaneous_file_name = fields.Char('File Name')
    
class OTAPList(models.Model):
    _name = 'ot.ap.list'
    
    intervention_id = fields.Many2one("ap.intervention", string="Intervention")
    ap_id = fields.Many2one("hr.employee", string="AP")
    remarks = fields.Char("Remarks")
    therapy_goals = fields.Char("Therapy Goals")
    date_planned = fields.Date("Date Planned")
    date_achieved = fields.Date("Date Achieved")
    type_intervention = fields.Selection([
        ('individual', 'Individual'),
        ('paired', 'Paired'),
        ('group', 'Group'),
        ('classroom', 'Classroom'),
        ('intervention', 'Intervention'),
        ('consulation', 'Consultation')], string='Type of Intervention')
    frequency_therapy = fields.Selection([
        ('weekly', 'Weekly'),
        ('fortnightly', 'Fortnightly'),
        ('monthly', 'Monthly'),
        ('daily', 'Daily'),
        ('ad hoc', 'Ad Hoc')], string='Frequency of Therapy')
    date = fields.Date("Date of Commencement")
    activities = fields.Text("Activities/Observations/Progress/Remarks")
    miscellaneous = fields.Binary('Miscellaneous')
    miscellaneous_file_name = fields.Char('File Name')

class STAPList(models.Model):
    _name = 'st.ap.list'
    
    intervention_id = fields.Many2one("ap.intervention", string="Intervention")
    ap_id = fields.Many2one("hr.employee", string="AP")
    remarks = fields.Char("Remarks")
    therapy_goals = fields.Char("Therapy Goals")
    date_planned = fields.Date("Date Planned")
    date_achieved = fields.Date("Date Achieved")
    type_intervention = fields.Selection([
        ('individual', 'Individual'),
        ('paired', 'Paired'),
        ('group', 'Group'),
        ('classroom', 'Classroom'),
        ('intervention', 'Intervention'),
        ('consulation', 'Consultation')], string='Type of Intervention')
    frequency_therapy = fields.Selection([
        ('weekly', 'Weekly'),
        ('fortnightly', 'Fortnightly'),
        ('monthly', 'Monthly'),
        ('daily', 'Daily'),
        ('ad hoc', 'Ad Hoc')], string='Frequency of Therapy')
    date = fields.Date("Date of Commencement")
    activities = fields.Text(" ")
    miscellaneous = fields.Binary('Miscellaneous')
    miscellaneous_file_name = fields.Char('File Name')

class CMAPList(models.Model):
    _name = 'cm.ap.list'
    
    intervention_id = fields.Many2one("ap.intervention", string="Intervention")
    ap_id = fields.Many2one("hr.employee", string="AP")
    remarks = fields.Char("Remarks")
    therapy_goals = fields.Char("Therapy Goals")
    date_planned = fields.Date("Date Planned")
    date_achieved = fields.Date("Date Achieved")
    type_intervention = fields.Char("Type of Intervention")
    counselling_psychotherapy = fields.Boolean(string="Counselling & Psychotherapy")
    sandplay = fields.Boolean(string="Sandplay Therapy")
    play_therapy = fields.Boolean(string="Play Therapy")
    art_psychotherapy = fields.Boolean(string="Art Psychotherapy")
    behaviour_therapy = fields.Boolean(string="Behaviour Therapy")
    others = fields.Boolean(string="Others")
    comments = fields.Text('Comments')
    
    # Counselling Psychotherapy Fields
    
    cp_session_no = fields.Char("Session No")
    cp_date_time = fields.Datetime("Date & Time")
    cp_themes = fields.Char("Theme(s)")
    cp_process = fields.Text("Process (S.O.A.P)")
    cp_follow_up = fields.Text("Follow-Up")
    cp_affect_behaviour = fields.Boolean("Affect/Behaviour")
    cp_comments = fields.Text("Comments")
    cp_miscellaneous = fields.Binary('Miscellaneous')
    cp_miscellaneous_file_name = fields.Char('File Name')
    
    # Affect Behaviour Fields
    
    ab_afraid = fields.Selection([
                ('anxious', 'Anxious'),
                ('distrustful', 'Distrustful'),
                ('fearful', 'Fearful'),
                ('helpless', 'Helpless'),
                ('nervous', 'Nervous'),
                ('scared', 'Scared'),
                ('terrified', 'Terrified'),
                ('vulnerable', 'Vulnerable'),
                ('weak', 'Weak')], string='Affraid')
    ab_sad = fields.Selection([
                ('discouraged', 'Discouraged'),
                ('disappointed', 'Disappointed'),
                ('hopeless', 'Hopeless'),
                ('lonely', 'Lonely'),
                ('pessimistic', 'Pessimistic')], string='Sad')
    ab_angry = fields.Selection([
                ('annoyed', 'Annoyed'),
                ('frustrated', 'Frustrated'),
                ('impatient', 'Impatient'),
                ('irritated', 'Irritated'),
                ('jealous', 'Jealous')], string='Angry')
    ab_happy = fields.Selection([
                ('cheerful', 'Cheerful'),
                ('excited', 'Excited'),
                ('pleased', 'Pleased'),
                ('relieved', 'Relieved'),
                ('satisfied', 'Satisfied')], string='Happy')
    ab_confident = fields.Selection([
                ('authoritative', 'Authoritative'),
                ('brave', 'Brave'),
                ('determined', 'Determined'),
                ('free', 'Free'),
                ('proud', 'Proud'),
                ('optimistic', 'Optimistic'),
                ('powerful', 'Powerful'),
                ('strong', 'Strong')], string='Confident')
    ab_hesitant = fields.Selection([
                ('ashamed', 'Ashamed'),
                ('confused', 'Confused'),
                ('embarrassed', 'Embarrassed'),
                ('inadequate', 'Inadequate'),
                ('mistrust', 'Mistrust'),
                ('nervous', 'Nervous'),
                ('timid', 'Timid'),
                ('uncertain', 'Uncertain')], string='Hesitant')
    ab_curious = fields.Selection([
                ('interested', 'Interested'),
                ('focused', 'Focused')], string='Curious')
    ab_flat = fields.Selection([
                ('ambiguous', 'Ambiguous'),
                ('constricted', 'Constricted'),
                ('dissociative', 'Dissociative'),
                ('restricted', 'Restricted')], string='Flat')
    
    # SandPlay Fields
    
    sp_session_no = fields.Char("Session No")
    sp_date_time = fields.Datetime("Date & Time")
    sp_type_sandtray = fields.Selection([
                ('wet', 'Wet'),
                ('dry', 'Dry')], string='Type of Sandtray')
    sp_time_sandtray = fields.Char("Time took to complete Sandtray")
    sp_miniatures = fields.Boolean(string="Miniatures")
    sp_process_description = fields.Char("Process Description")
    sp_overall_theme = fields.Boolean("Overall Theme")
    sp_subject_affect = fields.Boolean("Subject Affect")
    sp_observations_session = fields.Text("Behavioural Observations During Session")
    sp_sand_comments = fields.Text("Content of Conversation/Comments Made by Client before and/or after Working in Sand")
    sp_follow_up = fields.Text("Plan/Recommendation/Follow-up")
    
    # Miniatures Fields
    
    mn_people_hero = fields.Boolean("People – Heroes/ Heroines e.g. Superman")
    mn_people_hero_txt = fields.Char("People – Heroes/ Heroines")
    mn_people_occu = fields.Boolean("People – Occupational e.g. policeman")
    mn_people_occu_txt = fields.Char("People – Occupational")
    mn_people_histo = fields.Boolean("People – Historical e.g. king and queen")
    mn_people_histo_txt = fields.Char("People – Historical")
    mn_people_family = fields.Boolean("People – Family / Friends")
    mn_people_family_txt = fields.Char("People – Family / Friends")
    mn_fantasy_magical = fields.Boolean("Fantasy – Magical characters e.g. witch, wizard")
    mn_fantasy_magical_txt = fields.Char("Fantasy – Magical characters")
    mn_fantasy_animals = fields.Boolean("Fantasy – Animals e.g. unicorn")
    mn_fantasy_animals_txt = fields.Char("Fantasy – Animals")
    mn_fantasy_monsters = fields.Boolean("Fantasy – Monsters e.g. Frankenstein, vampire")
    mn_fantasy_monsters_txt = fields.Char("Fantasy – Monsters")
    mn_fantasy_folk = fields.Boolean("Fantasy – Folk e.g. Cinderella")
    mn_fantasy_folk_txt = fields.Char("Fantasy – Folk")
    mn_fantasy_cartoon = fields.Boolean("Fantasy – Cartoon e.g. Ben Ten")
    mn_fantasy_cartoon_txt = fields.Char("Fantasy – Cartoon")
    mn_fantasy_movie = fields.Boolean("Fantasy – Movie e.g. Harry Potter")
    mn_fantasy_movie_txt = fields.Char("Fantasy – Movie")
    mn_animals_farm = fields.Boolean("Animals – Farm/ Domestic e.g. cow")
    mn_animals_farm_txt = fields.Char("Animals – Farm/ Domestic")
    mn_animals_wild = fields.Boolean("Animals – Wild/ Zoo e.g. lion")
    mn_animals_wild_txt = fields.Char("Animals – Wild/ Zoo")
    mn_animals_prehistoric = fields.Boolean("Animals – Prehistoric e.g. dinosaur")
    mn_animals_prehistoric_txt = fields.Char("Animals – Prehistoric")
    mn_insects = fields.Boolean("Insects")
    mn_insects_txt = fields.Char("Insects")
    mn_sea_animals = fields.Boolean("Sea Animals")
    mn_sea_animals_txt = fields.Char("Sea Animals")
    mn_buildings = fields.Boolean("Buildings e.g. house, church")
    mn_buildings_txt = fields.Char("Buildings")
    mn_transportation_cars = fields.Boolean("Transportation – Cars")
    mn_transportation_cars_txt = fields.Char("Transportation – Cars")
    mn_transportation_trucks = fields.Boolean("Transportation – Trucks")
    mn_transportation_trucks_txt = fields.Char("Transportation – Trucks")
    mn_transportation_flight = fields.Boolean("Transportation – Flight vehicles")
    mn_transportation_flight_txt = fields.Char("Transportation – Flight vehicles")
    mn_transportation_nautical = fields.Boolean("Transportation – Nautical e.g. boat")
    mn_transportation_nautical_txt = fields.Char("Transportation – Nautical")
    mn_transportation_others = fields.Boolean("Transportation – Others e.g. train")
    mn_transportation_others_txt = fields.Char("Transportation – Others")
    mn_plants_vegetation = fields.Boolean("Plants and vegetation")
    mn_plants_vegetation_txt = fields.Char("Plants and vegetation")
    mn_fences = fields.Boolean("Fences/ Gates/ Barricades")
    mn_fences_txt = fields.Char("Fences/ Gates/ Barricades")
    mn_brigdes = fields.Boolean("Bridges")
    mn_brigdes_txt = fields.Char("Bridges")
    mn_signs = fields.Boolean("Signs")
    mn_signs_txt = fields.Char("Signs")
    mn_natural = fields.Boolean("Natural – Seashells/ Rocks/ Stones")
    mn_natural_txt = fields.Char("Natural – Seashells/ Rocks/ Stones")
    mn_landscaping = fields.Boolean("Landscaping – Celestial e.g. sky, rain, rainbow")
    mn_landscaping_txt = fields.Char("Landscaping – Celestial")
    mn_landscaping_topo = fields.Boolean("Landscaping – Topographical e.g. mountain, caves")
    mn_landscaping_topo_txt = fields.Char("Landscaping – Topographical")
    mn_household = fields.Boolean("Household – Furniture/ Tools")
    mn_household_txt = fields.Char("Household – Furniture/ Tools")
    mn_other = fields.Boolean("Other")
    mn_other_txt = fields.Char("Other")
    
    # Overall Theme Fields
    
    ovt_revenge = fields.Boolean("Anger / Revenge")
    ovt_abandonment = fields.Boolean("Abandonment")
    ovt_bridging = fields.Boolean("Bridging Opposites")
    ovt_aggression = fields.Boolean("Aggression / Conflict")
    ovt_death = fields.Boolean("Death / Loss / Grieving")
    ovt_empty = fields.Boolean("Empty / Depressed")
    ovt_exploratory = fields.Boolean("Exploratory")
    ovt_good_bad = fields.Boolean("Good vs Bad")
    ovt_helpless = fields.Boolean("Helpless / Inadequate")
    ovt_mastery = fields.Boolean("Mastery")
    ovt_healing = fields.Boolean("Nurturing / Healing")
    ovt_power_control = fields.Boolean("Power & Control")
    ovt_protection = fields.Boolean("Protection")
    ovt_relationships = fields.Boolean("Relationships")
    ovt_reparative = fields.Boolean("Reparative")
    ovt_security = fields.Boolean("Safety / Security")
    ovt_buried = fields.Boolean("Secretive / Buried")
    ovt_sexualized = fields.Boolean("Sexualized")
    ovt_other = fields.Boolean("Other")
    
    # Subject Affect Fields
    
    sa_afraid = fields.Selection([
                ('anxious', 'Anxious'),
                ('distrustful', 'Distrustful'),
                ('fearful', 'Fearful'),
                ('helpless', 'Helpless'),
                ('nervous', 'Nervous'),
                ('scared', 'Scared'),
                ('terrified', 'Terrified'),
                ('vulnerable', 'Vulnerable'),
                ('weak', 'Weak')], string='Affraid')
    sa_sad = fields.Selection([
                ('discouraged', 'Discouraged'),
                ('disappointed', 'Disappointed'),
                ('hopeless', 'Hopeless'),
                ('lonely', 'Lonely'),
                ('pessimistic', 'Pessimistic')], string='Sad')
    sa_angry = fields.Selection([
                ('annoyed', 'Annoyed'),
                ('frustrated', 'Frustrated'),
                ('impatient', 'Impatient'),
                ('irritated', 'Irritated'),
                ('jealous', 'Jealous')], string='Angry')
    sa_happy = fields.Selection([
                ('cheerful', 'Cheerful'),
                ('excited', 'Excited'),
                ('pleased', 'Pleased'),
                ('relieved', 'Relieved'),
                ('satisfied', 'Satisfied')], string='Happy')
    sa_confident = fields.Selection([
                ('authoritative', 'Authoritative'),
                ('brave', 'Brave'),
                ('determined', 'Determined'),
                ('free', 'Free'),
                ('proud', 'Proud'),
                ('optimistic', 'Optimistic'),
                ('powerful', 'Powerful'),
                ('strong', 'Strong')], string='Confident')
    sa_hesitant = fields.Selection([
                ('ashamed', 'Ashamed'),
                ('confused', 'Confused'),
                ('embarrassed', 'Embarrassed'),
                ('inadequate', 'Inadequate'),
                ('mistrust', 'Mistrust'),
                ('nervous', 'Nervous'),
                ('timid', 'Timid'),
                ('uncertain', 'Uncertain')], string='Hesitant')
    sa_curious = fields.Selection([
                ('interested', 'Interested'),
                ('focused', 'Focused')], string='Curious')
    sa_flat = fields.Selection([
                ('ambiguous', 'Ambiguous'),
                ('constricted', 'Constricted'),
                ('dissociative', 'Dissociative'),
                ('restricted', 'Restricted')], string='Flat')

    @api.multi
    def _default_session_get(self):
        return [(0,0,{'activity_low': 'child_act_low', 'activity_high': 'child_act_high'}),
                (0, 0, {'activity_low': 'int_play', 'activity_high': 'int_play'}),
                (0, 0, {'activity_low': 'inclusion_thera', 'activity_high': 'inclusion_thera'}),
                (0, 0, {'activity_low': 'aggressive', 'activity_high': 'constructive'}),
                (0, 0, {'activity_low': 'messy', 'activity_high': 'neat'}),
                (0, 0, {'activity_low': 'dep_therapist', 'activity_high': 'independence'}),
                (0, 0, {'activity_low': 'impulsive', 'activity_high': 'controlled'}),
                (0, 0, {'activity_low': 'inhibited', 'activity_high': 'creative'}),
                (0, 0, {'activity_low': 'immature', 'activity_high': 'age'})]

    # Play Therapy Fields
    
    pt_session_no = fields.Char("Session No")
    pt_date_time = fields.Datetime("Date & Time")
    pt_intial_obs = fields.Text("Initial Observations")
    pt_objective_play_themes = fields.Boolean("Objective Play Themes")
    pt_toys = fields.Boolean("Toys")
    pt_desc_play = fields.Text("Description of Significant Play")
    pt_clinical_imp = fields.Text("Clinical Impression")
    pt_session_dynamics = fields.One2many("pt.session.dynamics","cm_ap_list_id", string="Session Dynamics", default=_default_session_get)
    pt_subjective_affect = fields.Boolean("Subjective Affect")
    
    pt_protect_child = fields.Boolean("Protect Child - Physical & Emotional Safety")
    pt_protect_child_text = fields.Char("Protect Child - Physical & Emotional Safety")
    pt_protect_therapist = fields.Boolean("Protect therapist / Maintain Aceeptance")
    pt_protect_therapist_text = fields.Char("Protect therapist / Maintain Aceeptance")
    pt_protect_toys = fields.Boolean("Protect Toys / Rooms")
    pt_protect_toys_text = fields.Char("Protect Toys / Rooms")
    pt_structuring = fields.Boolean("Structuring e.g Time Limit")
    pt_structuring_text = fields.Char("Structuring e.g Time Limit")
    pt_follow_up = fields.Text("Plan/Recommendation/Follow-up")
    pt_miscellaneous = fields.Binary('Miscellaneous')
    pt_miscellaneous_file_name = fields.Char('File Name')
    
    # PT Objective Play Themes Fields
    
    opt_revenge = fields.Boolean("Anger / Revenge")
    opt_abandonment = fields.Boolean("Abandonment")
    opt_bridging = fields.Boolean("Bridging Opposites")
    opt_aggression = fields.Boolean("Aggression / Conflict")
    opt_death = fields.Boolean("Death / Loss / Grieving")
    opt_empty = fields.Boolean("Empty / Depressed")
    opt_exploratory = fields.Boolean("Exploratory")
    opt_good_bad = fields.Boolean("Good vs Bad")
    opt_helpless = fields.Boolean("Helpless / Inadequate")
    opt_mastery = fields.Boolean("Mastery")
    opt_healing = fields.Boolean("Nurturing / Healing")
    opt_power_control = fields.Boolean("Power & Control")
    opt_protection = fields.Boolean("Protection")
    opt_relationships = fields.Boolean("Relationships")
    opt_reparative = fields.Boolean("Reparative")
    opt_security = fields.Boolean("Safety / Security")
    opt_buried = fields.Boolean("Secretive / Buried")
    opt_sexualized = fields.Boolean("Sexualized")
    
    # PT Toys Fields
    
    toys_animal_domestic = fields.Boolean("Animal (Domestic)")
    toys_animal_domestic_text = fields.Char("Animal (Domestic)")
    toys_animal_scary = fields.Boolean("Animal (Scary)")
    toys_animal_scary_text = fields.Char("Animal (Scary)")
    toys_char_superhero = fields.Boolean("Character (Superhero)")
    toys_char_superhero_text = fields.Char("Character (Superhero)")
    toys_char_scary = fields.Boolean("Character (Scary)")
    toys_char_scary_text = fields.Char("Character (Scary)")
    toys_puppets = fields.Boolean("Puppets")
    toys_puppets_text = fields.Char("Puppets")
    toys_soldiers = fields.Boolean("Soldiers/ War")
    toys_soldiers_text = fields.Char("Soldiers/ War")
    toys_barbie_doll = fields.Boolean("Barbie Doll")
    toys_barbie_doll_text = fields.Char("Barbie Doll")
    toys_art = fields.Boolean("Art & Craft/ Easel")
    toys_art_text = fields.Char("Art & Craft/ Easel")
    toys_ball_games = fields.Boolean("Ball Games")
    toys_ball_games_text = fields.Char("Ball Games")
    toys_bobo_doll = fields.Boolean("Bobo Doll/ Punching Glove")
    toys_bobo_doll_text = fields.Char("Bobo Doll/ Punching Glove")
    toys_blocks = fields.Boolean("Constructive Blocks")
    toys_blocks_text = fields.Char("Constructive Blocks")
    toys_money = fields.Boolean("Cash Register/ Money")
    toys_money_text = fields.Char("Cash Register/ Money")
    toys_transportation = fields.Boolean("Transportation")
    toys_transportation_text = fields.Char("Transportation")
    toys_cleaning = fields.Boolean("Cleaning")
    toys_cleaning_text = fields.Char("Cleaning")
    toys_doctor_kit = fields.Boolean("Doctor's Kit")
    toys_doctor_kit_text = fields.Char("Doctor's Kit")
    toys_doll_house = fields.Boolean("Doll House")
    toys_doll_house_text = fields.Char("Doll House")
    toys_baby_doll = fields.Boolean("Baby Doll/ Child Doll")
    toys_baby_doll_text = fields.Char("Baby Doll/ Child Doll")
    toys_pretend = fields.Boolean("Dressed Up (Pretend)")
    toys_pretend_text = fields.Char("Dressed Up (Pretend)")
    toys_coking = fields.Boolean("Cooking/ Eating")
    toys_coking_text = fields.Char("Cooking/ Eating")
    toys_games = fields.Boolean("Games (Board/Card)")
    toys_games_text = fields.Char("Games (Board/Card)")
    toys_guns = fields.Boolean("Guns/ Handcuffs")
    toys_guns_text = fields.Char("Guns/ Handcuffs")
    toys_sword = fields.Boolean("Sword/ Knife")
    toys_sword_text = fields.Char("Sword/ Knife")
    toys_tools_kit = fields.Boolean("Tools kit")
    toys_tools_kit_text = fields.Char("Tools kit")
    toys_phone = fields.Boolean("Phone")
    toys_phone_text = fields.Char("Phone")
    toys_camera = fields.Boolean("Camera/ Torchlight")
    toys_camera_text = fields.Char("Camera/ Torchlight")
    toys_sandtray = fields.Boolean("Sandtray/ Miniature")
    toys_sandtray_text = fields.Char("Sandtray/ Miniature")
    
    # Subjective Affect Fields
    
    ptsa_afraid = fields.Selection([
                ('anxious', 'Anxious'),
                ('distrustful', 'Distrustful'),
                ('fearful', 'Fearful'),
                ('helpless', 'Helpless'),
                ('nervous', 'Nervous'),
                ('scared', 'Scared'),
                ('terrified', 'Terrified'),
                ('vulnerable', 'Vulnerable'),
                ('weak', 'Weak')], string='Affraid')
    ptsa_sad = fields.Selection([
                ('discouraged', 'Discouraged'),
                ('disappointed', 'Disappointed'),
                ('hopeless', 'Hopeless'),
                ('lonely', 'Lonely'),
                ('pessimistic', 'Pessimistic')], string='Sad')
    ptsa_angry = fields.Selection([
                ('annoyed', 'Annoyed'),
                ('frustrated', 'Frustrated'),
                ('impatient', 'Impatient'),
                ('irritated', 'Irritated'),
                ('jealous', 'Jealous')], string='Angry')
    ptsa_happy = fields.Selection([
                ('cheerful', 'Cheerful'),
                ('excited', 'Excited'),
                ('pleased', 'Pleased'),
                ('relieved', 'Relieved'),
                ('satisfied', 'Satisfied')], string='Happy')
    ptsa_confident = fields.Selection([
                ('authoritative', 'Authoritative'),
                ('brave', 'Brave'),
                ('determined', 'Determined'),
                ('free', 'Free'),
                ('proud', 'Proud'),
                ('optimistic', 'Optimistic'),
                ('powerful', 'Powerful'),
                ('strong', 'Strong')], string='Confident')
    ptsa_hesitant = fields.Selection([
                ('ashamed', 'Ashamed'),
                ('confused', 'Confused'),
                ('embarrassed', 'Embarrassed'),
                ('inadequate', 'Inadequate'),
                ('mistrust', 'Mistrust'),
                ('nervous', 'Nervous'),
                ('timid', 'Timid'),
                ('uncertain', 'Uncertain')], string='Hesitant')
    ptsa_curious = fields.Selection([
                ('interested', 'Interested'),
                ('focused', 'Focused')], string='Curious')
    ptsa_flat = fields.Selection([
                ('ambiguous', 'Ambiguous'),
                ('constricted', 'Constricted'),
                ('dissociative', 'Dissociative'),
                ('restricted', 'Restricted')], string='Flat')
    
    # Art Psychotherapy Fields
    
    ap_session_no = fields.Char("Session No")
    ap_date_time = fields.Datetime("Date & Time")
    ap_medium = fields.Char("Medium(s)")
    ap_artworks = fields.Char("Artworks")
    ap_themes = fields.Char("Theme(s)")
    ap_process = fields.Text("Process (S.O.A.P)")
    ap_follow_up = fields.Text("Follow-Up")
    ap_affect_behaviour = fields.Boolean("Affect/Behaviour")
    ap_miscellaneous = fields.Binary('Miscellaneous')
    ap_miscellaneous_file_name = fields.Char('File Name')
    
    # AP Affective Behaviour Fields
    
    apab_afraid = fields.Selection([
                ('anxious', 'Anxious'),
                ('distrustful', 'Distrustful'),
                ('fearful', 'Fearful'),
                ('helpless', 'Helpless'),
                ('nervous', 'Nervous'),
                ('scared', 'Scared'),
                ('terrified', 'Terrified'),
                ('vulnerable', 'Vulnerable'),
                ('weak', 'Weak')], string='Affraid')
    apab_sad = fields.Selection([
                ('discouraged', 'Discouraged'),
                ('disappointed', 'Disappointed'),
                ('hopeless', 'Hopeless'),
                ('lonely', 'Lonely'),
                ('pessimistic', 'Pessimistic')], string='Sad')
    apab_angry = fields.Selection([
                ('annoyed', 'Annoyed'),
                ('frustrated', 'Frustrated'),
                ('impatient', 'Impatient'),
                ('irritated', 'Irritated'),
                ('jealous', 'Jealous')], string='Angry')
    apab_happy = fields.Selection([
                ('cheerful', 'Cheerful'),
                ('excited', 'Excited'),
                ('pleased', 'Pleased'),
                ('relieved', 'Relieved'),
                ('satisfied', 'Satisfied')], string='Happy')
    apab_confident = fields.Selection([
                ('authoritative', 'Authoritative'),
                ('brave', 'Brave'),
                ('determined', 'Determined'),
                ('free', 'Free'),
                ('proud', 'Proud'),
                ('optimistic', 'Optimistic'),
                ('powerful', 'Powerful'),
                ('strong', 'Strong')], string='Confident')
    apab_hesitant = fields.Selection([
                ('ashamed', 'Ashamed'),
                ('confused', 'Confused'),
                ('embarrassed', 'Embarrassed'),
                ('inadequate', 'Inadequate'),
                ('mistrust', 'Mistrust'),
                ('nervous', 'Nervous'),
                ('timid', 'Timid'),
                ('uncertain', 'Uncertain')], string='Hesitant')
    apab_curious = fields.Selection([
                ('interested', 'Interested'),
                ('focused', 'Focused')], string='Curious')
    apab_flat = fields.Selection([
                ('ambiguous', 'Ambiguous'),
                ('constricted', 'Constricted'),
                ('dissociative', 'Dissociative'),
                ('restricted', 'Restricted')], string='Flat')
    
    # Behaviour Therapy Fields
    
    bt_date_time = fields.Datetime("Date & Time")
    bt_session = fields.Char("Session")
    bt_comments = fields.Text("Comments")
    bt_programme = fields.Boolean("Programme")

    # BT Programme Fields
    
    btp_programme = fields.Char("Programme 1")
    btp_programme1 = fields.Char("Programme 2")
    btp_programme2 = fields.Char("Programme 3")
    btp_programme3 = fields.Char("Programme 4")
    btp_programme4 = fields.Char("Programme 5")

    btp_data = fields.Binary("Data")
    btp_remarks = fields.Char("Remarks 1")
    btp_remarks1 = fields.Char("Remarks 2")
    btp_remarks2 = fields.Char("Remarks 3")
    btp_remarks3 = fields.Char("Remarks 4")
    btp_remarks4 = fields.Char("Remarks 5")

    btp_miscellaneous = fields.Binary('Miscellaneous')
    btp_miscellaneous_file_name = fields.Char('File Name')
    btp_percentage = fields.Float("Percentage (%) 1")
    btp_percentage1 = fields.Float("Percentage (%) 2")
    btp_percentage2 = fields.Float("Percentage (%) 3")
    btp_percentage3 = fields.Float("Percentage (%) 4")
    btp_percentage4 = fields.Float("Percentage (%) 5")
    
class PTSessionDynamics(models.Model):
    _name = "pt.session.dynamics"
    
    @api.onchange('activity_low')
    def activity_low_onchange(self):
        if self.activity_low == 'child_act_low':
            self.activity_high = 'child_act_high'
        if self.activity_low == 'int_play':
            self.activity_high = 'int_play'
        if self.activity_low == 'inclusion_thera':
            self.activity_high = 'inclusion_thera'
        if self.activity_low == 'aggressive':
            self.activity_high = 'constructive'
        if self.activity_low == 'messy':
            self.activity_high = 'neat'
        if self.activity_low == 'dep_therapist':
            self.activity_high = 'independence'
        if self.activity_low == 'impulsive':
            self.activity_high = 'controlled'
        if self.activity_low == 'inhibited':
            self.activity_high = 'creative'
        if self.activity_low == 'immature':
            self.activity_high = 'age'
     
    cm_ap_list_id = fields.Many2one("cm.ap.list", string="AP List")
    activity_low = fields.Selection([
                ('child_act_low', "Child's Activity Level(Low)"),
                ('int_play', 'Intensity of Play (Low)'),
                ('inclusion_thera', 'Inclusion of Therapist (Low)'),
                ('aggressive', 'Aggressive/Destructive'),
                ('messy', 'Messy/Chaotic/Disorganized'),
                ('dep_therapist', 'Dependence on Therapist'),
                ('impulsive', 'Impulsive'),
                ('inhibited', 'Inhibited'),
                ('immature', 'Immature/Regressive')], string='Activity')
    prio_1 = fields.Selection([
                ('1', '1')], string='L1')
    prio_2 = fields.Selection([
                ('2', '2')], string='L2')
    prio_3 = fields.Selection([
                ('3', '3')], string='L3')
    prio_4 = fields.Selection([
                ('4', '4')], string='L4')
    prio_5 = fields.Selection([
                ('5', '5')], string='L5')
    no = fields.Selection([
                ('no', 'No')], string='No')
    activity_high = fields.Selection([
                ('child_act_high', "Child's Activity Level(High)"),
                ('int_play', 'Intensity of Play (High)'),
                ('inclusion_thera', 'Inclusion of Therapist (High)'),
                ('constructive', 'Constructive'),
                ('neat', 'Neat/Orderly'),
                ('independence', 'Independence/Autonomous'),
                ('controlled', 'Controlled'),
                ('creative', 'Creative/Spontaneous/Free/Expressive'),
                ('age', 'Age-appropriate')], string='Activity')

        
