# -*- coding: utf-8 -*-
from odoo import fields, models, exceptions, api, _
from odoo.exceptions import UserError

class AcademicYear(models.Model):
    _inherit = 'academic.year'
    
