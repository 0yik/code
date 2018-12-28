# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
from datetime import datetime, date
from openerp.exceptions import UserError, ValidationError

mapping = ['sys_process','follow_instr','flexible','plan','job_knowledge','skill','learn_skill','accuracy','reliability','cust_sati','work_comple','pressure','handling','relationship','prob_solv','dec_mak','time_mng','express','share_know',
              'seeks','open_ideas','enthu','trust','ettiquttes','punctuality','descipline','attendance','team_work','team_build','strategy', 'participation']
mapping_avg = ['sys_process','follow_instr','flexible','plan','job_knowledge','skill','learn_skill','accuracy','reliability','cust_sati','work_comple','pressure','handling']


class hr_job(models.Model):
    _inherit = 'hr.job'

    kra_id = fields.Many2one('hr.kra', 'KRA')


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def _kra_count(self):
        for rec in self:
            kras = self.env['employee.kra'].search([('employee_id', '=', rec.id)])
            rec.kra_count = len(kras)

    @api.multi
    def _value_rating_count(self):
        for rec in self:
            print "hooooo"
            value_ratings = self.env['value.rating'].search([('employee_id', '=', rec.id)])
            rec.value_rating_count = len(value_ratings)

    kra_id = fields.Many2one('hr.kra', related='job_id.kra_id', string="KRA", readonly=True)
    employee_code = fields.Integer('Employee Code')
    kra_count = fields.Integer(compute='_kra_count', string="KRA")
    value_rating_count = fields.Integer(compute='_value_rating_count', string="Value Ratings")

    @api.multi
    def action_kra_tree_view(self):
        return {
            'name': 'Employee KRA',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'employee.kra',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('employee_id', 'in', self.ids)],
        }

    @api.multi
    def action_value_rating_tree_view(self):
        return {
            'name': 'Employee Value Rating',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'value.rating',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('employee_id', 'in', self.ids)],
        }

class employee_kra(models.Model):
    _name = 'employee.kra'
    _inherit = ['mail.thread']
    _rec_name = 'employee_id'

    @api.model
    def _get_default_employee(self):
        employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
        if employee:
            return employee[0].id
        else:
            raise Warning("There is no any employee assigned with logged user")

    name = fields.Selection([(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), (9, 'September'), (10, 'october'), (11, 'November'), (12, 'December') ], "KRA Month", required=True)
    quarterly = fields.Selection([(1, 'First Quarter'), (2, 'Second Quarter'), (3, 'Third Quarter'), (4, 'Fourth Quarter')], "KRA Quarter")
    year = fields.Many2one('hr.year', 'Year', required=True)
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True, default=_get_default_employee)
    kra_id = fields.Many2one('hr.kra', string="KRA")
    kra_question_ids = fields.One2many('employee.kra.question', 'employee_kra_id', 'Self Question')
    kra_question_ids2 = fields.One2many('employee.kra.question', 'employee_kra_id2', 'Manager to Employee Question')
    kra_question_ids3 = fields.One2many('employee.kra.question', 'employee_kra_id3', 'Employee to Manager Question')
    kra_question_ids4 = fields.One2many('employee.kra.question', 'employee_kra_id4', 'Manager Self Question')
    kra_question_ids5 = fields.One2many('employee.kra.question', 'employee_kra_id5', 'Employee to Subordinates Question')
    kra_question_ids6 = fields.One2many('employee.kra.question', 'employee_kra_id6', 'Subordinates Self Question')
    kra_question_ids7 = fields.One2many('employee.kra.question', 'employee_kra_id7', 'Employee to Colleagues Question')
    kra_question_ids8 = fields.One2many('employee.kra.question', 'employee_kra_id8', 'Colleagues Self Question')
    date = fields.Date("Date", default=fields.Date.today)
    state = fields.Selection([('draft', 'Draft'), ('submit', 'Submited To Supervisor'), ('cancel', 'Cancelled'), ('done', 'Done'), ], "State", track_visibility='onchange', default='draft')
    evaluation_type = fields.Selection([('self', 'Self Evaluation'),
                                       ('manager', 'Manager Evaluation'),
                                       ('subordinate', 'Subordinates Evaluation'),
                                       ('colleagues', 'Colleagues Evaluation')], default='self', string="Evaluation Type" , required=True)
    manager_id = fields.Many2one('hr.employee', string="Manager")
    subordinate_id = fields.Many2one('hr.employee', string="Subordinate")
    colleagues_id = fields.Many2one('hr.employee', string="Colleagues")
    department_id = fields.Many2one('hr.department', related="employee_id.department_id", string="Department")

    @api.model
    def create(self, vals):
        res = super(employee_kra, self).create(vals)
        if res.evaluation_type =='self':
            res.kra_id = res.employee_id.job_id.kra_id.id
        elif res.evaluation_type =='manager':
            res.kra_id = res.manager_id.job_id.kra_id.id
        elif res.evaluation_type =='subordinate':
            res.kra_id = res.subordinate_id.job_id.kra_id.id
        else:
            res.kra_id = res.colleagues_id.job_id.kra_id.id
        return res

    @api.multi
    def write(self, vals):
        for res in self:
            employee = False
            if vals.get('employee_id', False):
                employee = vals.get('employee_id') or res.employee_id.id
            elif vals.get('manager_id', False):
                employee = vals.get('manager_id') or res.manager_id.id
            elif vals.get('subordinate_id'):
                employee = vals.get('subordinate_id') or res.subordinate_id.id
            elif vals.get('colleagues_id'):
                employee = vals.get('colleagues_id') or res.colleagues_id.id
            if employee:
                vals['kra_id'] = self.env['hr.employee'].browse(employee).job_id.kra_id.id
        return super(employee_kra, self).write(vals)

    @api.multi
    def action_submit(self):
        self.state = 'submit'
        kra_ques_obj = self.env['employee.kra.question']
        if self.evaluation_type =='self':
            kra_question_ids = self.kra_question_ids
        elif self.evaluation_type =='manager':
            kra_question_ids = self.kra_question_ids3
        elif self.evaluation_type =='subordinate':
            kra_question_ids = self.kra_question_ids5
        else:
            kra_question_ids = self.kra_question_ids7
        for question in kra_question_ids:
            vals= {
                'name':question.name,
                'description':question.name,
                'hint':question.hint,
                'weightage':question.weightage,
                'employee_rating':question.employee_rating,
                'employee_remark':question.employee_remark,
                'manager_remark':question.manager_remark,
                'manager_rating':question.manager_rating,
                'final_score':question.final_score,
                'employee_id':question.employee_id.id,
            }
            if self.evaluation_type =='self':
                vals['employee_kra_id2'] = question.employee_kra_id.id
            elif self.evaluation_type =='manager':
                vals['employee_kra_id4'] = question.employee_kra_id3.id
            elif self.evaluation_type =='subordinate':
                vals['employee_kra_id6'] = question.employee_kra_id5.id
            else:
                vals['employee_kra_id8'] = question.employee_kra_id7.id
            kra_ques_obj.create(vals)

    @api.multi
    def action_cancel(self):
        self.state = 'cancel'

    @api.multi
    def action_done(self):
        self.state = 'done'

    @api.onchange('employee_id', 'manager_id', 'subordinate_id', 'colleagues_id', 'evaluation_type')
    def onchange_employee(self):
        data = []
        self.department_id = self.employee_id.department_id.id
        if self.evaluation_type=='self':
            employee = self.employee_id
        elif self.evaluation_type=='manager':
            employee = self.manager_id
        elif self.evaluation_type=='subordinate':
            employee = self.subordinate_id
        else:
            employee = self.colleagues_id
        for que in employee.job_id.kra_id.kra_question_ids:
            data.append((0,0,{
                'employee_id': self.employee_id.id,
                'name': que.name,
                'description': que.description,
                'weightage': que.weightage,
                'kra_question_id': que.id, 
                #'employee_kra_id': self.id,
                'sequence': que.sequence,
                'hint': que.hint}))
        if self.evaluation_type=='self':
            self.kra_question_ids = data
        elif self.evaluation_type=='manager':
            self.kra_question_ids3 = data
        elif self.evaluation_type=='subordinate':
            self.kra_question_ids5 = data
        else:
            self.kra_question_ids7 = data
        self.kra_id = employee.job_id.kra_id.id

class employee_kra_question(models.Model):
    _name = 'employee.kra.question'
    _order = 'sequence'

    @api.multi
    @api.depends('manager_rating')
    def _compute_total(self):
        for que in self:
            que.final_score = (que.weightage * que.manager_rating) / 10

    @api.multi
    def _check_max_limit(self):
        for que in self:
             if (que.employee_rating < 0.0 or que.employee_rating > 10.0):
                 return False
             if (que.manager_rating < 0.0 or que.manager_rating > 10.0):
                 return False
        return True

    name = fields.Char('Question')
    sequence = fields.Integer('Sr.No')
    description = fields.Text('Description')
    hint = fields.Char('Hint')
    employee_kra_id = fields.Many2one('employee.kra', 'KRA', ondelete='cascade')
    employee_kra_id2 = fields.Many2one('employee.kra', 'KRA', ondelete='cascade')
    employee_kra_id3 = fields.Many2one('employee.kra', 'KRA', ondelete='cascade')
    employee_kra_id4 = fields.Many2one('employee.kra', 'KRA', ondelete='cascade')
    employee_kra_id5 = fields.Many2one('employee.kra', 'KRA', ondelete='cascade')
    employee_kra_id6 = fields.Many2one('employee.kra', 'KRA', ondelete='cascade')
    employee_kra_id7 = fields.Many2one('employee.kra', 'KRA', ondelete='cascade')
    employee_kra_id8 = fields.Many2one('employee.kra', 'KRA', ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string="Employee")
    kra_question_id = fields.Many2one('kra.question', 'KRA Question')
    employee_remark = fields.Char('Employee Remark')
    manager_remark = fields.Char('Manager Remark')
    employee_rating = fields.Float('Employee Rating')
    manager_rating = fields.Float('Manager Rating')
    weightage = fields.Integer('Weightage')
    final_score = fields.Float(compute='_compute_total', string='Final Score', store=True,readonly='1')

    _constraints = [
        (_check_max_limit, 'Rating in between 0-10 only', ['employee_rating', 'manager_rating'])
    ]

class hr_kra(models.Model):
    _name = 'hr.kra'
    _inherit = ['mail.thread']

    @api.multi
    def _check_allocation(self):
        total = 0.0
        for percentage in self:
            for amount in percentage.kra_question_ids:
                total += amount.weightage
            if total == 100 or total == 0:
                return True
        return False

    name = fields.Char('Name', required=True)
    kra_question_ids = fields.One2many('kra.question', 'kra_id', 'KRA Question')

    _constraints = [
        (_check_allocation, 'Warning!| The total Weightage distribution should be 100%.', ['kra_question_ids']), 
    ]

class kra_question(models.Model):
    _name = 'kra.question'
    _order = 'sequence'

    sequence = fields.Integer('Sr.No')
    kra_id = fields.Many2one('hr.kra', 'KRA', ondelete='cascade')
    name = fields.Char('Question')
    description = fields.Text('Description')
    hint = fields.Char('Hint')
    weightage = fields.Integer('Weightage')
    

class value_rating(models.Model):
    _name = 'value.rating'
    _inherit = ['mail.thread']
    _rec_name = 'employee_id'

    @api.multi
    def _check_max_limit(self):
        for values in self:
            for val in mapping:
                if (values[val] < 0.0 or values[val] > 5.0):
                 return False
        return True

    @api.multi
    def calculate_avg(self):
        res = 0.0
        for rec in self:
            total = 0.0
            for val in mapping_avg:
                total += rec[val]
            rec.score_leader =  round((total /len(mapping_avg)), 2)

    @api.multi
    def total_average(self):
        for rec in self:
            total = 0.0
            for val in mapping:
                total += rec[val]
            rec.total_avg =  round((total /len(mapping)), 2)

    employee_id = fields.Many2one('hr.employee', 'Employee Name', required=True)
    employee_code = fields.Integer(related='employee_id.employee_code', string="Employee Code" ,readonly=True)
    month = fields.Selection([(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'), (6, 'June'),
                              (7, 'July'), (8, 'August'), (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')], 'Month', required=True)
    year = fields.Many2one('hr.year', 'Year', required=True)
    designation = fields.Many2one('hr.job', related='employee_id.job_id', string='Designation', readonly=True)
    appraiser_id = fields.Many2one('hr.employee', related='employee_id.parent_id', string="Appraiser", store=True, readonly=True)
    sys_process = fields.Float('System and Processes')
    follow_instr = fields.Float('Follow Instructions')
    flexible = fields.Float('Adaptable and Flexible')
    plan = fields.Float('Ability To Plan')
    job_knowledge = fields.Float('Job Knowledge')
    skill = fields.Float('Skill To Handle Work')
    learn_skill = fields.Float('Learn New Skill')
    accuracy = fields.Float('Accuracy')
    reliability = fields.Float('Reliability')
    cust_sati = fields.Float('Client Satisfaction')
    work_comple = fields.Float('Work Completion On Time')
    pressure = fields.Float('Ability to work under pressure')
    handling = fields.Float('Handling new portfolio')
    score_leader = fields.Float(compute="calculate_avg" , string='Leadership Score', readonly='1',
        help="This shows avg value for fields of foru sections: Approach To Work, Technical Skills, Quality Of work, Handling Targets")
    relationship = fields.Float('Relationship with co-workers')
    prob_solv = fields.Float('Problem solving')
    dec_mak = fields.Float('Decision making')
    time_mng = fields.Float('Time management')
    express = fields.Float('Oral and written expression')
    share_know = fields.Float('Sharing of knowledge')
    seeks = fields.Float('Seeks T & D')
    open_ideas = fields.Float('Open to ideas')
    enthu = fields.Float('Enthusiastic')
    trust = fields.Float('Trustworthy')
    ettiquttes = fields.Float('Work Place ettiquttes')
    punctuality = fields.Float('Punctuality')
    descipline = fields.Float('Descipline')
    attendance = fields.Float('Attendance')
    team_work = fields.Float('Team work')
    team_build = fields.Float('Team Building')
    strategy = fields.Float('New Strategy and direction')
    participation = fields.Float('Participation in HR activities')
    total_avg = fields.Float(compute='total_average' , string='Total average', readonly='1')
    state = fields.Selection([('draft', 'Draft'), ('cancel', 'Cancelled'), ('done', 'Done'), ], "State" ,track_visibility='onchange',default='draft')

    _constraints = [
        (_check_max_limit, 'Value Rating in between 0-5 only', ['sys_process','follow_instr','flexible','plan','job_knowledge','skill','learn_skill','accuracy','reliability','cust_sati','work_comple','pressure','handling','relationship','prob_solv','dec_mak','time_mng','express','share_know',
                                                                'seeks','open_ideas','enthu','trust','ettiquttes','punctuality','descipline','attendance','team_work','team_build','strategy', 'participation']),
    ]

    @api.multi
    def action_submit(self):
        self.state = 'submit'

    @api.multi
    def action_cancel(self):
        self.state = 'cancel'

    @api.multi
    def action_done(self):
        self.state = 'done'


class employee_year(models.Model):
    _name = 'employee.year'

    name = fields.Char('Year', size=4)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
