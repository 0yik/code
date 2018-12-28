from odoo import api, fields, models

class Applicant(models.Model):
    _inherit = "hr.applicant"

    family_member_of_employee = fields.Boolean(string="Family Member of Employee", default=False)
    name_of_emlpyee = fields.Char(string='Name of Employee')
    relationship = fields.Char(string="Applicant-Employee Relationship")

    @api.model
    def create(self, vals):
        applicant = super(Applicant, self).create(vals)
        dependent = self.env['dependents'].search([('identification_number', '=', applicant.identification_no)])
        if dependent:
            applicant.family_member_of_employee = True
            applicant.name_of_emlpyee = dependent[0].employee_id.name
            applicant.relationship = dependent[0].relation_ship
        return applicant