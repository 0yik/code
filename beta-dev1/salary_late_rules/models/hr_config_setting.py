# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-Today MpTechnolabs.
#    
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import fields, models

class hr_employee_configuration(models.TransientModel):
    _inherit = 'hr.employee.config.settings'
    
    module_sg_document_expiry = fields.Boolean(string="Manage Expiry Document Details With Report",
                                               help="This help to send mail for document expiry with report")
    late_minutes_buffer = fields.Integer(string="Late Minutes Buffer")
    late_entry_fee_type = fields.Selection([('auto','Auto'),('fixed','Fixed')], string="Late Entry Type")
    late_entry_deduction = fields.Integer('Late Entry Deduction')
    absence_fee_type = fields.Selection([('auto','Auto'),('fixed','Fixed')], string="Absence Fee Type")
    absence_fee_deduction = fields.Integer('Absence Fee Deduction')