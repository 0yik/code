from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

