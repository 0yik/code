# -*- coding: utf-8 -*-

from odoo import api, fields, models,_,SUPERUSER_ID
from odoo.exceptions import Warning as UserWarning

class JobOrderStages(models.Model):
    _name = 'job.order.stages'
    _order = 'sequence, id'

    name = fields.Char('Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=20)
    fold = fields.Boolean('Folded in Maintenance Pipe')
    final_state = fields.Boolean('Final Stage')
    is_in_progress = fields.Boolean('In Progress')

    @api.model
    def create(self, vals):
        res = super(JobOrderStages, self).create(vals)
        if res:
            if len(self.search([('final_state', '=', True)])) > 1:
                raise UserWarning(
                    _("Just only one Job Order Stages with Final Stage = TRUE"))
        return res

    @api.multi
    def write(self, vals):
        res = super(JobOrderStages, self).write(vals)
        if res:
            for rec in self:
                if len(rec.search([('final_state', '=', True)])) > 1:
                    raise UserWarning(
                        _("Just only one Job Order Stages with Final Stage = TRUE"))
                if 'is_in_progress' in vals:
                    if vals['is_in_progress']:
                        job_orders = self.env['job.order'].search([('status_id','=',rec.id)])
                        for job in job_orders:
                            job.number = self.env['ir.sequence'].next_by_code('job.order')
                            mr_state = self.env['maintenance.stage'].search([('is_in_progress','=',True)],limit=1)
                            if mr_state:
                                job.maintenance_id.stage_id = mr_state
        return res

class JobOrder(models.Model):
    _name = 'job.order'

    @api.returns('self')
    def _default_stage(self):
        return self.env['job.order.stages'].search([], limit=1)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        res = super(JobOrder, self).read_group(domain, fields, groupby, offset, limit=limit,
                                                                 orderby=orderby, lazy=lazy)
        if groupby and groupby[0]=='status_id':
            for line in res:
                status_id = line['status_id']
                if self.env['job.order.stages'].browse(status_id[0]).fold:
                    line.update({
                        '__fold' : True,
                    })
                else:
                    line.update({
                        '__fold': False,
                    })

        return res

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """ Read group customization in order to display all the stages in the
            kanban view, even if they are empty
        """
        stage_ids = stages._search([], order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    name = fields.Char('Subject',required=True)
    requested_by = fields.Many2one('res.users', string="Requested By", default=lambda self: self.env.user)
    team_id = fields.Many2one('maintenance.team', "Team")
    responsible_id = fields.Many2one('res.users', string="Responsible")
    equipment_id = fields.Many2one('maintenance.equipment', 'Facility')
    request_date = fields.Date('Requested Date')
    maintenance_id = fields.Many2one('maintenance.request','Maintenance Request')
    status_id = fields.Many2one('job.order.stages', 'Status',default=_default_stage,group_expand='_read_group_stage_ids')
    location_id = fields.Many2one('location')
    number = fields.Char('Number')

    @api.onchange('location_id')
    def ochange_location_id(self):
        if not self.location_id:
            return {
                'domain':{
                    'equipment_id' : [('id','in',[])]
                }
            }
        else:
            return {
                'domain': {
                    'equipment_id': [('id', 'in', self.env['maintenance.equipment'].search([('location_id','=',self.location_id.id)]).ids)]
                }
            }

    @api.onchange('maintenance_id')
    def onchange_maintenance_id(self):
        if self.maintenance_id:
            self.team_id=self.maintenance_id.maintenance_team_id
            self.responsible_id=self.maintenance_id.technician_user_id
            self.location_id=self.maintenance_id.location_id
            self.equipment_id=self.maintenance_id.equipment_id
            self.request_date=self.maintenance_id.request_date

    @api.multi
    def write(self,vals):
        res = super(JobOrder, self).write(vals)
        if 'status_id' in vals:
            if self.status_id:
                if self.status_id.final_state:
                    mr = self.maintenance_id
                    if all([line.status_id.final_state for line in mr.job_order_ids]):
                        mr_approve_state = self.env['maintenance.stage'].search([('approval_state','=',True)])
                        if mr_approve_state:
                            mr.stage_id = mr_approve_state
                if self.status_id.is_in_progress:
                    mr_state = self.env['maintenance.stage'].search([('is_in_progress', '=', True)], limit=1)
                    if mr_state:
                        self.maintenance_id.stage_id = mr_state
                    self.number = self.env['ir.sequence'].next_by_code('job.order')
        return res


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    job_order_count = fields.Integer('#Job Order', compute='compute_job_order_count')
    job_order_ids = fields.One2many('job.order','maintenance_id')

    @api.depends('job_order_ids')
    @api.multi
    def compute_job_order_count(self):
        for rec in self:
            rec.job_order_count = len(rec.job_order_ids)

    def get_job_order_vals(self):
        return {
                'name' : self.name,
                'team_id' :  self.maintenance_team_id and self.maintenance_team_id.id or False,
                'responsible_id' : self.technician_user_id and self.technician_user_id.id or False ,
                'equipment_id' : self.equipment_id and self.equipment_id.id or False ,
                'request_date' : self.request_date,
                'maintenance_id' : self.id ,
                'location_id' : self.location_id and self.location_id.id or False ,
            }
    @api.model
    def create(self,vals):
        res = super(MaintenanceRequest, self).create(vals)
        if res:
            job_order_vales = res.get_job_order_vals()
            self.env['job.order'].create(job_order_vales)
        return res

    @api.multi
    def action_view_job_order(self):
        if self.job_order_count > 1:
            return {
                'name': _('Job Order'),
                'view_mode': 'kanban,tree,form',
                'view_type': 'form',
                # 'view_id': self.env.ref('maintenance_job_order.job_order_view_kanban').id,
                'res_model': 'job.order',
                'type': 'ir.actions.act_window',
                'domain' : [('id','in',self.job_order_ids.ids)]
            }
        else:
            return {
                'name': _('Job Order'),
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': self.env.ref('maintenance_job_order.job_order_view_form').id,
                'res_model': 'job.order',
                'type': 'ir.actions.act_window',
                'res_id' : self.job_order_ids[0].id
            }

class MaintenanceStage(models.Model):
    _inherit = 'maintenance.stage'

    approval_state = fields.Boolean('Approval Stage')

    @api.model
    def create(self, vals):
        res = super(MaintenanceStage, self).create(vals)
        if res:
            if len(self.search([('approval_state','=',True)])) > 1 :
                raise UserWarning(
                _("Just only one Maintenance Stages with Approval Stage = TRUE"))
        return res
    @api.multi
    def write(self, vals):
        res = super(MaintenanceStage, self).write(vals)
        if res:
            for rec in self:
                if len(rec.search([('approval_state', '=', True)])) > 1:
                    raise UserWarning(
                        _("Just only one Maintenance Stages with Approval Stage = TRUE"))
        return res