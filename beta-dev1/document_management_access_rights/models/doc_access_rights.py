from odoo import api, fields, models, _
from muk_dms.models import muk_dms_base as base
from odoo.exceptions import UserError

class DocumentMgmAccessRights(models.Model):
    _inherit = 'document.mgm.access.rights'
    _description = 'Document Management Access Rights'
    _order = 'id desc'

    name = fields.Char( string='Access')
    access_group_ids = fields.Many2many('access.rights.group', string='Access Rights Groups')
    muk_dms_id = fields.Many2one('muk_dms.directory','Directory')
    muk_file_id = fields.Many2one('muk_dms.file', 'File')

DocumentMgmAccessRights()

class Directory(base.DMSModel):
    _inherit = 'muk_dms.directory'

    doc_mgm_access_group_ids = fields.One2many('document.mgm.access.rights','muk_dms_id','Document Management')

    @api.model
    def default_get(self, fields):
        rec = super(Directory, self).default_get(fields)
        all_data = []
        all_data.append((0, 0, {'name': 'Create'}))
        all_data.append((0, 0, {'name': 'Read'}))
        all_data.append((0, 0, {'name': 'Edit(own)'}))
        all_data.append((0, 0, {'name': 'Edit(other)'}))
        all_data.append((0, 0, {'name': 'Delete(own)'}))
        all_data.append((0, 0, {'name': 'Delete(other)'}))
        rec['doc_mgm_access_group_ids'] = all_data
        return rec

    @api.model
    def create(self, vals):
        record = super(Directory, self).create(vals)
        model_obj = self.env['ir.model'].search([('name','=','Directory')],limit=1)
        for group in record.doc_mgm_access_group_ids:
           for group1 in group.access_group_ids:
               if group.name == 'Create':
                    rule_vals = {}
                    rule_vals['name'] = record.name
                    rule_vals['model_id'] = model_obj.id
                    rule_vals['perm_read'] = True
                    rule_vals['perm_write'] = True
                    rule_vals['perm_create'] = True
                    rule_vals['perm_unlink'] = False
                    rule_vals['domain_force'] = [('id','=',record.id)]
                    rule_vals['groups'] = [(6,0,group1.group_ids.ids)]
                    self.env['ir.rule'].create(rule_vals)

               if group1.group_ids and group.name == 'Read':
                   rule_vals = {}
                   rule_vals['name'] = record.name
                   rule_vals['model_id'] = model_obj.id
                   rule_vals['perm_read'] = True
                   rule_vals['perm_write'] = False
                   rule_vals['perm_create'] = False
                   rule_vals['perm_unlink'] = False
                   rule_vals['domain_force'] = [('id', '=', record.id)]
                   rule_vals['groups'] = [(6, 0, group1.group_ids.ids)]
                   self.env['ir.rule'].create(rule_vals)

               if group1.group_ids and group.name == 'Edit(own)':

                   rule_vals = {}
                   rule_vals['name'] = record.name
                   rule_vals['model_id'] = model_obj.id
                   rule_vals['perm_read'] = True
                   rule_vals['perm_write'] = True
                   rule_vals['perm_create'] = False
                   rule_vals['perm_unlink'] = False
                   rule_vals['domain_force'] = [('id', '=', record.id)]
                   rule_vals['groups'] = [(6, 0, group1.group_ids.ids)]
                   self.env['ir.rule'].create(rule_vals)

               if group1.group_ids and group.name == 'Edit(other)':
                   rule_vals = {}
                   rule_vals['name'] = record.name
                   rule_vals['model_id'] = model_obj.id
                   rule_vals['perm_read'] = True
                   rule_vals['perm_write'] = True
                   rule_vals['perm_create'] = False
                   rule_vals['perm_unlink'] = False
                   rule_vals['domain_force'] = [('id', '=', record.id)]
                   rule_vals['groups'] = [(6, 0, group1.group_ids.ids)]
                   self.env['ir.rule'].create(rule_vals)

               if group1.group_ids and group.name == 'Delete(own)':
                   rule_vals = {}
                   rule_vals['name'] = record.name
                   rule_vals['model_id'] = model_obj.id
                   rule_vals['perm_read'] = True
                   rule_vals['perm_write'] = False
                   rule_vals['perm_create'] = False
                   rule_vals['perm_unlink'] = True
                   rule_vals['domain_force'] = [('id', '=', record.id)]
                   rule_vals['groups'] = [(6, 0, group1.group_ids.ids)]
                   self.env['ir.rule'].create(rule_vals)

               if group1.group_ids and group.name == 'Delete(other)':
                   rule_vals = {}
                   rule_vals['name'] = record.name
                   rule_vals['model_id'] = model_obj.id
                   rule_vals['perm_read'] = True
                   rule_vals['perm_write'] = False
                   rule_vals['perm_create'] = False
                   rule_vals['perm_unlink'] = True
                   rule_vals['domain_force'] = [('id', '=', record.id)]
                   rule_vals['groups'] = [(6, 0, group1.group_ids.ids)]
                   self.env['ir.rule'].create(rule_vals)
        return record

    @api.multi
    def unlink(self):
        self._check_group()
        return super(Directory, self).unlink()

    def _check_group(self):
        for group in self.doc_mgm_access_group_ids:
            for group1 in group.access_group_ids:
                if group.name == 'delete(own)' or group.name == 'delete(own)':
                    if not group.doc_mgm_access_group_ids:
                        raise UserError(_("Sorry, You don't have access to delete this directory."))
        return True

    @api.multi
    def write(self,vals):
        res = super(Directory, self).write(vals)
        model_obj = self.env['ir.model'].search([('name', '=', 'Directory')], limit=1)
        domain_rule = "[('id','=','"+str(res)+"]"

        for record in self:
            if model_obj:
                # finding record rule for craete, delete, edit, unlink
                create_rule_obj = self.env['ir.rule'].search([('name','=',record.name),('model_id','=',model_obj.id),('domain','=',domain_rule)])
                create_rule_obj.unlink()
                # creating record rule
                model_obj = self.env['ir.model'].search([('name', '=', 'Directory')], limit=1)
                for group in record.doc_mgm_access_group_ids:
                    for group1 in group.access_group_ids:
                        if group.name == 'Create':
                            rule_vals = {}
                            rule_vals['name'] = record.name
                            rule_vals['model_id'] = model_obj.id
                            rule_vals['perm_read'] = True
                            rule_vals['perm_write'] = True
                            rule_vals['perm_create'] = True
                            rule_vals['perm_unlink'] = False
                            rule_vals['domain_force'] = [('id', '=', record.id)]
                            rule_vals['groups'] = [(6, 0, group1.group_ids.ids)]
                            self.env['ir.rule'].create(rule_vals)

                        if group1.group_ids and group.name == 'Read':

                            rule_vals = {}
                            rule_vals['name'] = record.name
                            rule_vals['model_id'] = model_obj.id
                            rule_vals['perm_read'] = True
                            rule_vals['perm_write'] = False
                            rule_vals['perm_create'] = False
                            rule_vals['perm_unlink'] = False
                            rule_vals['domain_force'] = [('id', '=', record.id)]
                            rule_vals['groups'] = [(6, 0, group1.group_ids.ids)]
                            self.env['ir.rule'].create(rule_vals)

                        if group1.group_ids and group.name == 'Edit(own)':
                            rule_vals = {}
                            rule_vals['name'] = record.name
                            rule_vals['model_id'] = model_obj.id
                            rule_vals['perm_read'] = True
                            rule_vals['perm_write'] = True
                            rule_vals['perm_create'] = False
                            rule_vals['perm_unlink'] = False
                            rule_vals['domain_force'] = [('id', '=', record.id)]
                            rule_vals['groups'] = [(6, 0, group1.group_ids.ids)]
                            self.env['ir.rule'].create(rule_vals)

                        if group1.group_ids and group.name == 'Edit(other)':
                            rule_vals = {}
                            rule_vals['name'] = record.name
                            rule_vals['model_id'] = model_obj.id
                            rule_vals['perm_read'] = True
                            rule_vals['perm_write'] = True
                            rule_vals['perm_create'] = False
                            rule_vals['perm_unlink'] = False
                            rule_vals['domain_force'] = [('id', '=', record.id)]
                            rule_vals['groups'] = [(6, 0, group1.group_ids.ids)]
                            self.env['ir.rule'].create(rule_vals)

                        if group1.group_ids and group.name == 'Delete(own)':
                            rule_vals = {}
                            rule_vals['name'] = record.name
                            rule_vals['model_id'] = model_obj.id
                            rule_vals['perm_read'] = True
                            rule_vals['perm_write'] = False
                            rule_vals['perm_create'] = False
                            rule_vals['perm_unlink'] = True
                            rule_vals['domain_force'] = [('id', '=', record.id)]
                            rule_vals['groups'] = [(6, 0, group1.group_ids.ids)]
                            self.env['ir.rule'].create(rule_vals)

                        if group1.group_ids and group.name == 'Delete(other)':
                            rule_vals = {}
                            rule_vals['name'] = record.name
                            rule_vals['model_id'] = model_obj.id
                            rule_vals['perm_read'] = True
                            rule_vals['perm_write'] = False
                            rule_vals['perm_create'] = False
                            rule_vals['perm_unlink'] = True
                            rule_vals['domain_force'] = [('id', '=', record.id)]
                            rule_vals['groups'] = [(6, 0, group1.group_ids.ids)]
                            self.env['ir.rule'].create(rule_vals)
            # write_rule_obj = self.env['ir.rule'].search(
            #     [('name', '=', record.name), ('model_id', '=', model_obj.id), ('domain', '=', domain_rule),
            #      ('perm_write', '=', True)])
            # read_rule_obj = self.env['ir.rule'].search(
            #     [('name', '=', record.name), ('model_id', '=', model_obj.id), ('domain', '=', domain_rule),
            #      ('perm_read', '=', True)])
            # delete_rule_obj = self.env['ir.rule'].search(
            #     [('name', '=', record.name), ('model_id', '=', model_obj.id), ('domain', '=', domain_rule),
            #      ('perm_delete', '=', True)])
            #
            # # if finded record rules unlink the object goup and add groups according to dir
            # for dir in record.doc_mgm_access_group_ids:
            #     for dir1 in dir.group_ids:
            #         if dir.name == 'craete' and record.doc_mgm_access_group_ids and create_rule_obj:
            #             create_rule_obj.group = False
            #             create_rule_obj.group = [(6,0, dir1.group_ids.ids)]
            #         if dir.name == 'write' and record.doc_mgm_access_group_ids and :
            #             create_rule_obj.group = False
            #             create_rule_obj.group = [(6, 0, dir1.group_ids.ids)]
        return res

Directory()

class File(base.DMSModel):
    _inherit = 'muk_dms.file'

    doc_mgm_access_group_ids = fields.One2many('document.mgm.access.rights', 'muk_file_id', 'File')

    @api.model
    def default_get(self, fields):
        rec = super(File, self).default_get(fields)
        all_data = []
        all_data.append((0, 0, {'name': 'Create'}))
        all_data.append((0, 0, {'name': 'Read'}))
        all_data.append((0, 0, {'name': 'Edit(own)'}))
        all_data.append((0, 0, {'name': 'Edit(other)'}))
        all_data.append((0, 0, {'name': 'Delete(own)'}))
        all_data.append((0, 0, {'name': 'Delete(other)'}))
        rec['doc_mgm_access_group_ids'] = all_data
        return rec

    @api.model
    def create(self, vals):
        record = super(File, self).create(vals)
        model_obj = self.env['ir.model'].search([('name', '=', 'File')], limit=1)
        for group in record.doc_mgm_access_group_ids:
            for group1 in group.access_group_ids:
                if group.name == 'Create':
                    rule_vals = {}
                    rule_vals['name'] = record.name
                    rule_vals['model_id'] = model_obj.id
                    rule_vals['perm_read'] = True
                    rule_vals['perm_write'] = True
                    rule_vals['perm_create'] = True
                    rule_vals['perm_unlink'] = False
                    rule_vals['domain_force'] = [('id', '=', record.id)]
                    rule_vals['groups'] = [(6, 0, group1.group_ids.ids)]
                    self.env['ir.rule'].create(rule_vals)

                if group1.group_ids and group.name == 'Read':
                    rule_vals = {}
                    rule_vals['name'] = record.name
                    rule_vals['model_id'] = model_obj.id
                    rule_vals['perm_read'] = True
                    rule_vals['perm_write'] = False
                    rule_vals['perm_create'] = False
                    rule_vals['perm_unlink'] = False
                    rule_vals['domain_force'] = [('id', '=', record.id)]
                    rule_vals['groups'] = [(6, 0, group1.group_ids.ids)]
                    self.env['ir.rule'].create(rule_vals)

                if group1.group_ids and group.name == 'Edit(own)':
                    rule_vals = {}
                    rule_vals['name'] = record.name
                    rule_vals['model_id'] = model_obj.id
                    rule_vals['perm_read'] = True
                    rule_vals['perm_write'] = True
                    rule_vals['perm_create'] = False
                    rule_vals['perm_unlink'] = False
                    rule_vals['domain_force'] = [('id', '=', record.id)]
                    rule_vals['groups'] = [(6, 0, group1.group_ids.ids)]
                    self.env['ir.rule'].create(rule_vals)

                if group1.group_ids and group.name == 'Edit(other)':
                    rule_vals = {}
                    rule_vals['name'] = record.name
                    rule_vals['model_id'] = model_obj.id
                    rule_vals['perm_read'] = True
                    rule_vals['perm_write'] = True
                    rule_vals['perm_create'] = False
                    rule_vals['perm_unlink'] = False
                    rule_vals['domain_force'] = [('id', '=', record.id)]
                    rule_vals['groups'] = [(6, 0, group1.group_ids.ids)]
                    self.env['ir.rule'].create(rule_vals)

                if group1.group_ids and group.name == 'Delete(own)':
                    rule_vals = {}
                    rule_vals['name'] = record.name
                    rule_vals['model_id'] = model_obj.id
                    rule_vals['perm_read'] = True
                    rule_vals['perm_write'] = False
                    rule_vals['perm_create'] = False
                    rule_vals['perm_unlink'] = True
                    rule_vals['domain_force'] = [('id', '=', record.id)]
                    rule_vals['groups'] = [(6, 0, group1.group_ids.ids)]
                    self.env['ir.rule'].create(rule_vals)

                if group1.group_ids and group.name == 'Delete(other)':
                    rule_vals = {}
                    rule_vals['name'] = record.name
                    rule_vals['model_id'] = model_obj.id
                    rule_vals['perm_read'] = True
                    rule_vals['perm_write'] = False
                    rule_vals['perm_create'] = False
                    rule_vals['perm_unlink'] = True
                    rule_vals['domain_force'] = [('id', '=', record.id)]
                    rule_vals['groups'] = [(6, 0, group1.group_ids.ids)]
                    self.env['ir.rule'].create(rule_vals)

        return record

    @api.multi
    def write(self, vals):
        res = super(File, self).write(vals)
        model_obj = self.env['ir.model'].search([('name', '=', 'File')], limit=1)
        domain_rule = "[('id','=','" + str(res) + "]"

        for record in self:
            if model_obj:
                # finding record rule for craete, delete, edit, unlink
                create_rule_obj = self.env['ir.rule'].search(
                    [('name', '=', record.name), ('model_id', '=', model_obj.id), ('domain', '=', domain_rule)])
                create_rule_obj.unlink()
                # creating record rule
                model_obj = self.env['ir.model'].search([('name', '=', 'Directory')], limit=1)
                for group in record.doc_mgm_access_group_ids:
                    for group1 in group.access_group_ids:
                        if group.name == 'Create':
                            rule_vals = {}
                            rule_vals['name'] = record.name
                            rule_vals['model_id'] = model_obj.id
                            rule_vals['perm_read'] = True
                            rule_vals['perm_write'] = True
                            rule_vals['perm_create'] = True
                            rule_vals['perm_unlink'] = False
                            rule_vals['domain_force'] = [('id', '=', record.id)]
                            rule_vals['groups'] = [(6, 0, group1.group_ids.ids)]
                            self.env['ir.rule'].create(rule_vals)

                        if group1.group_ids and group.name == 'Read':
                            rule_vals = {}
                            rule_vals['name'] = record.name
                            rule_vals['model_id'] = model_obj.id
                            rule_vals['perm_read'] = True
                            rule_vals['perm_write'] = False
                            rule_vals['perm_create'] = False
                            rule_vals['perm_unlink'] = False
                            rule_vals['domain_force'] = [('id', '=', record.id)]
                            rule_vals['groups'] = [(6, 0, group1.group_ids.ids)]
                            self.env['ir.rule'].create(rule_vals)

                        if group1.group_ids and group.name == 'Edit(own)':
                            rule_vals = {}
                            rule_vals['name'] = record.name
                            rule_vals['model_id'] = model_obj.id
                            rule_vals['perm_read'] = True
                            rule_vals['perm_write'] = True
                            rule_vals['perm_create'] = False
                            rule_vals['perm_unlink'] = False
                            rule_vals['domain_force'] = [('id', '=', record.id)]
                            rule_vals['groups'] = [(6, 0, group1.group_ids.ids)]
                            self.env['ir.rule'].create(rule_vals)

                        if group1.group_ids and group.name == 'Edit(other)':
                            rule_vals = {}
                            rule_vals['name'] = record.name
                            rule_vals['model_id'] = model_obj.id
                            rule_vals['perm_read'] = True
                            rule_vals['perm_write'] = True
                            rule_vals['perm_create'] = False
                            rule_vals['perm_unlink'] = False
                            rule_vals['domain_force'] = [('id', '=', record.id)]
                            rule_vals['groups'] = [(6, 0, group1.group_ids.ids)]
                            self.env['ir.rule'].create(rule_vals)

                        if group1.group_ids and group.name == 'Delete(own)':
                            rule_vals = {}
                            rule_vals['name'] = record.name
                            rule_vals['model_id'] = model_obj.id
                            rule_vals['perm_read'] = True
                            rule_vals['perm_write'] = False
                            rule_vals['perm_create'] = False
                            rule_vals['perm_unlink'] = True
                            rule_vals['domain_force'] = [('id', '=', record.id)]
                            rule_vals['groups'] = [(6, 0, group1.group_ids.ids)]
                            self.env['ir.rule'].create(rule_vals)

                        if group1.group_ids and group.name == 'Delete(other)':
                            rule_vals = {}
                            rule_vals['name'] = record.name
                            rule_vals['model_id'] = model_obj.id
                            rule_vals['perm_read'] = True
                            rule_vals['perm_write'] = False
                            rule_vals['perm_create'] = False
                            rule_vals['perm_unlink'] = True
                            rule_vals['domain_force'] = [('id', '=', record.id)]
                            rule_vals['groups'] = [(6, 0, group1.group_ids.ids)]
                            self.env['ir.rule'].create(rule_vals)
        return res

    @api.multi
    def unlink(self):
        self._check_group()
        return super(File, self).unlink()

    def _check_group(self):
        if not self.env.ref('base.group_erp_manager'):
            for group in self.doc_mgm_access_group_ids:
                if group.name == 'delete(own)' or group.name == 'delete(own)':
                    if not group.doc_mgm_access_group_ids:
                        raise UserError(_("Sorry, You don't have access to delete this directory."))
        return True

File()