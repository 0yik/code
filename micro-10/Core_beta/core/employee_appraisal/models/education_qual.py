# -*- coding: utf-8 -*- 
from odoo import fields,models,api

class EducationQualification(models.Model):
    _name = "education.qualification"

    qual_seq = fields.Char(string="Qual Seq")
    name = fields.Char(string="Degree Name",required=True)
    active = fields.Boolean(string="Active", default=True)
    note = fields.Text(string="Description")

    _sql_constraints = [('name_uniq','unique(name)','The qualification name must be unique.')]


    @api.model
    def create(self,vals):
        ''' Method overridden to generate the sequence number. '''
        vals['qual_seq'] = self.env['ir.sequence'].next_by_code('education.qualification') or '/'
        return super(EducationQualification, self).create(vals)


