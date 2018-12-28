from odoo import models, fields, api,_
from odoo.exceptions import UserError, AccessError
from lxml import etree
from odoo.tools.translate import html_translate
from odoo.osv.orm import setup_modifiers
from cStringIO import StringIO
import base64
from zipfile import ZipFile
from odoo.exceptions import UserError, AccessError

class DeveloperTaskList(models.Model):
    _inherit='developer.task.list'
    
    module_file = fields.Binary('Module File')
    module_file_name = fields.Char('Module File Name')
        
    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(DeveloperTaskList,self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        user = self.env.user
        #Project Developers only can edit module Repository
#         developer_group = user.user_has_groups('developer_task.group_project_developer_access')
        ir_model_data = self.env['ir.model.data']
        developer_group = ir_model_data.get_object_reference('developer_task', 'group_project_developer_access')
        #If user is with developer access right, Status and Modules can be update only by this user
        if developer_group:
            developer_group = self.env['res.groups'].sudo().browse(developer_group[1])        
            if view_type == "form":
                user = self.env.user
                user_as_developer = user.id in map(int,developer_group.users)
                if user_as_developer:
                    doc = etree.XML(res['arch'])
                    for node in doc.iter(tag="field"):
                        if node.get("name","") not in ('module_ids','status_project'):
                            node.set('attrs', "{'readonly':1}")
                            setup_modifiers(node, res['fields'][node.get("name")])
                    res['arch'] = etree.tostring(doc)
                                    
        if view_type == "search":
            context = self._context
            if context.get('from_team_developers_kanban',False):
                active_id = context.get('active_id',False)
                if active_id:
                    doc = etree.XML(res['arch'])
                    record = self.env['team.developers'].browse(active_id)
                    for node in doc.xpath("//filter[@name='developer_filter']"):
                        domain = [('developer_id','=',record.user_id.id),('status_project','!=','done')]
                        node.set('domain',str(domain))
                    res['arch'] = etree.tostring(doc)
        return res
    
    #This button is set because when Developer Task form Developer Dashboard
    #at that time, we need to close Popup automatically and refresh the kanban
    @api.multi
    def button_dummy_for_save_record(self):
        return {'type': 'ir.actions.act_window_close'}
    
    @api.multi
    def download_latest_module(self):
        version_obj = self.env['version.history']
        self.inMemoryOutputFile = StringIO()
        zip_file = ZipFile(self.inMemoryOutputFile, 'a')
        if not self.module_ids:
            raise UserError(_('Warning!! Module is not available.'))
        file_compress_count = 0
        for repository in self.module_ids:
            version_id = version_obj.search([('repository_id','=',repository.id)],order="id desc",limit=1)
            if version_id:
                version_id = version_id[0]
                if version_id.module_file:
                    file_compress_count += 1
                    zip_file.writestr(version_id.filename, base64.b64decode(version_id.module_file))
#             else:
#                 raise UserError(_('Warning!! Module is not available.'))
        if not file_compress_count:
            raise UserError(_('Warning!! No file found for download. '))
        zip_file.close()
        self.inMemoryOutputFile.seek(0)
        zip_data=base64.encodestring(self.inMemoryOutputFile.getvalue())
        #attachment_id = self.pool.get('attachment.store').create(cr,uid,{'attach_file':zip_data,'filename':'modules.zip'})
        self.module_file = zip_data
        self.module_filename = 'modules.zip'
        return {
            'type' : 'ir.actions.act_url',
            'url': "web/content/?model=developer.task.list&id=" + str(self.id) + "&filename_field=module_filename&field=module_file&download=true&filename=modules.zip" ,
            'target': 'self',
            }            

class ModuleRepository(models.Model):
    _inherit = 'module.repository'
    
    @api.one
    @api.depends('version_history_ids.module_file','version_history_ids.create_date')
    def _get_latest_version_file(self):
        latest_version = self.env['version.history'].search([('repository_id','=',self.id)],order="create_date desc",limit=1)
        if latest_version:
            latest_version = latest_version[0]
            if latest_version.module_file:
                self.latest_module_file = latest_version.module_file
                self.module_filename = latest_version.filename            
#             if latest_version.module_file:
# #                 file_data = base64.decodestring(latest_version.module_file)
# # #                 file_data = pickle.loads(base64.decodestring(latest_version.module_file))
# #                 self.latest_module_file = base64.encodestring(file_data)
#                 fobj = tempfile.NamedTemporaryFile(delete=False)
#                 fname = fobj.name
#                 fobj.write(latest_version.module_file)
#                 self.latest_module_file = base64.encodestring(fobj.read())
#                 fobj.close()
#                 self.module_filename = latest_version.filename
        
#     latest_module_file = fields.Binary(compute='_get_latest_version_file',string='Attachment',store=True)
#     module_filename = fields.Char(compute='_get_latest_version_file',string='Filename',store=True)      
    latest_module_file = fields.Binary(string='Attachment')
    module_filename = fields.Char(string='Filename')
    project_manager_id = fields.Many2one('res.users','Project Manager')
    
    @api.multi
    def download_latest_version(self):
        latest_version = self.env['version.history'].search([('repository_id','=',self.id)],order="id desc",limit=1)
        if latest_version:
            latest_version = latest_version[0]
            if not latest_version.module_file:
                raise UserError(_('Warning!! There is no Module to download. '))            
            if latest_version.module_file:
                self.latest_module_file = latest_version.module_file
                self.module_filename = latest_version.filename
        return {
            'type' : 'ir.actions.act_url',
            'url': "web/content/?model=module.repository&id=" + str(self.id) + "&filename_field=module_filename&field=latest_module_file&download=true&filename=" + self.module_filename,
            'target': 'self',
            }
    
class VersionHistory(models.Model):
    _inherit='version.history'
    
    """
    Create & write override over here for the process to set the latest module attachment file with module repository
    """
    @api.model
    def create(self, vals):
        record = super(VersionHistory,self).create(vals)
        if record:
            repository_id = record.repository_id
            latest_version = self.search([('repository_id','=',repository_id.id)],order="create_date desc",limit=1)
            if latest_version:
                latest_version = latest_version[0]
                if latest_version.module_file:
                    repository_id.latest_module_file = latest_version.module_file
                    repository_id.module_filename = latest_version.filename
        return record

    @api.multi
    def write(self, vals):
        res = super(VersionHistory,self).write(vals)
        if 'create_date' in vals or 'module_file' in vals:
            for record in self.search([('id','in',self.ids)]):
                repository_id = record.repository_id
                latest_version = self.search([('repository_id','=',repository_id.id)],order="create_date desc",limit=1)
                if latest_version:
                    latest_version = latest_version[0]
                    if latest_version.module_file:
                        repository_id.latest_module_file = latest_version.module_file
                        repository_id.module_filename = latest_version.filename
        return res                

class TaskRevisionModule(models.Model):
    _inherit='task.revision.module'
    
    #Set default value for date_asked field
    date_asked = fields.Datetime(string='Date Asked',default=fields.Datetime.now)
    
    @api.multi
    def download_attachtement(self):
        if not self.attch_bin_revision:
            raise UserError(_('Warning!! There is no attachment to download. '))
        return {
            'type' : 'ir.actions.act_url',
            'url': "web/content/?model=task.revision.module&id=" + str(self.id) + "&filename_field=filename&field=attch_bin_revision&download=true&filename=" + self.filename,
            'target': 'self',
            }