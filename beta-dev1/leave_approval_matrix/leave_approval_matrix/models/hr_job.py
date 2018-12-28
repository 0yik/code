from odoo import models, fields, api

class hr_job(models.Model):
    _inherit = 'hr.job'

    approving_manager_id    = fields.Many2one('hr.job',string='Approving Manager',index=True,on_delete="restrict")
