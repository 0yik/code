# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProjectProject(models.Model):
    _inherit = 'project.project'

    sub_contractor_ids = fields.Many2many(
        'res.partner',
        'sub_contractor_project_id',
        string="Sub Contractor"
    )
    notes_count = fields.Integer(
        compute='_compute_notes_count', 
        string="Notes",
        store=False,
    )

class Task(models.Model):
    _inherit = "project.task"

    @api.multi
    def _get_subtask_count(self):
        for task in self:
            task.subtask_count = len(task.child_task_ids)  

class JobCosting(models.Model):
    _inherit = 'job.costing'

    @api.onchange('project_id')
    def onchange_project_id(self):
        for obj in self:
            obj.update({'partner_id': obj.project_id.partner_id.id})
        return

class Product(models.Model):
    _inherit = 'product.product'

    boq_type = fields.Selection([
        ('eqp_machine', 'Machinery / Equipment'),
        ('worker_resource', 'Worker / Resource'),
        ('work_cost_package', 'Work Cost Package'),
        ('subcontract', 'Subcontract')], 
        string='BOQ Type', 
        help="This will be used in Material Request / BOQ while calculating total cost"
        " for each category/type of material/labour.",
    )

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    project_id = fields.Many2one(
        'project.project',
        string='Project',
    )