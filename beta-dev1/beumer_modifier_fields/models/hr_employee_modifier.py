from odoo import fields, models, api, exceptions

class hr_employee_race(models.Model):
    _name = "hr.employee.race"

    name = fields.Char(string="Employee Race", required=True)

class hr_employee_religion(models.Model):
    _name = "hr.employee.religion"

    name = fields.Char(string="Employee Religion", required=True)

class hr_employee_qualification(models.Model):
    _name = "hr.employee.qualification"

    name = fields.Char(string="Employee Qualification", required=True)
