# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (C) 2004-2012 OpenERP S.A. (<http://openerp.com>).
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

class hr_config_settings(models.TransientModel):
    _name = 'hr.config.settings'
    _inherit = 'res.config.settings'

    module_hr_timesheet_sheet = fields.Boolean('Allow timesheets validation by managers',
                                               help="""This installs the module hr_timesheet_sheet.""")
    module_hr_attendance = fields.Boolean('Install attendances feature',
                                          help="""This installs the module hr_attendance.""")
    module_hr_timesheet = fields.Boolean('Manage timesheets',
                                         help="""This installs the module hr_timesheet.""")
    module_hr_holidays = fields.Boolean('Manage holidays, leaves and allocation requests',
                                        help="""This installs the module hr_holidays.""")
    module_hr_expense = fields.Boolean('Manage employees expenses',
                                       help="""This installs the module hr_expense.""")
    module_hr_recruitment = fields.Boolean('Manage the recruitment process',
                                           help="""This installs the module hr_recruitment.""")
    module_hr_contract = fields.Boolean('Record contracts per employee',
                                        help="""This installs the module hr_contract.""")
    module_hr_evaluation = fields.Boolean('Organize employees periodic evaluation',
                                          help="""This installs the module hr_evaluation.""")
    module_hr_gamification = fields.Boolean('Drive engagement with challenges and badges',
                                            help="""This installs the module hr_gamification.""")
    module_account_analytic_analysis = fields.Boolean(
        'Allow invoicing based on timesheets (the sale application will be installed)',
        help="""This installs the module account_analytic_analysis, which will install sales management too.""")
    module_hr_payroll = fields.Boolean('Manage payroll',
                                       help="""This installs the module hr_payroll.""")

    def onchange_hr_timesheet(self, timesheet):
        """ module_hr_timesheet implies module_hr_attendance """
        if timesheet:
            return {'value': {'module_hr_attendance': True}}
        return {}

    def onchange_hr_attendance(self, attendance):
        """ module_hr_timesheet implies module_hr_attendance """
        if not attendance:
            return {'value': {'module_hr_timesheet': False}}
        return {}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
