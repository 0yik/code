# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SchoolStandard(models.Model):
    _inherit = 'school.standard'

    application_fee_structure_id = fields.Many2one('student.fees.structure', 'Application Fee Structure')
    is_from_course = fields.Boolean('Is Application Fees Structure')

    @api.onchange('application_fee_structure_id')
    def onchange_application_fee_structure_id(self):
    	if self.application_fee_structure_id:
    		self.is_from_course = True
    	else:
    		self.is_from_course = False
