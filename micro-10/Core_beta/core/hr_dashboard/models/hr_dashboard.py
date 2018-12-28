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
import pytz
from datetime import datetime

from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, \
    DEFAULT_SERVER_DATETIME_FORMAT
from odoo import models, fields, api


class HRDashboard(models.Model):
    _name = 'hr.dashboard'
    _description = "HR Dashboard"

    name = fields.Char("Name")

    @api.model
    def get_hr_dashboard_details(self):
        emp_obj = self.env['hr.employee']
        cr = self.env.cr
        user = self.env.user
        data = {'bday': [],
                'aday': [],
                }

        # GET THE CURRENT DATE WITH TIMEZONE.
#        tz = "Asia/Riyadh"
        tz = "Singapore"
        cur_date = datetime.now()
        local_tz = pytz.timezone(user.tz or tz)
        local_dt = cur_date.replace(tzinfo = pytz.utc
                                         ).astimezone(local_tz)
        date = str(cur_date.month)
        dt_str = date.zfill(2)

        suf = lambda n: "%d%s" % (n,
                                 {1: "st",
                                   2: "nd",
                                   3: "rd"
                                 }.get(n if n < 20 else n % 10, "th"))
        # GET MONTH NAME
        month_date = datetime.strftime(local_dt, "%B-%Y")
        data.update({
            'month_date': month_date,
        })
        # FETCH BIRTHDAYS OF EMPLOYEES OF THE CURRENT MONTH
        cr.execute("select id from hr_employee where resource_id in \
                    (select id from resource_resource where active IS TRUE) \
                    and TO_CHAR(birthday, 'mm') = %s ",
                             (dt_str,))
        birthday_ids = cr.fetchall()
        if birthday_ids:
            bday_emps = [bday_emp[0] for bday_emp in birthday_ids]
            data.update({
                'bday_details': bday_emps
            })
            for day in emp_obj.browse(bday_emps[:6]):
                image = '/hr_dashboard/static/src/img/avatar.png'
                if day.image:
                    image = "data:image/gif;base64," + day.image
                if day.birthday:
                    bday_date1 = datetime.strptime(day.birthday,
                                                DEFAULT_SERVER_DATE_FORMAT)
                    bday_date2 = datetime.strftime(bday_date1, "%m/%d/%Y")
                    data['bday'].append({
                          'ID': day.id,
                          'Name': day.name_related,
                          'birthday': bday_date2,
                          'age': day.age,
                          'Img': image
                    })

        # Fetch Work Anniversaries of Employees of the Current Month
        cr.execute("select id from hr_employee where resource_id in \
                    (select id from resource_resource where active IS TRUE) \
                    and TO_CHAR(join_date, 'mm') = %s \
                            and anniversary >= 1",
                             (dt_str,))
        anniversary_ids = cr.fetchall()
        if anniversary_ids:
            ann_emps = [ann_emp[0] for ann_emp in anniversary_ids]
            data.update({
                'aday_details': ann_emps
            })
            for day in emp_obj.browse(ann_emps[:6]):
                image = '/hr_dashboard/static/src/img/avatar.png'
                if day.image:
                    image = "data:image/gif;base64," + day.image
                if day.join_date:
                    join_date1 = datetime.strptime(day.join_date,
                                                DEFAULT_SERVER_DATE_FORMAT)
                    join_date = datetime.strftime(join_date1.date(),
                                                  "%m/%d/%Y")
                    data['aday'].append({
                                          'ID': day.id,
                                          'Name': day.name_related,
                                          'join_date': join_date,
                                          'anniversary': suf(day.anniversary),
                                          'Img': image})

        # Get Company's Average Age
        avrage_age_emp = user.company_id.a_age
        data.update({
            'comp_avg_age': avrage_age_emp,
        })

        # Fetch all the Employees
        cr.execute('select count(id) from hr_employee where resource_id in \
        (select id from resource_resource where active=True)')
        res = cr.fetchone()
        total_emps = res and res[0]
        data.update({
            'total_emp': total_emps,
        })

        # Fetch Current Recruitments
        cr.execute("select sum(no_of_employee),sum(no_of_recruitment) \
        from hr_job where state='recruit'")
        res = cr.fetchone()
        recruit_emps, recruit_jobs = res
        if recruit_jobs and recruit_emps:
            open_recruits = recruit_jobs - recruit_emps
            data.update({
                'emp_recruit': open_recruits,
                'emp_recruit_perc': (recruit_emps * 100) / recruit_jobs
            })

        # Fetch New Employees
        cr.execute("select count(id) from hr_employee where resource_id in \
        (select id from resource_resource where active=True) and \
        join_date=now()")
        res = cr.fetchone()
        join_emps = res and res[0]
        data.update({
            'join_emp_len': join_emps,
            'join_emp_perc': (join_emps * 100) / total_emps,
        })

        # Fetch Employees in Notice Period
        cr.execute("select count(id) from hr_employee where resource_id in \
        (select id from resource_resource where active=True) and \
        emp_status='in_notice'")
        res = cr.fetchone()
        notice_emp_len = res and res[0]
        data.update({
            'notice_emp_len': notice_emp_len,
            'notice_emp_perc': (notice_emp_len * 100) / total_emps,
        })

        # Fetch Employees in Probation
        cr.execute("select count(id) from hr_employee where resource_id in \
        (select id from resource_resource where active=True) and \
        emp_status='probation'")
        res = cr.fetchone()
        probation_emp_len = res and res[0]
        data.update({
            'probation_emp_len': probation_emp_len,
            'probation_emp_perc': (probation_emp_len * 100) / total_emps,
        })

        # Fetch the leaves of Today.
        db_format_dt = cur_date.strftime('%Y-%m-%d %H:%M:%S')
        cr.execute("select id from hr_holidays where type='remove' \
        and '%s' between date_from and date_to \
        and state not in ('refuse','cancel')" % (db_format_dt,))
        res = cr.fetchall()
        leave = res
        emp_on_leave = len(leave)
        data.update({
            'on_leave_emp': leave,
            'emp_on_leave': emp_on_leave,
            'emp_on_leave_perc': (emp_on_leave * 100) / total_emps,
        })

        # Fetch the Absent Employees
        now_str = datetime.strftime(cur_date, "%Y-%m-%d")
        cr.execute("select id from hr_employee where \
                    resource_id in \
                    (select id from resource_resource where active IS TRUE) \
                    and id not in \
                    (select employee_id from hr_attendance where \
                    TO_CHAR(check_in, 'yyyy-mm-dd') = %s )",
                    (now_str,))
        res = cr.fetchall()
        absent_emps = [emp[0] for emp in res]
        absent_emp_len = len(absent_emps)
        data.update({
            'absent_emp': absent_emps,
            'absent_emp_len': absent_emp_len,
            'absent_emp_perc': (absent_emp_len * 100) / total_emps,
        })

        # Fetch the Late Employees
        cr.execute("select id from hr_attendance where \
                    TO_CHAR(check_in, 'yyyy-mm-dd') = %s \
                    and checkin_status = 'late' ",
                    (now_str,))
        res = cr.fetchall()
        late_emps = [emp[0] for emp in res]
        late_emp_len = len(late_emps)
        data.update({
            'late_emp_id': late_emps,
            'late_emp_len': late_emp_len,
            'late_emp_perc': (late_emp_len * 100) / total_emps,
        })
        return data

    @api.model
    def create_dashboard_history(self):
        cr = self.env.cr
        cur_date = datetime.now().date()
        ab_history_obj = self.env['absent.history']
        late_emp_history_obj = self.env['late.employee.history']
        avg_age_history_obj = self.env['average.age.history']
        new_join_history_obj = self.env['new.join.history']
        notice_period_history_obj = self.env['notice.period.history']

        # Generate Absent History
        cur_date_str = datetime.strftime(cur_date, "%Y-%m-%d")
        cr.execute("select id from hr_employee where \
                    resource_id in \
                    (select id from resource_resource where active IS TRUE) \
                    and id not in \
                    (select employee_id from hr_attendance where \
                    TO_CHAR(check_in, 'yyyy-mm-dd') = %s )",
                    (cur_date_str,))
        absent_result = cr.fetchall()
        uid = self.env['res.users'].browse(self.env.uid)
        ab_vals = {
                  'no_of_absent_emp': len(absent_result),
                  'company_id': uid.company_id.id,
                  'date': cur_date,
                  }
        ab_history_obj.create(ab_vals)

        # Generate Late Employee History
        cr.execute("select count(id) from hr_attendance where \
                    TO_CHAR(check_in, 'yyyy-mm-dd') = %s \
                    and checkin_status = 'late' ",
                    (cur_date_str,))
        res = cr.fetchone()
        no_of_late_emp = res and res[0] or 0

        late_emp_vals = {
                  'no_of_late_emp': no_of_late_emp,
                  'company_id': uid.company_id.id,
                  'date': cur_date,
                  }
        late_emp_history_obj.create(late_emp_vals)

        # Generate Average Age History
        avrage_age_emp = uid.company_id.a_age
        avg_age_vals = {
                  'emp_avg_age': avrage_age_emp,
                  'company_id': uid.company_id.id,
                  'date': cur_date,
                  }
        avg_age_history_obj.create(avg_age_vals)

        # Generate Joining History
        cr.execute("select count(id) from hr_employee where resource_id in \
        (select id from resource_resource where active=True) and \
        join_date=now()")
        res = cr.fetchone()
        no_of_join_emp = res and res[0]

        join_vals = {
                  'no_of_join_emp': no_of_join_emp,
                  'company_id': uid.company_id.id,
                  'date': cur_date,
                  }
        new_join_history_obj.create(join_vals)

        # Generate Notice Period
        cr.execute("select count(id) from hr_employee where resource_id in \
        (select id from resource_resource where active=True) and \
        emp_status='in_notice'")
        res = cr.fetchone()
        no_of_notice_emp = res and res[0]

        notice_vals = {
                  'no_of_notice_emp': no_of_notice_emp,
                  'company_id': uid.company_id.id,
                  'date': cur_date,
                  }
        notice_period_history_obj.create(notice_vals)
