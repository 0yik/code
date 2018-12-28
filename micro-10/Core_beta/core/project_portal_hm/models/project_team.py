from odoo import models, fields, api,_
from odoo.exceptions import UserError, AccessError
from lxml import etree
from odoo.tools.translate import html_translate
from odoo.osv.orm import setup_modifiers

#Its specially for manage Task Details in Kanban View
#we need to make project name bold in kanban view
class TaskDetails(models.Model):
    _name='developer.task.details'
    
    project_id = fields.Many2one('project.project',string='Project')
    task_details = fields.Char('Task Details')
    team_developer_id = fields.Many2one('team.developers','Related Project Team')
    
class TeamDevelopers(models.Model):
    _name='team.developers'
    
    @api.multi
    def get_projects(self):
        for record in self:
            project_ids = []
            user_id = record.user_id
            tasks = tasks = self.env['developer.task.list'].search([('developer_id','=',user_id.id),('status_project','in',['pending','toberevised'])])
            for task in tasks:
                if task.projet_id:
                    project_ids.append(task.projet_id.id)
            record.project_ids = project_ids  
    
    @api.multi
    def _get_user_task_details_1(self):
        for record in self:
            user_id = record.user_id
            task_details = ''
            if user_id:
                tasks = self.env['developer.task.list'].search([('developer_id','=',user_id.id),('status_project','in',['pending','toberevised','implemented'])])
                task_data = {}
                for task in tasks:
                    #it will collect the details of the task, in which project is set
                    if not task.project_id:
                        continue
                    project_id = task.project_id
                    if project_id.name not in task_data:
                        task_data[project_id.name] = {}
                        
                    if not task.status_project in task_data[project_id.name]:
                        task_data[project_id.name][task.status_project] = []               
                    task_data[project_id.name][task.status_project].append(task.name or '')
                    
            for key,val in task_data.items():
                task_details += "%s - " %(key) 
                for status,task_list in val.items():
                    task_details += ' & '.join(val[status])
                    task_details += " - %s, " %(status)
                task_details += "\n"
                
            record.user_task_details = task_details
    
    @api.multi
    def _set_color(self):
        developer_task = self.env['developer.task.list']
        for record in self:
            if record.dashboard_team_id and record.dashboard_team_id != record.current_team_id:
                record.color = 4
            else:  
                task_status = {'pending':0,'toberevised':0}
                tasks = developer_task.search([('developer_id','=',record.user_id.id)])
                task_count = 0
                for task in tasks:
                    if task.status_project in ['pending','toberevised']:
                        task_count = task_count + 1
                if task_count == 1:
                    record.color = 6
                elif task_count > 1:
                    record.color = 8
                else:
                    record.color = 0

    @api.model
    def _read_group_team_ids(self, stages, domain, order):
        team_ids = self.env['project.team'].search([])
        return team_ids
    
#     @api.multi
#     def _get_all_projects(self):
#         for record in self:
#             record.project_ids = [2,3]
                        
    user_id = fields.Many2one('res.users','User')
    current_team_id = fields.Many2one('project.team','Current Project Team')
    dashboard_team_id = fields.Many2one('project.team','Dashboard Project Team',
                                        help='Team, where the user will move from current team from Developer Dashboard.',
                                        group_expand='_read_group_team_ids')
    user_task_details = fields.Char(compute='_get_user_task_details_1',string="User Task Details")
    color = fields.Integer(compute='_set_color',string='Color Index')
#     project_ids = fields.Many2many('project.project',string="Projects",compute='_get_all_projects')
#     payment_move_line_ids = fields.Many2many('account.move.line', string='Payment Move Lines', compute='_compute_payments', store=True)
        
    @api.model
    def create(self,vals):
        user_id = vals.get('user_id',False)
        if user_id: 
            existing_teams = self.search([('user_id','=',user_id)])
            if existing_teams:
                user = self.env['res.users'].browse(user_id)
                team = existing_teams[0].current_team_id
                raise UserError(_('User : %s is already with team : %s. You can not assign same user in other team.'%(user.name,team.name)))
        if 'current_team_id' in vals:
            vals.update({'dashboard_team_id':vals.get('current_team_id',False)})
        return super(TeamDevelopers,self).create(vals)
    
    @api.multi
    def write(self, vals):
        if 'dashboard_team_id' in vals:
            #dashboard team id found in vals it means someone tries to move developer from one team to other
            #we need to restrict that only project manager can do it.
            project_manager_group = self.env.user.user_has_groups('project.group_project_manager')
            if not project_manager_group:
                raise UserError(_('Sorry!! You can not move developer from one team to other. Project Manager only can do this.')) 
        return super(TeamDevelopers,self).write(vals)
    
    @api.multi
    def open_developer_task_form(self):
        project_manager_group = self.env.user.user_has_groups('project.group_project_manager')
        if not project_manager_group:
            raise UserError(_('Sorry!! User with Project Manager access only can assign task to developers.'))
        project_head_group = self.env.user.user_has_groups('developer_task.group_project_head')
        #project manager can only assign task to his related tema developers,
        #but project head can assign task to developer of any team
        ctx = {}
        if not project_head_group:
            project_managers = []
            if self.dashboard_team_id:
                project_managers.append(self.dashboard_team_id.project_manager.id)
                project_managers += map(int,self.dashboard_team_id.specialist_ids)
            if self.current_team_id.project_manager:
                project_managers.append(self.current_team_id.project_manager.id)
            project_managers += map(int,self.current_team_id.specialist_ids) 
            
            if self.env.user.id not in project_managers:
                raise UserError(_('the team of which you are project manager/system analyst, you can assign the task to the developers of the corresponding team only.'))
        if self.dashboard_team_id and self.dashboard_team_id.project_manager:
            ctx.update({'default_manager_id':self.dashboard_team_id.project_manager.id})
        ctx.update({'default_developer_id':self.user_id.id,'default_status_project':'pending'})
        return {
            'name': _('Developer Task'),
            'type': 'ir.actions.act_window',
            'res_model':'developer.task.list',
            'target': 'new',
            'view_mode':'form',
            'context':ctx,
        }

    @api.multi
    def get_task_data(self):
        tasks = self.env['developer.task.list'].search([])
        return tasks                
        
    
class ProjectTeam(models.Model):
    _name='project.team'
    
    name = fields.Char('Team Name',required=True)
    project_manager = fields.Many2one('res.users','Project Manager')
    developer_ids = fields.One2many('team.developers','current_team_id','Current Team')
    specialist_ids = fields.Many2many('res.users','specialist_user_rel','team_id','user_id','System Specialist')

# class DeveloperTaskList(models.Model):
#     _inherit='developer.task.list'
#     
#     @api.model
#     def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
#         res = super(DeveloperTaskList,self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
#         user = self.env.user
#         #Project Developers only can edit module Repository
# #         developer_group = user.user_has_groups('developer_task.group_project_developer_access')
#         ir_model_data = self.env['ir.model.data']
#         developer_group = ir_model_data.get_object_reference('developer_task', 'group_project_developer_access')
#         #If user is with developer access right, Status and Modules can be update only by this user
#         if developer_group:
#             developer_group = self.env['res.groups'].sudo().browse(developer_group[1])        
#             if view_type == "form":
#                 user = self.env.user
#                 user_as_developer = user.id in map(int,developer_group.users)
#                 if user_as_developer:
#                     doc = etree.XML(res['arch'])
#                     for node in doc.iter(tag="field"):
#                         if node.get("name","") not in ('module_ids','status_project'):
#                             node.set('attrs', "{'readonly':1}")
#                             setup_modifiers(node, res['fields'][node.get("name")])
#                     res['arch'] = etree.tostring(doc)
#                                     
#         if view_type == "search":
#             context = self._context
#             if context.get('from_team_developers_kanban',False):
#                 active_id = context.get('active_id',False)
#                 if active_id:
#                     doc = etree.XML(res['arch'])
#                     record = self.env['team.developers'].browse(active_id)
#                     for node in doc.xpath("//filter[@name='developer_filter']"):
#                         domain = [('developer_id','=',record.user_id.id),('status_project','!=','done')]
#                         node.set('domain',str(domain))
#                     res['arch'] = etree.tostring(doc)
#         return res
#     
#     #This button is set because when Developer Task form Developer Dashboard
#     #at that time, we need to close Popup automatically and refresh the kanban
#     @api.multi
#     def button_dummy_for_save_record(self):
#         return {'type': 'ir.actions.act_window_close'}    
