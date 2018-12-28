# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2017 Serpent Consulting Services Pvt. Ltd.
#    Copyright (C) 2017 OpenERP SA (<http://www.serpentcs.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#0
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api, tools


class AbsentHistory(models.Model):
    _name = "absent.history"

    company_id = fields.Many2one('res.company', 'Company')
    no_of_absent_emp = fields.Integer('No. of Absent Employee')
    date = fields.Date('Date')


class LateEmployeeHistory(models.Model):
    _name = "late.employee.history"

    company_id = fields.Many2one('res.company', 'Company')
    no_of_late_emp = fields.Integer('No. of Late Employee')
    date = fields.Date('Date')


class AverageAgeHistory(models.Model):
    _name = "average.age.history"

    company_id = fields.Many2one('res.company', 'Company')
    emp_avg_age = fields.Integer('Employee Average Age')
    date = fields.Date('Date')


class NewJoinHistory(models.Model):
    _name = "new.join.history"

    company_id = fields.Many2one('res.company', 'Company')
    no_of_join_emp = fields.Integer('No. of Newly Joined Employees')
    date = fields.Date('Date')


class NoticePeriodHistory(models.Model):
    _name = "notice.period.history"

    company_id = fields.Many2one('res.company', 'Company')
    no_of_notice_emp = fields.Integer('No. of Employees on Notice Period')
    date = fields.Date('Date')


class AbsentHistoryView(models.Model):
    _name = "absent.history.view"
    _description = "absenent history view"
    _auto = False

    company_id = fields.Many2one('res.company', 'Company')
    no_of_absent_emp = fields.Integer('No. of Absent Employee')
    date = fields.Date('Date')

    @api.model_cr
    def init(self):
        """
        A method to create the view of Absent History
        ---------------------------------------------
        @param self : object pointer
        """
        cr = self.env.cr
        tools.drop_view_if_exists(cr, 'absent_history_view')
        cr.execute("""
            create or replace view absent_history_view as (
            select id,date as date,
            company_id as company_id,
            no_of_absent_emp as no_of_absent_emp
            from absent_history
        )
        """)


class LateEmployeeHistoryView(models.Model):
    _name = "late.employee.history.view"
    _description = "Late Employee history view"
    _auto = False

    company_id = fields.Many2one('res.company', 'Company')
    no_of_late_emp = fields.Integer('No. of Late Employee')
    date = fields.Date('Date')

    @api.model_cr
    def init(self):
        """
        A method to create the view of Late Employee History
        ----------------------------------------------------
        @param self : object pointer
        """
        cr = self.env.cr
        tools.drop_view_if_exists(cr, 'late_employee_history_view')
        cr.execute("""
            create or replace view late_employee_history_view as (
            select id,date as date,
            company_id as company_id,
            no_of_late_emp as no_of_late_emp
            from late_employee_history
        )
        """)


class AverageAgeHistoryView(models.Model):
    _name = "average.age.history.view"
    _description = "Average age history view"
    _auto = False

    company_id = fields.Many2one('res.company', 'Company')
    emp_avg_age = fields.Integer('Employee Average Age')
    date = fields.Date('Date')

    @api.model_cr
    def init(self):
        """
        A method to create the view of Average Age History
        --------------------------------------------------
        @param self : object pointer
        """
        cr = self.env.cr
        tools.drop_view_if_exists(cr, 'average_age_history_view')
        cr.execute("""
            create or replace view average_age_history_view as (
            select id,date as date,
            company_id as company_id,
            emp_avg_age as emp_avg_age
            from average_age_history
        )
        """)


class NewJoinHistoryView(models.Model):
    _name = "new.join.history.view"
    _description = "new join history view"
    _auto = False

    company_id = fields.Many2one('res.company', 'Company')
    no_of_join_emp = fields.Integer('No. of Newly Joined Employees')
    date = fields.Date('Date')

    @api.model_cr
    def init(self):
        """
        A method to create the view of New Joining History
        --------------------------------------------------
        @param self : object pointer
        """
        cr = self.env.cr
        tools.drop_view_if_exists(cr, 'new_join_history_view')
        cr.execute("""
            create or replace view new_join_history_view as (
            select id,date as date,
            company_id as company_id,
            no_of_join_emp as no_of_join_emp
            from new_join_history
        )
        """)


class NoticePeriodHistoryView(models.Model):
    _name = "notice.period.history.view"
    _description = "Notice Period History View"
    _auto = False

    company_id = fields.Many2one('res.company', 'Company')
    no_of_notice_emp = fields.Integer('No. of Employees on Notice Period')
    date = fields.Date('Date')

    @api.model_cr
    def init(self):
        """
        A method to create the view of Notice Period History
        ----------------------------------------------------
        @param self : object pointer
        """
        cr = self.env.cr
        tools.drop_view_if_exists(cr, 'notice_period_history_view')
        cr.execute("""
            create or replace view notice_period_history_view as (
            select id,date as date,
            company_id as company_id,
            no_of_notice_emp as no_of_notice_emp
            from notice_period_history
        )
        """)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
