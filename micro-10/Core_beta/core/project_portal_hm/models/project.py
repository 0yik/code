# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from datetime import datetime
from odoo.exceptions import UserError, AccessError

class ProjectProject(models.Model):
    _inherit = 'project.project'
    
    @api.multi
    def _total_meetings(self):
        for record in self:
            record.total_meetings = len(record.meeting_ids)

    @api.one
    @api.depends('developer_task_ids.developer_id')
    def _get_project_developers(self):
        developer_tasks = self.env['developer.task.list'].search([('project_id','=',self.id)])
        developers = []
        for task in developer_tasks:
            if task.developer_id:
                developers.append(task.developer_id.id)
        developers = list(set(developers))
        self.project_developer_ids = developers
                        
    manager_ids = fields.Many2many('res.users','manager_project_rel','project_id','manager_id', string='Project Manager')
    specialist_ids = fields.Many2many('res.users','specialist_project_rel','project_id','specialist_id', string='System Specialists')
    customer_ids = fields.Many2many('res.users','customer_project_rel','project_id','customer_id', string='Customer')
    category = fields.Selection([('a','A'),('b','B'),('c','C'),('d','D'),('e','E'),('f','F')],string='Project Category',)
    module_ids = fields.Many2many('project.module', string='Module')
    sbd = fields.Binary(string='SBD')
    filename = fields.Char(string='File Name')
    document_ids = fields.One2many('project.document','project_id',string='Document')
    product_ids = fields.Many2many('product.product','project_product_join_rel','project_id','product_id', string='Products',
                                   domain=[('sale_ok','=',True)])
    meeting_ids = fields.Many2many('calendar.event','meeting_project_rel','project_id','meeting_id',string="Meetings")
    total_meetings = fields.Integer(compute='_total_meetings', string='Meetings')
    project_developer_ids = fields.Many2many(comodel_name='res.users', string='Project Developers',
                                             compute='_get_project_developers',store=True)
    
    @api.model
    def default_get(self, fields_list):
        result = super(ProjectProject, self).default_get(fields_list)
        data_list = []
        for record in ['FRD','UAT','Training Sign Of','Project Completion Sign Off']:
            vals = {}
            vals['name'] = record
            vals['date'] = fields.Datetime.now()
            vals['planned_date_readonly'] = False
            data_list.append((0, 0, vals))
        result['document_ids'] = data_list
        #In tasks, sone default stages needs to be add. So if any project is going to generate, we will assign
        #some default stages in it 
        stages_ids = self.env['project.task.type'].search([('use_as_default','=',True)])
        stages_ids = map(int,stages_ids)
        if stages_ids:
            result['type_ids'] = stages_ids
        return result
        
    @api.multi
    def project_meetings(self):
        self.ensure_one()
        action = self.env.ref('calendar.action_calendar_event').read()[0]
        if action:
            meeting_ids = self.env['calendar.event'].search([('project_ids','in',self.ids)])
            meeting_ids = map(int,meeting_ids)
            action['domain'] = [('id','in',meeting_ids)]
            action['context'] = {
                'default_project_ids': self.ids,
            }
        return action
    
    @api.multi
    def write(self, vals):
        res = super(ProjectProject, self).write(vals)
        if 'active' in vals:
            project_milestone_ids = self.env['project.document'].search([('project_id','in',self.ids),'|',('active','=',True),('active','=',False)])
            for milestone in project_milestone_ids:
                milestone.write({'active':vals.get('active',False)})
        return res
    

ProjectProject()

class ProjectModule(models.Model):
    _name = 'project.module'

    color = fields.Integer(string='Color Index')
    name = fields.Char('Name')

ProjectModule()

class ProductDocument(models.Model):
    _name = 'project.document'
    _order = 'planned_start_date'
    
    @api.one
    @api.depends('project_id.manager_ids')
    def _get_manager_specialists_name(self):
        project_id = self.project_id
        if not project_id:
            self.project_managers = ''
            self.system_specialists = ''
        else:
            self.project_managers = project_id.manager_ids and ','.join([x.name for x in project_id.manager_ids]) or ''
            self.system_specialists = project_id.specialist_ids and ','.join([x.name for x in project_id.specialist_ids]) or '' 
            

    name = fields.Text(string='Document Name')
    description = fields.Text(string="Description")
    date = fields.Datetime(string='Date Started', default=fields.Date.context_today)
    type = fields.Selection([('project document','Project Document'),('client document','Client Document'),('others','Others')],string='Type')
    project_id = fields.Many2one('project.project', string='Project')
    data = fields.Binary('Attachment')
    filename = fields.Char('File Name')
    date_completed = fields.Date("Date Completed")
    notes = fields.Text("Remarks")
    planned_start_date = fields.Date("Planned Start Date")
    planned_end_date = fields.Date("Planned End Date")
    planned_date_readonly = fields.Boolean("Planned Date Readonly",default=False)
    project_managers = fields.Char(compute="_get_manager_specialists_name",string="Project Manager",store=True)
    system_specialists = fields.Char(compute="_get_manager_specialists_name",string="System Specialist")
    project_category = fields.Selection(related="project_id.category", string='Project Category',readonly=True,store=True)
    active = fields.Boolean("Active",default=True)
#     planned_end_readonly = fields.Boolean("Planned End Date Readonly")
    
    @api.multi
    def data_commit(self):
        msg = ""
        if (not self.planned_start_date) and (not self.planned_end_date):
            msg = "Needs to set Planned Start Date and Planned End Date."
        elif not self.planned_start_date:
            msg = "Needs to set Planned Start Date "
        elif not self.planned_end_date:
            msg = "Needs to set Planned End Date "
        if msg:
            raise UserError(_(msg))
        else:
            self.planned_date_readonly = True
        return
    

ProductDocument()

class CalendarEvents(models.Model):
    _inherit='calendar.event'
      
    project_ids = fields.Many2many('project.project','meeting_project_rel','meeting_id','project_id',string="Projects")

class ProjectTasks(models.Model):
    _inherit = 'project.task'
    
    quoted_price = fields.Float('Quoted Price')
    
class ProjectTaskStages(models.Model):
    _inherit = 'project.task.type'
    
    use_as_default = fields.Boolean('Use as Default',help='Indicates weather the stage will be set as by default in new project or not.')    