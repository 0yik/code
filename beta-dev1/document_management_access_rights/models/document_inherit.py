from odoo import api, fields, models, _
from . import muk_dms_base as base
from odoo.exceptions import AccessError

class DocumentMgmAccessRights(models.Model):
    _name = 'document.mgm.access.rights'
    _description = 'Document Management Access Rights'

    name = fields.Char( string='Access')
    access_group_ids = fields.Many2many('access.rights.group', string='Access Rights Groups')
    muk_dms_id = fields.Many2one('muk_dms.directory','Directory')
    muk_file_id = fields.Many2one('muk_dms.file', 'File')

DocumentMgmAccessRights()

class IrRule(models.Model):
    _inherit = 'ir.rule'

    access_rights_id = fields.Many2one('access.rights.group',string='Access Rights Groups')
    muk_dms_id = fields.Many2one('muk_dms.directory','Directory')
    muk_file_id = fields.Many2one('muk_dms.file', 'File')

IrRule()

class Directory(base.DMSModel):
    _inherit = 'muk_dms.directory'

    @api.multi
    def update_user_group_ids(self):
        self = self.sudo()
        for record in self:
            access_group_ids = []
            for line in record.doc_mgm_access_group_ids:
                access_group_ids.extend(line.access_group_ids.ids)
            access_group_ids = list(set(access_group_ids))
            user_ids = self.env['res.users'].search([('access_rights_id', 'in', access_group_ids)]).ids
            ### Update Users ###
            # Delete old links
            self._cr.execute('DELETE FROM muk_dms_directory_res_users_rel WHERE muk_dms_directory_id=' + str(record.id))
            # Create new links
            for user_id in user_ids:
                self._cr.execute('INSERT INTO muk_dms_directory_res_users_rel (muk_dms_directory_id, res_users_id) VALUES (%s, %s)' % (record.id, user_id))
            ### Update Groups ###
            # Delete old links
            self._cr.execute('DELETE FROM access_rights_group_muk_dms_directory_rel WHERE muk_dms_directory_id=' + str(record.id))
            # Create new links
            for access_group_id in access_group_ids:
                self._cr.execute('INSERT INTO access_rights_group_muk_dms_directory_rel (muk_dms_directory_id, access_rights_group_id) VALUES (%s, %s)' % (record.id, access_group_id))
            self._cr.commit()

    doc_mgm_access_group_ids = fields.One2many('document.mgm.access.rights','muk_dms_id','Document Management')
    user_ids = fields.Many2many('res.users', string='Users')
    access_group_ids = fields.Many2many('access.rights.group', string='Access Groups')
    dir_perm_create = fields.Boolean(compute='_compute_dir_perm_create', string="Directory Create")
    dir_perm_read = fields.Boolean(compute='_compute_dir_perm_read', string="Directory Read")
    dir_perm_write = fields.Boolean(compute='_compute_dir_perm_write', string="Directory Write")
    dir_perm_unlink = fields.Boolean(compute='_compute_dir_perm_unlink', string="Directory Delete")

    @api.one
    def _compute_dir_perm_create(self):
        create_access_id = self.env['document.mgm.access.rights'].sudo().search(
            [('muk_dms_id','=',self.id),('name','=','Create')])
        if self.env.user.access_rights_id.id in create_access_id.access_group_ids.ids:
            self.dir_perm_create = True
        else:
            self.dir_perm_create = False

    @api.one
    def _compute_dir_perm_read(self):
        read_access_id = self.env['document.mgm.access.rights'].sudo().search(
            [('muk_dms_id', '=', self.id), ('name', '=', 'Read')])
        if self.env.user.access_rights_id.id in read_access_id.access_group_ids.ids:
            self.dir_perm_read = True
        else:
            self.dir_perm_read = False

    @api.one
    def _compute_dir_perm_write(self):
        write_access_id = self.env['document.mgm.access.rights'].sudo().search(
            [('muk_dms_id', '=', self.id), ('name', 'in', ['Edit(own)', 'Edit(other)'])])
        access_group_ids = sum([line.access_group_ids.ids for line in write_access_id], [])
        if self.env.user.access_rights_id.id in access_group_ids:
            self.dir_perm_write = True
        else:
            self.dir_perm_write = False

    @api.one
    def _compute_dir_perm_unlink(self):
        unlink_access_id = self.env['document.mgm.access.rights'].sudo().search(
            [('muk_dms_id', '=', self.id), ('name', 'in', ['Delete(own)', 'Delete(other)'])])
        access_group_ids = sum([line.access_group_ids.ids for line in unlink_access_id], [])
        if self.env.user.access_rights_id.id in access_group_ids:
            self.dir_perm_unlink = True
        else:
            self.dir_perm_unlink = False

    @api.model
    def default_get(self, fields):
        rec = super(Directory, self).default_get(fields)
        all_data = []
        if self.env.user.access_rights_id:
            all_data.append((0, 0, {'name': 'Create','access_group_ids': [(6,0,[self.env.user.access_rights_id.id])]}))
            all_data.append((0, 0, {'name': 'Edit(own)','access_group_ids':  [(6,0,[self.env.user.access_rights_id.id])]}))
            all_data.append((0, 0, {'name': 'Edit(other)'}))
            all_data.append((0, 0, {'name': 'Read','access_group_ids':  [(6,0,[self.env.user.access_rights_id.id])]}))
            all_data.append((0, 0, {'name': 'Delete(own)','access_group_ids':  [(6,0,[self.env.user.access_rights_id.id])]}))
            all_data.append((0, 0, {'name': 'Delete(other)'}))
            rec['access_group_ids'] = [(6, 0, [self.env.user.access_rights_id.id])]
        else:
            all_data.append((0, 0, {'name': 'Create'}))
            all_data.append((0, 0, {'name': 'Edit(own)'}))
            all_data.append((0, 0, {'name': 'Edit(other)'}))
            all_data.append((0, 0, {'name': 'Read'}))
            all_data.append((0, 0, {'name': 'Delete(own)'}))
            all_data.append((0, 0, {'name': 'Delete(other)'}))
        rec['doc_mgm_access_group_ids'] = all_data
        rec['user_ids'] = [(6, 0, [self.env.user.id])]
        return rec

    @api.multi
    def set_parent_access(self):
        self = self.sudo()
        for record in self:
            access_rights_ids = list(set(sum([line.access_group_ids.ids for line in record.doc_mgm_access_group_ids], [])))
            parent_rec = record.parent_id
            while (parent_rec):
                for access_rights_id in access_rights_ids:
                    user_ids = self.env['res.users'].search([('access_rights_id', '=', access_rights_id)]).ids
                    ### Update Users ###
                    for user_id in user_ids:
                        self._cr.execute('SELECT * FROM muk_dms_directory_res_users_rel WHERE muk_dms_directory_id=%s AND res_users_id=%s' % (parent_rec.id, user_id))
                        if not self._cr.fetchall():
                            self._cr.execute('INSERT INTO muk_dms_directory_res_users_rel (muk_dms_directory_id, res_users_id) VALUES (%s, %s)' % (parent_rec.id, user_id))
                    ### Update Groups ###
                    self._cr.execute('SELECT * FROM access_rights_group_muk_dms_directory_rel WHERE muk_dms_directory_id=%s AND access_rights_group_id=%s' % (parent_rec.id, access_rights_id))
                    if not self._cr.fetchall():
                        self._cr.execute('INSERT INTO access_rights_group_muk_dms_directory_rel (muk_dms_directory_id, access_rights_group_id) VALUES (%s, %s)' % (parent_rec.id, access_rights_id))
                    self._cr.commit()
                parent_rec = parent_rec.parent_id
                if not parent_rec:
                    break
        return True

    @api.model
    def create(self, vals):
        record = super(Directory, self.sudo()).create(vals)
        if vals.get('doc_mgm_access_group_ids') or vals.get('parent_id'):
            record.update_user_group_ids()
            record.set_parent_access()
        return record

    @api.multi
    def write(self, vals):
        res = super(Directory, self).write(vals)
        if vals.get('doc_mgm_access_group_ids') or vals.get('parent_id'):
            self.update_user_group_ids()
            self.set_parent_access()
        return res

Directory()

class File(base.DMSModel):
    _inherit = 'muk_dms.file'

    @api.multi
    def update_user_group_ids(self):
        self = self.sudo()
        for record in self:
            access_group_ids = []
            for line in record.doc_mgm_access_group_ids:
                access_group_ids.extend(line.access_group_ids.ids)
            access_group_ids = list(set(access_group_ids))
            user_ids = self.env['res.users'].search([('access_rights_id', 'in', access_group_ids)]).ids
            ### Update users ###
            # Clear old records
            self._cr.execute('DELETE FROM muk_dms_file_res_users_rel WHERE muk_dms_file_id=' + str(record.id))
            # Create new links
            for user_id in user_ids:
                self._cr.execute('INSERT INTO muk_dms_file_res_users_rel (muk_dms_file_id, res_users_id) VALUES (%s, %s)' % (record.id, user_id))
            ### Update groups ###
            # Clear old records
            self._cr.execute('DELETE FROM access_rights_group_muk_dms_file_rel WHERE muk_dms_file_id=' + str(record.id))
            # Create new links
            for access_group_id in access_group_ids:
                self._cr.execute('INSERT INTO access_rights_group_muk_dms_file_rel (muk_dms_file_id, access_rights_group_id) VALUES (%s, %s)' % (record.id, access_group_id))
            self._cr.commit()

    doc_mgm_access_group_ids = fields.One2many('document.mgm.access.rights', 'muk_file_id', 'File')
    user_ids = fields.Many2many('res.users', string='Users')
    access_group_ids = fields.Many2many('access.rights.group', string='Access Groups')
    file_perm_create = fields.Boolean(compute='_compute_file_perm_create', string="File Create")
    file_perm_read = fields.Boolean(compute='_compute_file_perm_read', string="File Read")
    file_perm_write = fields.Boolean(compute='_compute_file_perm_write', string="File Write")
    file_perm_unlink = fields.Boolean(compute='_compute_file_perm_unlink', string="File Delete")

    @api.one
    def _compute_file_perm_create(self):
        create_access_id = self.env['document.mgm.access.rights'].sudo().search(
            [('muk_file_id', '=', self.id), ('name', '=', 'Create')])
        if self.env.user.access_rights_id.id in create_access_id.access_group_ids.ids:
            self.file_perm_create = True
        else:
            self.file_perm_create = False

    @api.one
    def _compute_file_perm_read(self):
        read_access_id = self.env['document.mgm.access.rights'].sudo().search(
            [('muk_file_id', '=', self.id), ('name', '=', 'Read')])
        if self.env.user.access_rights_id.id in read_access_id.access_group_ids.ids:
            self.file_perm_read = True
        else:
            self.file_perm_read = False

    @api.one
    def _compute_file_perm_write(self):
        write_access_id = self.env['document.mgm.access.rights'].sudo().search(
            [('muk_file_id', '=', self.id), ('name', 'in', ['Edit(own)', 'Edit(other)'])])
        access_group_ids = sum([line.access_group_ids.ids for line in write_access_id], [])
        if self.env.user.access_rights_id.id in access_group_ids:
            self.file_perm_write = True
        else:
            self.file_perm_write = False

    @api.one
    def _compute_file_perm_unlink(self):
        unlink_access_id = self.env['document.mgm.access.rights'].sudo().search(
            [('muk_file_id', '=', self.id), ('name', 'in', ['Delete(own)', 'Delete(other)'])])
        access_group_ids = sum([line.access_group_ids.ids for line in unlink_access_id], [])
        if self.env.user.access_rights_id.id in access_group_ids:
            self.file_perm_unlink = True
        else:
            self.file_perm_unlink = False

    @api.model
    def default_get(self, fields):
        rec = super(File, self).default_get(fields)
        all_data = []
        if self.env.user.access_rights_id:
            all_data.append((0, 0, {'name': 'Create', 'access_group_ids': [(6, 0, [self.env.user.access_rights_id.id])]}))
            all_data.append((0, 0, {'name': 'Edit(own)', 'access_group_ids': [(6, 0, [self.env.user.access_rights_id.id])]}))
            all_data.append((0, 0, {'name': 'Edit(other)'}))
            all_data.append((0, 0, {'name': 'Read', 'access_group_ids': [(6, 0, [self.env.user.access_rights_id.id])]}))
            all_data.append((0, 0, {'name': 'Delete(own)', 'access_group_ids': [(6, 0, [self.env.user.access_rights_id.id])]}))
            all_data.append((0, 0, {'name': 'Delete(other)'}))
            rec['access_group_ids'] = [(6, 0, [self.env.user.access_rights_id.id])]
        else:
            all_data.append((0, 0, {'name': 'Create'}))
            all_data.append((0, 0, {'name': 'Edit(own)'}))
            all_data.append((0, 0, {'name': 'Edit(other)'}))
            all_data.append((0, 0, {'name': 'Read'}))
            all_data.append((0, 0, {'name': 'Delete(own)'}))
            all_data.append((0, 0, {'name': 'Delete(other)'}))
        rec['doc_mgm_access_group_ids'] = all_data
        rec['user_ids'] = [(6, 0, [self.env.user.id])]
        return rec

    @api.multi
    def set_parent_access(self):
        self = self.sudo()
        for record in self:
            access_rights_ids = list(set(sum([line.access_group_ids.ids for line in record.doc_mgm_access_group_ids], [])))
            parent_rec = record.directory
            while (parent_rec):
                for access_rights_id in access_rights_ids:
                    user_ids = self.env['res.users'].search([('access_rights_id', '=', access_rights_id)]).ids
                    ### Update Users ###
                    for user_id in user_ids:
                        self._cr.execute('SELECT * FROM muk_dms_directory_res_users_rel WHERE muk_dms_directory_id=%s AND res_users_id=%s' % (parent_rec.id, user_id))
                        if not self._cr.fetchall():
                            self._cr.execute('INSERT INTO muk_dms_directory_res_users_rel (muk_dms_directory_id, res_users_id) VALUES (%s, %s)' % (parent_rec.id, user_id))
                    ### Update Groups ###
                    self._cr.execute('SELECT * FROM access_rights_group_muk_dms_directory_rel WHERE muk_dms_directory_id=%s AND access_rights_group_id=%s' % (parent_rec.id, access_rights_id))
                    if not self._cr.fetchall():
                        self._cr.execute('INSERT INTO access_rights_group_muk_dms_directory_rel (muk_dms_directory_id, access_rights_group_id) VALUES (%s, %s)' % (parent_rec.id, access_rights_id))
                    self._cr.commit()
                parent_rec = parent_rec.parent_id
                if not parent_rec:
                    break
        return True

    @api.model
    def create(self, vals):
        record = super(File, self.sudo()).create(vals)
        if vals.get('doc_mgm_access_group_ids') or vals.get('directory'):
            record.update_user_group_ids()
            record.set_parent_access()
        return record

    @api.multi
    def write(self, vals):
        res = super(File, self).write(vals)
        if vals.get('doc_mgm_access_group_ids') or vals.get('directory'):
            self.update_user_group_ids()
            self.set_parent_access()
        return res

File()