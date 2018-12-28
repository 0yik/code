# -*- coding: utf-8 -*-

from odoo import fields,api,_,models

class request_price(models.Model):
    
    _name = "request.price"
    
    @api.multi
    def jobcost_count(self):
        for estimate in self:
            job_ids = self.env['sale.estimate.job'].search([('request_id','=',estimate.id)])
            estimate.job_cost_count = len(job_ids)
            
    name = fields.Char("Reference No")
    company_id = fields.Many2one("res.company",string="Company")
    salesman_id = fields.Many2one("res.users",string="Salesman")
    project_id = fields.Many2one("project.project",string="Project")
    partner_id = fields.Many2one("res.partner",string="Customer",domain=[('customer','=',True)])
    approver_id = fields.Many2one("res.users",string="Approver")
    location = fields.Char("Project Location")
    desc = fields.Char('Description')
    state = fields.Selection([('draft','Draft'),('request_appove','Request for Approval'),
                              ('approve','Approved')],default="draft")
    job_cost_count = fields.Integer(compute='jobcost_count',string="Job Costs")
    
    @api.multi
    def request_for_approval(self):
        for rec in self:
            rec.state = 'request_appove'
    
    @api.multi
    def approved(self):
        for rec in self:
            rec.state = "approve"
        
    @api.multi
    def reset_to_draft(self):
        for rec in self:
            rec.state = "draft"
            
class SaleestimateIinherit(models.Model):
    
    _inherit = "sale.estimate.job"
    
    request_id = fields.Many2one('request.price',string="Request Price")
