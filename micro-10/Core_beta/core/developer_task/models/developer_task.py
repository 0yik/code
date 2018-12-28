# -*- coding: utf-8 -*-
from odoo import models, fields, api,SUPERUSER_ID
from datetime import datetime
from lxml import etree
from odoo.osv.orm import setup_modifiers
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from dateutil.relativedelta import relativedelta
import random

class ProjectProject(models.Model):
    _inherit = 'project.project'

    developer_task_ids = fields.One2many('developer.task.list','project_id',string='Developer Tasks')

ProjectProject()

class ProjectSettings(models.TransientModel):
    _inherit = 'project.config.settings'

    past_dated_task_days = fields.Integer(string='Past Dated Task Days', help='System will run a scheduler to update task status from Implemented to Done if the task is older than the past dated task days.',
                                          default=30)

    @api.multi
    def set_past_dated_task_days(self):
        return self.env['ir.values'].sudo().set_default(
            'project.config.settings', 'past_dated_task_days', self.past_dated_task_days)

class DeveloperTaskList(models.Model):
    _name = 'developer.task.list'

    def set_as_done(self):
        ir_values = self.env['ir.values']
        past_dated_task_days = ir_values.get_default('project.config.settings', 'past_dated_task_days')

        for project in self.search([]):
            if project.status_project == 'implemented':
                revisions = project.revision_ids.sorted(lambda k : k.date_asked, reverse=True)
                if revisions:
                    revision = revisions[0]
                    latest_date_asked = datetime.strptime(revision.date_asked,DEFAULT_SERVER_DATETIME_FORMAT)
                    if latest_date_asked < datetime.now() - relativedelta(days=past_dated_task_days):
                        project.status_project = 'done'

    @api.multi
    def _set_color(self):
        developer_task = self.env['developer.task.list']
        for record in self:
            record.color = random.randint(0,9)
    
    @api.model
    def _get_logged_user(self):
        return self.env.uid

    @api.model
    def _get_default_state(self):
        state = self.env['developer.task.status'].search([('status_project','=','pending')])
        if state:
            return state.id

    project_id = fields.Many2one('project.project', string='Project')
    name = fields.Char(string='Function Name')
    objective_name = fields.Char(string='Objective')
    upload_video = fields.Binary('Video')
    filename = fields.Char('Filename')
    deadline_of_task = fields.Date('Deadline')
    status_project = fields.Selection([('pending', 'Pending'),('implemented','Implemented'),('toberevised','To be revised'),('tested','Tested'),('done','Done')], 'Status', default="pending")
    state = fields.Many2one('developer.task.status', string="Status", group_expand='_read_group_stage_ids', default=_get_default_state)
    type = fields.Many2one('project.task.type',string="type")
    developer_id = fields.Many2one('res.users',string='Developer')
    manager_id = fields.Many2one('res.users',string='Project Manager', default=_get_logged_user)
    module_ids = fields.Many2many('module.repository', string='Module(s)')
    proj_features = fields.Text(string='Features')
    proj_case_study = fields.Text(string='Case Study')
    revision_ids = fields.One2many('task.revision.module', 'revision_id',string='Revisions')
    color = fields.Integer(compute='_set_color',string='Color Index')
#     project_team_id = fields.Many2one('project_team')
#     developer_ids = fields.Many2one('project.team')

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        search_domain = []
        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    @api.multi
    def write(self, vals):
        #If developer user update the module repository, developer task status should be set Implemented automatically
        user_as_developer = False 
        ir_model_data = self.env['ir.model.data']
        developer_group = ir_model_data.get_object_reference('developer_task', 'group_project_developer_access')
        #If user is with developer access right, Status and Modules can be update only by this user
        if developer_group:
            developer_group = self.env['res.groups'].sudo().browse(developer_group[1])
            user_as_developer = self.env.user.id in map(int,developer_group.users)
        if user_as_developer:
            if vals.get('module_ids',False):
                module_ids = vals['module_ids'][0]
                #If there is no record, we need to do nothing. module_ids[2] is [] means there is no record in the field. 
                if len(module_ids) >= 3 and module_ids[2]:
                    vals.update({'status_project':'implemented'})
        if vals.get('status_project', False):
            state = self.env['developer.task.status'].search([('status_project','=',vals['status_project'])])
            vals['state'] = state.id
        if vals.get('state', False):
            state = self.env['developer.task.status'].browse(vals['state'])
            vals['status_project'] = state.status_project

        return super(DeveloperTaskList,self).write(vals)

    @api.onchange('state')
    def onchange_state(self):
        self.status_project = self.state.status_project
    
    @api.onchange('status_project')
    def onchange_status_project(self):
        state = self.env['developer.task.status'].search([('status_project','=',self.status_project)])
        self.state = state.id

DeveloperTaskList()

class DeveloperTaskStatus(models.Model):
    _name = 'developer.task.status'
    
    name = fields.Char('Status Name')
    status_project = fields.Selection([('pending', 'Pending'),('implemented','Implemented'),('toberevised','To be revised'),('tested','Tested'),('done','Done')], 'Status', default="pending")
    fold = fields.Boolean("Folded in Developer Task")

class TaskRevisionModule(models.Model):
    _name='task.revision.module'

    @api.model
    def _get_logged_user(self):
        return self.env.uid

    revision_summary = fields.Char(string='Revision Summary')
    date_asked = fields.Datetime(string='Date Asked',default=datetime.today())
    project_manager_review = fields.Many2one('res.users',string='Project Manager', default=_get_logged_user)
    attch_bin_revision = fields.Binary('Attachment')
    filename = fields.Char('Filename')
    revision_id = fields.Many2one('developer.task.list', string='Revision')
    developer_id = fields.Many2one('res.users', string='Developer')

TaskRevisionModule()
