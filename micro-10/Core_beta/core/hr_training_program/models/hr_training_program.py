# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools
from odoo import tools, _
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import ValidationError



class TrainingPrograms(models.Model):
    _name = "training.programs"
    _description = "Training Programs"

    @api.multi
    def _get_count(self):
        for obj in self:
            obj.conduct_count = len(self.env['training.conducts'].search(
                [('program_id', '=', obj.id)]).ids)

    name = fields.Char('Name', required=True)
    description = fields.Text('Description')
    conducted_at = fields.Char('Conducted at')
    renewable = fields.Integer('Renewable every')
    bond = fields.Integer('Bond')
    conduct_count = fields.Integer(
        string='Training Conduct',
        help='Training Conduct Count', compute='_get_count', )

    @api.multi
    def action_view_training_conduct(self):
        """docstring for action_view_conduct"""
        conduct_ids = self.env['training.conducts'].search(
                [('program_id', '=', self.id)])
        action = self.env.ref('hr_training_program.open_hr_training_conducts').read()[0]
        if len(conduct_ids.ids) > 1:
            action['domain'] = [('id', 'in', conduct_ids.ids)]
        elif len(conduct_ids.ids) == 1:
            action['views'] = [(self.env.ref('hr_training_program.view_training_conducts_form').id, 'form')]
            action['res_id'] = conduct_ids.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action


TrainingPrograms()


class TrainingConducts(models.Model):
    _name = 'training.conducts'
    _description = 'Training Conducts'


    name = fields.Char('Name')
    program_id = fields.Many2one('training.programs', string="Program", required=True)
    status = fields.Selection([
        ('pending', 'Pending'),
        ('progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='pending')
    date_start = fields.Date('Date Start', default=date.today().strftime('%Y-%m-%d'))
    date_completed = fields.Date('Date Completed', required=False)
    list_conduct_ids = fields.One2many('list.conducts', 'training_id', string="Training Conducts")
    venue = fields.Text('Venue',required=True)
    @api.model
    def create(self, vals):
        training_id = self.env['list.conducts']

        name = vals['name']
        training_program = vals['program_id']
        date_attempted = vals['date_start']
        date_completed = vals['date_completed']
        status = vals['status']

        training_program_id = self.env['training.programs'].browse(training_program)
        renew = training_program_id.renewable
        date_expire = False
        if date_completed:
            date_expire = (datetime.strptime(date_completed, DEFAULT_SERVER_DATE_FORMAT) + relativedelta(months=renew)).strftime(DEFAULT_SERVER_DATE_FORMAT)

        trainings_id = super(TrainingConducts, self).create(vals)
        if date_completed:
            self._cr.execute("update list_conducts set name=%s , program_id=%s, date_start=%s, date_completed=%s, date_expire=%s, status=%s where training_id=%s ",(name,training_program,date_attempted,date_completed,date_expire,status,trainings_id.id))
        else:
            self._cr.execute("update list_conducts set name=%s , program_id=%s, date_start=%s, status=%s where training_id=%s ", (name, training_program, date_attempted, status, trainings_id.id))
        return trainings_id


    @api.multi
    def write(self, vals):

        training_id = super(TrainingConducts, self).write(vals)
        data_record = self.search([('id','=', self.ids[0])])
        training_program_id= self.env['training.programs'].browse(data_record.program_id.id)
        if 'name' in vals:
              self._cr.execute("update list_conducts set name=%s where training_id=%s ",(vals['name'],self.ids[0]))
        if 'status' in vals:
            if vals['status']== 'completed':
                if not self.date_completed or vals.get('date_completed',False):
                    raise ValidationError(_('Please enter Date Completed'))
                for record_id in self.env['list.conducts'].search([('training_id','=', self.ids[0])]):
                    status_list= record_id.status_list
                    if status_list=='pending':
                        raise ValidationError(_('Please update all the status for all employees'))
            self._cr.execute("update list_conducts set status=%s where training_id=%s ",(vals['status'],self.ids[0]))
        if 'date_start' in vals:
              self._cr.execute("update list_conducts set date_start=%s where training_id=%s ",(vals['date_start'],self.ids[0]))

        if 'program_id' in vals:
            renew = training_program_id.renewable
            if data_record.date_completed:
                date_expire = (datetime.strptime(data_record.date_completed, DEFAULT_SERVER_DATE_FORMAT) + relativedelta(months=renew)).strftime(DEFAULT_SERVER_DATE_FORMAT)
                self._cr.execute("update list_conducts set program_id=%s, date_expire=%s where training_id=%s ",(vals['program_id'],date_expire,self.ids[0]))
            else:
                self._cr.execute("update list_conducts set program_id=%s where training_id=%s ", (vals['program_id'], self.ids[0]))

        if 'date_completed' in vals and vals.get('date_completed',False):
            renew = training_program_id.renewable
            date_expire = (datetime.strptime(vals['date_completed'], DEFAULT_SERVER_DATE_FORMAT) + relativedelta(months=renew)).strftime(DEFAULT_SERVER_DATE_FORMAT)
            self._cr.execute("update list_conducts set date_completed=%s, date_expire=%s where training_id=%s ",(vals['date_completed'],date_expire,self.ids[0]))
        else:
            data_record = self.search([('id','=', self.ids[0])])
            renew = training_program_id.renewable
            if data_record.date_completed:
                date_expire = (datetime.strptime(data_record.date_completed, DEFAULT_SERVER_DATE_FORMAT) + relativedelta(months=renew)).strftime(DEFAULT_SERVER_DATE_FORMAT)
                self._cr.execute("update list_conducts set name=%s , program_id=%s, date_start=%s, date_completed=%s, date_expire=%s, status=%s where training_id=%s ",(data_record.name,data_record.program_id.id,data_record.date_start,data_record.date_completed,date_expire, data_record.status,data_record.id))
            else:
                self._cr.execute("update list_conducts set name=%s , program_id=%s, date_start=%s, status=%s where training_id=%s ", (data_record.name, data_record.program_id.id, data_record.date_start, data_record.status, data_record.id))
        print "=======status========",vals
        if vals.get('status', False):
            if vals['status']=='completed':
                for line in self.list_conduct_ids:
                    if self.date_completed:
                        date_completed = datetime.strptime(self.date_completed, DEFAULT_SERVER_DATE_FORMAT)
                        expiry_date = date_completed + relativedelta(months=self.program_id.bond)
                        values = {
                                'employee_id':line.employee_id.id,
                                'program_id':self.program_id.id,
                                'training_id':self.id,
                                'date_complete':self.date_completed,
                                'attachment':line.attachment,
                                'expiry_date':expiry_date,
                        }
                        res = self.env['employee.bond'].create(values)
            if vals['status']=='cancelled':
                for line in self.list_conduct_ids:
                    line.status_list = 'pending'
        return training_id

    @api.onchange('program_id')
    def onchange_program_id(self):
        self.venue = self.program_id.conducted_at

class ListConducts(models.Model):
    _name = "list.conducts"
    _description = "List Conducts"
    _rec_name = "program_id"

    employee_id = fields.Many2one('hr.employee', string="Employee")
    training_id = fields.Many2one('training.conducts', "Training")
    attended = fields.Boolean('Attended')
    absent = fields.Boolean('Absent')
    remarks = fields.Text('Remarks')
    attachment = fields.Binary('Attachment')
    name = fields.Char('Name')
    program_id = fields.Many2one('training.programs', string="Program")
    date_start = fields.Date('Date Start', default=date.today().strftime('%Y-%m-%d'))
    date_completed = fields.Date('Date Completed')
    date_expire = fields.Date('Expire Date')
    status = fields.Selection([
        ('pending', 'Pending'),
        ('progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status')
    status_list = fields.Selection([
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ], string='Status', default= 'pending')

    emp_job_name = fields.Char(string="Job Position", compute="_get_details", store=True)
    emp_dept_name = fields.Char(string="Department", compute="_get_details", store=True)

    @api.depends('employee_id')
    def _get_details(self):
        for rec in self:
            rec.emp_job_name = rec.employee_id.job_id.name
            rec.emp_dept_name = rec.employee_id.department_id.name



    @api.multi
    def tick(self):
        if not self.attachment:
            raise ValidationError(_('You need to upload attachment to be certified'))
        if not self.attended:
            raise ValidationError(_('User must "attend" the training conduct in order to be success'))
        return self.write({'status_list': 'success'})

    @api.multi
    def cross(self):
        return self.write({'status_list': 'failed'})

    @api.onchange('attended')
    def onchange_attended(self):
        if self.attended:
            self.absent = False

    @api.onchange('absent')
    def onchange_absent(self):
        if self.absent:
            self.attended = False

class Employee(models.Model):
    _inherit = 'hr.employee'

    employee_training_ids = fields.One2many('list.conducts', 'employee_id', string="Employee Trainings")
    employee_bond_ids = fields.One2many('employee.bond', 'employee_id', string="Employee Bonds")

class EmployeeBonds(models.Model):
    _name = 'employee.bond'
    _description = 'Employee Bond'

    employee_id = fields.Many2one('hr.employee', string="Employee")
    program_id = fields.Many2one('training.programs', string="Program")
    training_id = fields.Many2one('training.conducts', "Training Conduct")
    date_complete = fields.Date('Complete Date')
    attachment = fields.Binary('Attachment')
    expiry_date = fields.Date('Expiry Date')

class TrainingRequests(models.Model):
    _name = 'training.requests'
    _description = 'Training Requests'

    employee = fields.Many2one('hr.employee', 'Employee')
    trainingprogram = fields.Many2one('training.programs', 'Training Program')
    job_position = fields.Many2one('hr.job', 'Job Position')
    remarks = fields.Text('Remarks')
    state = fields.Selection([
        ('pending', 'Pending'),
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', default='pending')


    @api.multi
    def action_request(self):
        # context = dict(self.env.context or {})
        # view_id = self.env.ref('hr.view_hr_job_form').id
        self.write({'state': 'requested'})
        # return   {
        #             'name': _('Job Candidates'),
        #             'res_model':'hr.job',
        #             'model': 'ir.actions.act_window',
        #             'type':'ir.actions.act_window',
        #             'view_type':'form',
        #             'view_id': view_id,
        #             'view_mode':'form',
        #             'create': False,
        #             'context': context,
        #             'res_id': self.job_position.id,
        #             'target': 'new',
        #             }


    @api.multi
    def action_approved(self):
        context = dict(self.env.context or {})
        view_id = self.env.ref('hr_training_program.training_requests_wizard_form_view').id
        # self.write({'state': 'approved'})
        return {
            'name': _('Training Conducts'),
            'res_model': 'training.requests.wizard',
            'model': 'ir.actions.act_window',
            'type':'ir.actions.act_window',
            'view_type': 'form',
            'view_id': view_id,
            'view_mode':'form',
            'edit': True,
            'context': context,
            'res_id': self.env.context.get('employee') and self.ids[0],
            'target': 'new',
        }

    @api.multi
    def action_rejected(self):
        return self.write({'state': 'rejected'})


class Job(models.Model):
    _inherit = 'hr.job'

    training_required_ids = fields.Many2many('training.programs', 'program_trainings_rel','training_program_id','job_id', 'Trainings Required')
    candidates_training_ids = fields.One2many('candidates.training', 'job_training', 'Candidates' )

class CandidatesTraining(models.Model):
    _name = 'candidates.training'
    _description = 'Candidates Trainings List'

    employee = fields.Many2one('hr.employee','Employee')
    trainings_completed_ids = fields.Many2many('training.programs', 'candidate_training_completed_rel', 'candidate_id', 'program_id', string='Trainings Completed', compute='_compute_training_programs')
    trainings_todo_ids = fields.Many2many('training.programs', 'candidate_training_todo_rel', 'candidate_id', 'program_id', string='Trainings to do', compute='_compute_training_programs')
    job_training = fields.Many2one('hr.job','Training Candidates')

    @api.depends('employee', 'job_training')
    def _compute_training_programs(self):
        for record in self:
            if record.job_training and record.job_training.id:
                trainings_todo_ids      = record.trainings_todo_ids.browse([])
                trainings_completed_ids = record.trainings_completed_ids.browse([])
                now = datetime.now()
                # Calculate completed
                if record.employee and record.employee.id:
                    conducts = self.env['training.conducts'].search([
                        ('status', '=', 'completed'),
                        ('list_conduct_ids.employee_id', '=', record.employee.id),
                    ])
                    for conduct in conducts:
                        check = True
                        if conduct.program_id and conduct.program_id.id :
                            list_conduct_ids = conduct.list_conduct_ids
                            for list_conduct_id in list_conduct_ids:
                                if list_conduct_id.date_expire != False:
                                    if datetime.strptime(list_conduct_id.date_expire,'%Y-%m-%d') < now or list_conduct_id.status_list != 'success':
                                        check = False
                                        break
                            if check is True:
                                trainings_completed_ids += conduct.program_id

                # Calculate todo course
                for program in record.job_training.training_required_ids:
                    if program.id not in trainings_completed_ids.ids:
                        trainings_todo_ids += program

                record.trainings_todo_ids      = trainings_todo_ids
                record.trainings_completed_ids = trainings_completed_ids

    @api.onchange('employee')
    def _onchange_employee(self):

            trainings_todo_ids = self.trainings_todo_ids.browse([])
            trainings_completed_ids = self.trainings_completed_ids.browse([])
            now = datetime.now()

            # Calculate completed
            if self.employee and self.employee.id:
                conducts = self.env['training.conducts'].search([
                    ('status', '=', 'completed'),
                    ('list_conduct_ids.employee_id', '=', self.employee.id),
                ])
                for conduct in conducts:
                    check = True
                    if conduct.program_id and conduct.program_id.id:
                        list_conduct_ids = conduct.list_conduct_ids
                        for list_conduct_id in list_conduct_ids:
                            if list_conduct_id.date_expire != False:
                                if datetime.strptime(list_conduct_id.date_expire,
                                                     '%Y-%m-%d') < now or list_conduct_id.status_list != 'success':
                                    check = False
                                    break
                        if check is True:
                            trainings_completed_ids += conduct.program_id
            # Calculate todo course
            for program in self.job_training.training_required_ids:
                if program.id not in trainings_completed_ids.ids:
                    trainings_todo_ids += program

            self.trainings_todo_ids = trainings_todo_ids
            self.trainings_completed_ids = trainings_completed_ids


class TrainingProgress(models.Model):
    _name = 'training.progress'

    name = fields.Char(string='Name')
    training_progress_line = fields.One2many('training.progress.line', 'training_progress_id',
                            string="Training Progress Line", copy=True)
    employee_ids = fields.One2many('hr.employee', 'training_progress_id', 
        string="Employee", copy=True)
    job_position = fields.Char(string="JOb Position")
    department = fields.Char(string="Department")


class TrainingProgress(models.Model):
    _name = 'training.progress.report'
    _inherit = 'hr.employee'

    name = fields.Char(string='Name')
    training_progress_name = fields.Char(string="Training Name")
    employee_name = fields.Char(string="Employee", copy=True)
    job_position = fields.Char(string="JOb Position")
    department = fields.Char(string="Department")


class TrainingProgress(models.Model):
    _name = 'training.progress.line'

    training_progress_id = fields.Many2one('training.progress', 
        string="Training Progress Reference", ondelete="cascade", index=True, copy=False)
    employee_ids = fields.Many2one('hr.employee', string="Employee", copy=True)
    job_position = fields.Char(string="JOb Position")
    department = fields.Char(string="Department")


class CustomHREmployee(models.Model):
    _inherit = 'hr.employee'

    training_progress_line_id = fields.Many2one('training.progress.line', 
        string="Training Progress Line", ondelete="cascade", index=True, copy=False)

    training_progress_id = fields.Many2one('training.progress', 
        string="Training Progress", ondelete="cascade", index=True, copy=False)