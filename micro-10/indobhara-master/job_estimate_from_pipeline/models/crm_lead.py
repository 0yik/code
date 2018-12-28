from odoo import fields,models,api,_

class SaleestimateIinherit(models.Model):
    
    _inherit = "sale.estimate.job"
    
    lead_id = fields.Many2one('crm.lead',string="Lead")
    
class CrmLead(models.Model):
    
    _inherit = 'crm.lead'
    
    @api.multi
    def jobcost_count(self):
        for lead in self:
            job_ids = self.env['sale.estimate.job'].search([('lead_id','=',lead.id)])
            lead.job_cost_count = len(job_ids)
        
    job_cost_count = fields.Integer(compute='jobcost_count',string="Job Costs")