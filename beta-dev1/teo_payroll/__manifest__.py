# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-Today Serpent Consulting Services Pvt. Ltd. (<http://serpentcs.com>).
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

{
    "name": "Teo Garments Payroll Reports",
    "version": "1.3",
    "depends": ["l10n_sg_hr_payroll"],
    'author': 'HashMicro/Satya',
    'website': 'www.hashmicro.com',
    "category": "Human Resources",
    "description": """
Payroll Reports.
=================

    * Department Payroll Report
    * Company Total Payroll Report
   
    """,
    'data': [
             'wizard/company_total_payroll_wizard_view.xml',
             'wizard/department_total_payroll_wizard_view.xml',
             'views/company_total_payroll_temp.xml',
             'views/dpt_total_payroll_temp.xml',
             'views/report_data.xml',
             'data/salary_rule.xml',
       
                ],
    'installable': True,
    'auto_install':False,
    'application':True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
