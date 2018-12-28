from odoo import models, fields, api
from odoo import SUPERUSER_ID

class hr_employee(models.Model):
    _inherit = 'hr.employee'

    commission = fields.Float(string="Commission (%)")
