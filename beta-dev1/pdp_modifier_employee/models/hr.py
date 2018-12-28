from odoo import api, fields, models

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    address_home = fields.Text(string='Home Address')
