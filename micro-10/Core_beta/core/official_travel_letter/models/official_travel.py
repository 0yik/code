# -*- coding: utf-8 -*-

from odoo import models,api,_,fields
from datetime import date
from odoo.exceptions import Warning

class official_travel(models.Model):
    
    _name = "official.travel"
    
    employee_id = fields.Many2one("hr.employee",string="Employee",domain=[('user_id','!=',False)])
    from_date = fields.Date("Travel from date")
    to_date = fields.Date("Travel to date")
    job_id = fields.Many2one(related="employee_id.job_id", string='Job')
    department_id = fields.Many2one(related="employee_id.department_id", string='Department')
    name = fields.Char("Letter Number")
    company_id = fields.Many2one("res.company",string="Travel To")
    job_desc_ids = fields.One2many("travel.job.details",'travel_id',string="Job Des")
    state = fields.Selection([('draft','Draft'),('confirm','Confirmed')],default="draft")
    send_date = fields.Date("Send Date")
    
    _sql_constraints = [
        ('date_check', "CHECK ( from_date < to_date )", "The start date must be anterior to the end date."),
        ]
    
    @api.multi
    def confirm(self):
        for rec in self:
            next_letter = self.env['ir.sequence'].next_by_code('official.travel')
            self.name = next_letter
            rec.state = 'confirm'
            self.send_date = date.today()
            official_template = self.env['mail.template'].search([('name','=','Official Travel')])
            ans = official_template.send_mail(self.id)
            return True
    
    @api.multi
    def copy(self,default=None):
        self.ensure_one()
        context = dict(self._context)
        default = default or {}
        default['name'] = ''
        res = super(official_travel,self).copy(default=default)
        return res
    
    @api.multi
    def unlink(self):
        for letter in self:
            if letter.state == 'confirm':
                raise Warning(_("You can not delete confirmed letter!"))
        return super(official_travel, self.sudo()).unlink()
    
    def print_letter(self):
        return self.env['report'].get_action(self, 'official_travel.report_travel')
        
class travel_job_details(models.Model):
    
    _name = "travel.job.details"
    
    name = fields.Char("Job Detail")
    travel_id = fields.Many2one("official.travel")