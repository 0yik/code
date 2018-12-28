# coding: utf-8

from odoo import api, fields, models
from odoo import api, fields, models, tools, _

class job_checklist(models.Model):
    _name = 'job.checklist'

    name = fields.Char('Job Checklist Name', required=1)
    active = fields.Boolean('Active', default=True)
    check_list_description_ids = fields.One2many('job.checklist.description', 'job_checklist_id')

class job_checklist_description(models.Model):
    _name = 'job.checklist.description'

    name = fields.Text('Description')
    job_checklist_id = fields.Many2one('job.checklist')

class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    job_checklist_id = fields.Many2one('job.checklist', 'Job Checklist')

    def get_job_order_vals(self):
        vals = super(MaintenanceRequest, self).get_job_order_vals()
        vals.update({
            'job_checklist_id': self.job_checklist_id and self.job_checklist_id.id or False,
        })
        return vals

class JobOrder(models.Model):
    _inherit = 'job.order'

    job_checklist_id = fields.Many2one('job.checklist', 'Job Checklist')
    job_order_checklist_ids = fields.One2many('job.order.checklist', 'job_order_id')

    @api.onchange('maintenance_id')
    def onchange_maintenance_id(self):
        if self.maintenance_id:
            super(JobOrder, self).onchange_maintenance_id()
            self.job_checklist_id = self.maintenance_id.job_checklist_id


    @api.model
    def create(self,vals):
        res = super(JobOrder, self).create(vals)
        if res.job_checklist_id:
            res.onchange_job_checklist()
        return res

    @api.onchange('job_checklist_id')
    def onchange_job_checklist(self):
        self.job_order_checklist_ids = ''
        if self.job_checklist_id:
            JobOrderChecklist = self.env['job.order.checklist'].browse([])
            for line in self.job_checklist_id.check_list_description_ids:
                JobOrderChecklist += JobOrderChecklist.new({
                    'name' : line.name,
                })
            self.job_order_checklist_ids = JobOrderChecklist

class JobOrderChecklist(models.Model):
    _name = 'job.order.checklist'

    name = fields.Text('Description')
    done = fields.Boolean('Done')
    job_order_id = fields.Many2one('job.order')
    remark = fields.Text('Remark')
    checked_by = fields.Many2one('hr.employee', domain=False)




class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        ctx = self._context
        if 'maintenance_id' in ctx:
            team = self.env['maintenance.request'].browse(ctx.get('maintenance_id'))
            ids = team.employee_ids.ids
            args+= [('id', 'in', ids)]
        recs = self.search([('name', operator, name)]+args, limit=limit)
        return recs.name_get()
