import pytz
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, \
DEFAULT_SERVER_DATE_FORMAT
import calendar
#from odoo.exceptions import ValidationError
from odoo.exceptions import UserError, ValidationError
import datetime as dt
from datetime import timedelta
import base64

class Emp_attendance_report(models.Model):
    _name="emp.report_part"
    
    @api.model
    def create(self, values):
        
        att = self.env['hr.attendance']
        if values['file_txt']:
            data_file = []
            new_id = super(Emp_attendance_report, self).create(values)
            data_file = values['file_txt']
            data_file = base64.b64decode(data_file)
            # out=data_file.readlines()
            list_of_items = data_file.split("\n")
            while True:
                try:
                    list_of_items.remove("")
                except:
                    break
            empty=[]
            x=True
            if x==True:
                for line in list_of_items:
                    val='-'.join([line[2:6],line[6:8],line[8:10]])
                    empty.append(val)

                d_time=[]
                for line in list_of_items:
                    value=':'.join([line[11:12],line[12:14]])
                    d_time.append(value)
                
                test_complete_date=[]
                for i in empty:
                    for j in d_time:
                        kd=i+' '+j
                        test_complete_date.append(kd)


                for items in test_complete_date:
                    items=dt.datetime.strptime(items,'%Y-%m-%d %H:%M')
                emp_id=[]
                for line in list_of_items:
                    emp= ','.join([line[24:28]])
                    emp=int(emp)
                    emp_id.append(emp)
                temp=[]
                att = self.env['hr.employee'].search([])  
                print "-----------len----",len(att)
                for k in att:
                    for ids in list_of_items: 

                    
                        k.emp_id =str(k.emp_id)
                        if k.emp_id in ids:
                            print "---",k.emp_id,k.id,k.name
                            
                            current_line=ids
                            temp.append(ids)
                            # for no_date in range(len(temp)):
                            if len(temp) > 1:
                                temp=sorted(temp,key=int)
                                
                                temp_start_date=temp[0]
                                temp_end_date=temp[-1]
                                
                                
                                date_line = '-'.join([temp_start_date[2:6],temp_start_date[6:8],temp_start_date[8:10]])
                                time_line1 = '.'.join([temp_start_date[10:12],temp_start_date[12:14]])
                                time_line = ':'.join([temp_start_date[10:12],temp_start_date[12:14],'00'])
                                start_date_time = date_line+ " "+time_line
                                # start_date_time=dt.datetime.strptime(start_date_time,'%Y-%m-%d %H:%M:%S')
                                date_line_end = '-'.join([temp_end_date[2:6],temp_end_date[6:8],temp_end_date[8:10]])
                                time_line_end1 = '.'.join([temp_end_date[10:12],temp_end_date[12:14]])
                                time_line_end = ':'.join([temp_end_date[10:12],temp_end_date[12:14],'00'])
                                end_date_time = date_line_end+ " "+time_line_end
                                # end_date_time=dt.datetime.strptime(end_date_time,'%Y-%m-%d %H:%M:%S')


                                print "start_date_time  ",start_date_time
                                print "end_date_time   ",end_date_time
                                if k.id != 1: 
                                    self.env['hr.contract']
                                    values = {
                                    'employee_id' : k.id,
                                    'check_in' : start_date_time,
                                    'check_out' : end_date_time,
                                    'date_dt':date_line,
                                    'o_timein':time_line1,
                                    'o_timeout':time_line_end1,
                                    'adj_timein':time_line1,
                                    'adj_timeout':time_line_end1,
                                    }
                                    print "//       ***         **  ----        ",values

                                    new_id = self.env['hr.attendance'].create(values)
                                list_of_items.remove(ids)
                                # for date in temp:
                                #     date_line = '-'.join([date[2:6],date[6:8],date[8:10]])
                                #     time_line = ':'.join([ids[11:12],ids[12:14],'00'])
                                #     date_time = date_line+ " "+time_line
                    print "temporary ",temp,len(temp)
                
                    # err    
                                # err



                # values = {}
                # temp = []
                # date_only=[]
                # empty_val=[]
                # date_time=[]
                # full_date=[]
                # get_ids=[]
                # test = []
                # for i in emp_id:
                #     for j in att:
                #         for k in self.env['hr.employee'].browse(j.id):
                #             ik=str(i)
                #             if ik == k.emp_id:
                #                 # values = {'employee_id':k.emp_id} 
                #                 ii=str(i)
                #                 for ids in list_of_items: 
                #                     # print "ids[24:28]               ",ids[24:28],type(ids[24:28]),ii,type(ii)
                                    
                #                     if ii == ids[24:28]:
                #                         temp.append(ids)
                #                         val1='-'.join([ids[2:6],ids[6:8],ids[8:10]])
                #                         empty_val.append(val)
                #                         val2=':'.join([ids[11:12],ids[12:14],'00'])
                #                         date_time.append(val2)
                #                         list_of_items.remove(ids)
                #                         emp_id.remove(i)

                #                         # for ij in empty_val:
                #                         #     for jk in date_time:
                #                         #         kd=ij+' '+jk
                #                         #         full_date.append(kd)
                #                         for list_vals in full_date:
                #                             item=dt.datetime.strptime(list_vals,'%Y-%m-%d %H:%M:%S')
                #                             item=item+timedelta(hours=9)
                #                             values = {
                #                             'check_in':list_vals,
                #                             'employee_id':k.id,
                #                             'state':'draft',
                #                             }


                #                         print "--****--",empty_val
                #                         print "\n\n\n\n\n/*/*/*/*/*/*/*",date_time
                #                         print "\n\n\n*/*/*/**+*+*+*+*+*+*+*+*+",temp
                #                         # err
                #                         # list_of_items.remove(ids)
                #                         # emp_id.remove(i)
                #                         # new_id = self.env['hr.attendance'].create(values)

                #                             #     print "item",item
                #                         # err
                #                         # for line in temp:
                #                         #     val='-'.join([line[2:6],line[6:8],line[8:10]])
                #                         #     empty_val.append(val)
                #                         # print "empty        _____   ",empty_val
                #                         # err
                #                         # for line in temp:
                #                         #     value=':'.join([line[11:12],line[12:14]])
                #                         #     date_time.append(value)
                #                         # for i in temp:
                #                         #     for j in date_time:
                #                         #         kd=i+' '+j
                #                         #         full_date.append(kd)
                #                         # for item in full_date:
                #                         #     item=dt.datetime.strptime(item,'%Y-%m-%d %H:%M')
                #                         #     print "item",item
            else:
                print ("Already Executed")

        # err            
        return new_id

    @api.onchange('employee_id','start_date','end_date')
    def on_change_employee(self):
        val={}
        if self.employee_id and self.start_date and self.end_date:
            start_date=self.start_date
            end_date=self.end_date
            orders = self.env['hr.attendance'].search([('check_in', '>=',start_date),('check_out', '<=',end_date),('employee_id','=',self.employee_id.id)])
            val={'value':{'attendee_ids':orders,'employee_id':self.employee_id.id,'start_date':self.start_date,'end_date':self.end_date}}
            new_id = super(Emp_attendance_report, self).create(val)      
        return val
    @api.multi
    def create_attendance(self):
        pass

    @api.multi
    def generate_report(self):
        start_date=self.start_date
        end_date=self.end_date
        orders = self.env['hr.attendance'].search([('check_in', '>=',start_date),('check_out', '<=',end_date),('employee_id','=',self.employee_id.id)])
        if len(orders) >=1:
            for i in orders:
                for j in self.env['hr.attendance'].browse(i.id):
                    j.write({'attendee_id':self.id})
            test=self.browse(self.id)
            for ids in test: 
                print "ids.attendee_ids             ",ids.attendee_ids
                for i in ids.attendee_ids:
                    print "s    ",i.employee_id.name,i.check_in
            return self.env['report'].get_action(self, 'hr_attendance_extended.Report_hr_attendance_part_time')
        else:
            raise UserError(_('No Records Found'))

    file_txt = fields.Binary("Attachment", help="Select image here")
    file_name = fields.Char("file name")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    start_date = fields.Datetime(string='Start Date',default=fields.Datetime.now)
    end_date = fields.Datetime(string='End Date', default=fields.Datetime.now)
    attendee_ids = fields.One2many("hr.attendance","attendee_id",string="Attendees")
    current_date = fields.Datetime(string='Date',default=fields.Datetime.now)

class Full_Emp_attendance_report(models.Model):
    _name="emp.report_full"

    @api.onchange('employee_id','start_date','end_date')
    def on_change_employee(self):
        vals={}
        if self.employee_id and self.start_date and self.end_date:
            start_date=self.start_date
            end_date=self.end_date
            orders = self.env['hr.attendance'].search([('check_in', '>=',start_date),('check_out', '<=',end_date),('employee_id','=',self.employee_id.id)])
            vals={'value':{'attendance_ids':orders,'employee_id':self.employee_id.id,'start_date':self.start_date,'end_date':self.end_date}}
            obj = super(Full_Emp_attendance_report, self).create(vals)
        return vals
    
    @api.multi
    def generate_report(self):
        start_date=self.start_date
        end_date=self.end_date
        orders = self.env['hr.attendance'].search([('check_in', '>=',start_date),('check_out', '<=',end_date),('employee_id','=',self.employee_id.id)])
        
        if len(orders) >=1:
            for i in orders:
                for j in self.env['hr.attendance'].browse(i.id):
                    j.write({'attendance_id':self.id})
            test=self.browse(self.id)
            for ids in test: 
                print "ids.attendee_ids             ",ids.attendance_ids
                for i in ids.attendance_ids:
                    print "s    ",i.employee_id.name,i.check_in
            return self.env['report'].get_action(self, 'hr_attendance_extended.Report_hr_attendance_full_time_emp')
        else:
            raise UserError(_('No Records Found'))
    employee_id = fields.Many2one('hr.employee', string="Employee")
    start_date = fields.Datetime(string='Start Date', required=True,default=fields.Datetime.now)
    end_date = fields.Datetime(string='End Date', required=True,default=fields.Datetime.now)
    attendance_ids = fields.One2many("hr.attendance","attendance_id",string="Attendees")
    current_date = fields.Datetime(string='Date',default=fields.Datetime.now)

class HR_Employee(models.Model):
    _inherit = "hr.employee"

    emp_id = fields.Char("Employee ID")


class HrAttendance_extended(models.Model):
    _inherit ="hr.attendance"
    
    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        """ Verifies the validity of the attendance record compared to the others from the same employee.
            For the same employee we must have :
                * maximum 1 "open" attendance record (without check_out)
                * no overlapping time slices with previous employee records
        """
        for attendance in self:
            # we take the latest attendance before our check_in time and check it doesn't overlap with ours
            last_attendance_before_check_in = self.env['hr.attendance'].search([
                ('employee_id', '=', attendance.employee_id.id),
                ('check_in', '<=', attendance.check_in),
                ('id', '!=', attendance.id),
            ], order='check_in desc', limit=1)
            print "//",last_attendance_before_check_in
            print "//",last_attendance_before_check_in.check_out,last_attendance_before_check_in.check_out,attendance.check_in
            # if last_attendance_before_check_in and last_attendance_before_check_in.check_out and last_attendance_before_check_in.check_out > attendance.check_in:
            #     print "-*-*-*-*-*-*     kd     -*-*-*-*-*-*-*-*-*-*-*-"
            #     raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s") % {
            #         'empl_name': attendance.employee_id.name_related,
            #         'datetime': fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(attendance.check_in))),
            #     })

            if not attendance.check_out:
                # if our attendance is "open" (no check_out), we verify there is no other "open" attendance
                no_check_out_attendances = self.env['hr.attendance'].search([
                    ('employee_id', '=', attendance.employee_id.id),
                    ('check_out', '=', False),
                    ('id', '!=', attendance.id),
                ])
                if no_check_out_attendances:
                    raise ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee hasn't checked out since %(datetime)s") % {
                        'empl_name': attendance.employee_id.name_related,
                        'datetime': fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(no_check_out_attendances.check_in))),
                    })
            else:
                # we verify that the latest attendance with check_in time before our check_out time
                # is the same as the one before our check_in time computed before, otherwise it overlaps
                last_attendance_before_check_out = self.env['hr.attendance'].search([
                    ('employee_id', '=', attendance.employee_id.id),
                    ('check_in', '<', attendance.check_out),
                    ('id', '!=', attendance.id),
                ], order='check_in desc', limit=1)
                if last_attendance_before_check_out and last_attendance_before_check_in != last_attendance_before_check_out:
                    print "-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-"
                    raise ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s") % {
                        'empl_name': attendance.employee_id.name_related,
                        'datetime': fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(last_attendance_before_check_out.check_in))),
                    })


    # department_id = fields.Many2one('hr.department', string='Department')
    state = fields.Selection([('draft','Draft'),('approved','Approved')], string="status", default='draft')
    shift = fields.Char("Shift")
    # type_id = fields.Many2one('hr.contract.type', string="Shift") #required=True, default=lambda self: self.env['hr.contract.type'].search([], limit=1)
    date_dt = fields.Date("Date")
    day = fields.Char("Day")
    emp_remark = fields.Char("Emp Remark")
    lev_remark = fields.Char("Lev Remark")
    sup_remark = fields.Char("Sup Remark")
    o_timein = fields.Float("O Timein")
    o_timeout = fields.Float("O Timeout")
    adj_timein =fields.Float("adj_timein")
    adj_timeout = fields.Float("adj_timeout")
    attendee_id = fields.Many2one("emp.report_part")
    attendance_id = fields.Many2one("emp.report_full")

    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        """ Verifies the validity of the attendance record compared to the others from the same employee.
            For the same employee we must have :
                * maximum 1 "open" attendance record (without check_out)
                * no overlapping time slices with previous employee records
        """
        for attendance in self:
            # we take the latest attendance before our check_in time and check it doesn't overlap with ours
            last_attendance_before_check_in = self.env['hr.attendance'].search([
                ('employee_id', '=', attendance.employee_id.id),
                ('check_in', '<=', attendance.check_in),
                ('id', '!=', attendance.id),
            ], order='check_in desc', limit=1)
            print "//",last_attendance_before_check_in
            print "//",last_attendance_before_check_in.check_out,last_attendance_before_check_in.check_out,attendance.check_in
            # if last_attendance_before_check_in and last_attendance_before_check_in.check_out and last_attendance_before_check_in.check_out > attendance.check_in:
            #     print "-*-*-*-*-*-*     kd     -*-*-*-*-*-*-*-*-*-*-*-"
            #     raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s") % {
            #         'empl_name': attendance.employee_id.name_related,
            #         'datetime': fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(attendance.check_in))),
            #     })

            if not attendance.check_out:
                # if our attendance is "open" (no check_out), we verify there is no other "open" attendance
                no_check_out_attendances = self.env['hr.attendance'].search([
                    ('employee_id', '=', attendance.employee_id.id),
                    ('check_out', '=', False),
                    ('id', '!=', attendance.id),
                ])
                if no_check_out_attendances:
                    raise ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee hasn't checked out since %(datetime)s") % {
                        'empl_name': attendance.employee_id.name_related,
                        'datetime': fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(no_check_out_attendances.check_in))),
                    })
            else:
                # we verify that the latest attendance with check_in time before our check_out time
                # is the same as the one before our check_in time computed before, otherwise it overlaps
                last_attendance_before_check_out = self.env['hr.attendance'].search([
                    ('employee_id', '=', attendance.employee_id.id),
                    ('check_in', '<', attendance.check_out),
                    ('id', '!=', attendance.id),
                ], order='check_in desc', limit=1)
                if last_attendance_before_check_out and last_attendance_before_check_in != last_attendance_before_check_out:
                    print "-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-"
                    raise ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s") % {
                        'empl_name': attendance.employee_id.name_related,
                        'datetime': fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(last_attendance_before_check_out.check_in))),
                    })

    def get_diff(self, employee, checkin = False, checkout = False):
       # Fetch the cursor to execute the queries

        cr = self._cr
        user = self.env.user
        checkin_diff = check_in_status = checkout_diff = checkout_status = \
            False
        if checkin:
            # Fetch the Starting Hour for a particular day to Match against the
            # CheckIn
            check_in_dt = datetime.strptime(checkin,
                                            DEFAULT_SERVER_DATETIME_FORMAT)
            #Getting the Timezone
            local_tz = pytz.timezone(user.tz or 'UTC')
            ci_dt = check_in_dt.replace(tzinfo = pytz.utc
                                         ).astimezone(local_tz)
            qry = '''select hour_from
                        from resource_calendar rc, \
                        resource_calendar_attendance rca
                        where rc.id = rca.calendar_id and
                        rc.id = %s and \
                        dayofweek=%s'''
            qry1 = qry + " and %s between date_from and date_to order by \
            hour_from limit 1"
            if not employee.calendar_id:
                raise ValidationError(_('Please Configure Working Time in Employee!'))
            params1 = (employee.calendar_id.id, str(ci_dt.weekday()), checkin)
            cr.execute(qry1, params1)
            res = cr.fetchone()
            # If specific dates are not given then fetch the records that do
            # not have dates
            if not res:
                qry2 = qry + " order by hour_from limit 1"
                params2 = (employee.calendar_id.id, str(ci_dt.weekday()))
                cr.execute(qry2, params2)
                res = cr.fetchone()
            hour_from = res and res[0] or 0.0
            # Converting the Hours and Minutes to Float to match as
            # odoo Standard.
            checkin_time = ci_dt.hour + (ci_dt.minute * 100 / 60) / 100.0
            # Get the Check In Difference
            #Setting the Office start time
            hour_from=8.25
            print "checkin_time             ",checkin_time
            checkin_diff = checkin_time - hour_from

            print "\n\n\n\n\\n\n\n\n\n\n\n\ncheckin_diff",checkin_diff


            # Generate the CheckIn Status as per the CheckIn time
            check_in_status = 'ontime'
            if checkin_diff > 0:
                check_in_status = 'late'
            elif checkin_diff < 0:
                check_in_status = 'early'
        if checkout:
            # Fetch the Ending Hour for a particular day to Match against
            # the CheckOut
            check_out_dt = datetime.strptime(checkout,
                                             DEFAULT_SERVER_DATETIME_FORMAT)
            local_tz = pytz.timezone(user.tz or 'UTC')
            co_dt = check_out_dt.replace(tzinfo = pytz.utc
                                         ).astimezone(local_tz)
            qry = '''select hour_to,rca.id as rca_id
                        from resource_calendar rc, \
                        resource_calendar_attendance rca
                        where rc.id = rca.calendar_id and
                        rc.id = %s and \
                        dayofweek=%s'''
            qry1 = qry + "and %s between date_from and date_to order by \
                   hour_to desc limit 1"
            
            params1 = (employee.calendar_id.id, str(co_dt.weekday()), checkin)
            cr.execute(qry1, params1)
            res = cr.fetchone()
            # If specific dates are not given then fetch the records that do
            # not have dates
            if not res:
                qry2 = qry + " order by hour_to desc limit 1"
                params2 = (employee.calendar_id.id, str(co_dt.weekday()))
                cr.execute(qry2, params2)
                res = cr.fetchone()
            hour_to = res and res[0] or 0.0
            # Converting the Hours and Minutes to Float to match as
            # odoo Standard.
            checkout_time = co_dt.hour + (co_dt.minute * 100 / 60) / 100.0
            # Get the Check Out Difference
            hour_to=17.83
            checkout_diff = checkout_time - hour_to
            print "checkout_diff                ",checkout_diff
            # Generate the CheckOut Status as per the CheckOut time
            checkout_status = 'ontime'
            if checkout_diff > 0:
                checkout_status = 'late'
            elif checkout_diff < 0:
                checkout_status = 'early'
        return checkin_diff, check_in_status, checkout_diff, checkout_status

class HR_payroll_extended(models.Model):
    _inherit="hr.payslip"


    @api.model
    def get_payslip_lines(self, contract_ids, payslip_id):
        def _sum_salary_rule_category(localdict, category, amount):
            if category.parent_id:
                localdict = _sum_salary_rule_category(localdict, category.parent_id, amount)
            if category.code in localdict['categories'].dict:
                amount += localdict['categories'].dict[category.code]
                print "amount           ",amount
            localdict['categories'].dict[category.code] = amount
            return localdict

        class BrowsableObject(object):
            def __init__(self, employee_id, dict, env):
                self.employee_id = employee_id
                self.dict = dict
                self.env = env

            def __getattr__(self, attr):
                return attr in self.dict and self.dict.__getitem__(attr) or 0.0

        class InputLine(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""
            def sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = fields.Date.today()
                self.env.cr.execute("""
                    SELECT sum(amount) as sum
                    FROM hr_payslip as hp, hr_payslip_input as pi
                    WHERE hp.employee_id = %s AND hp.state = 'done'
                    AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s""",
                    (self.employee_id, from_date, to_date, code))
                return self.env.cr.fetchone()[0] or 0.0

        class WorkedDays(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""
            def _sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = fields.Date.today()
                self.env.cr.execute("""
                    SELECT sum(number_of_days) as number_of_days, sum(number_of_hours) as number_of_hours
                    FROM hr_payslip as hp, hr_payslip_worked_days as pi
                    WHERE hp.employee_id = %s AND hp.state = 'done'
                    AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s""",
                    (self.employee_id, from_date, to_date, code))
                return self.env.cr.fetchone()

            def sum(self, code, from_date, to_date=None):
                res = self._sum(code, from_date, to_date)
                return res and res[0] or 0.0

            def sum_hours(self, code, from_date, to_date=None):
                res = self._sum(code, from_date, to_date)
                return res and res[1] or 0.0

        class Payslips(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""

            def sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = fields.Date.today()
                self.env.cr.execute("""SELECT sum(case when hp.credit_note = False then (pl.total) else (-pl.total) end)
                            FROM hr_payslipas hp, hr_payslip_line as pl
                            WHERE hp.employee_id = %s AND hp.state = 'done'
                            AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pl.slip_id AND pl.code = %s""",
                            (self.employee_id, from_date, to_date, code))
                res = self.env.cr.fetchone()
                return res and res[0] or 0.0

        #we keep a dict with the result because a value can be overwritten by another rule with the same code

        result_dict = {}
        rules_dict = {}
        worked_days_dict = {}
        inputs_dict = {}
        blacklist = []
        payslip = self.env['hr.payslip'].browse(payslip_id)
        for worked_days_line in payslip.worked_days_line_ids:
            worked_days_dict[worked_days_line.code] = worked_days_line
        for input_line in payslip.input_line_ids:
            inputs_dict[input_line.code] = input_line

        categories = BrowsableObject(payslip.employee_id.id, {}, self.env)
        inputs = InputLine(payslip.employee_id.id, inputs_dict, self.env)
        worked_days = WorkedDays(payslip.employee_id.id, worked_days_dict, self.env)
        payslips = Payslips(payslip.employee_id.id, payslip, self.env)
        rules = BrowsableObject(payslip.employee_id.id, rules_dict, self.env)

        baselocaldict = {'categories': categories, 'rules': rules, 'payslip': payslips, 'worked_days': worked_days, 'inputs': inputs}
        #get the ids of the structures on the contracts and their parent id as well
        contracts = self.env['hr.contract'].browse(contract_ids)
        structure_ids = contracts.get_all_structures()
        #get the rules of the structure and thier children
        rule_ids = self.env['hr.payroll.structure'].browse(structure_ids).get_all_rules()
        #run the rules by sequence
        sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x:x[1])]
        sorted_rules = self.env['hr.salary.rule'].browse(sorted_rule_ids)

        for contract in contracts:
            employee = contract.employee_id
            localdict = dict(baselocaldict, employee=employee, contract=contract)
            for rule in sorted_rules:
                key = rule.code + '-' + str(contract.id)
                print "key",key
                localdict['result'] = None
                localdict['result_qty'] = 1.0
                localdict['result_rate'] = 100
                #check if the rule can be applied
                if rule.satisfy_condition(localdict) and rule.id not in blacklist:
                    #compute the amount of the rule
                    amount, qty, rate = rule.compute_rule(localdict)
                    #check if there is already a rule computed with that code
                    previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                    #set/overwrite the amount computed for this rule in the localdict
                    tot_rule = amount * qty * rate / 100.0
                    localdict[rule.code] = tot_rule
                    rules_dict[rule.code] = rule
                    #sum the amount for its salary category
                    localdict = _sum_salary_rule_category(localdict, rule.category_id, tot_rule - previous_amount)
                    #create/overwrite the rule in the temporary results
                    print "tot_rule - previous_amount               ",tot_rule - previous_amount
                    result_dict[key] = {
                        'salary_rule_id': rule.id,
                        'contract_id': contract.id,
                        'name': rule.name,
                        'code': rule.code,
                        'category_id': rule.category_id.id,
                        'sequence': rule.sequence,
                        'appears_on_payslip': rule.appears_on_payslip,
                        'condition_select': rule.condition_select,
                        'condition_python': rule.condition_python,
                        'condition_range': rule.condition_range,
                        'condition_range_min': rule.condition_range_min,
                        'condition_range_max': rule.condition_range_max,
                        'amount_select': rule.amount_select,
                        'amount_fix': rule.amount_fix,
                        'amount_python_compute': rule.amount_python_compute,
                        'amount_percentage': rule.amount_percentage,
                        'amount_percentage_base': rule.amount_percentage_base,
                        'register_id': rule.register_id.id,
                        'amount': amount,
                        'employee_id': contract.employee_id.id,
                        'quantity': qty,
                        'rate': rate,
                    }
                else:
                #blacklist this rule and its children
                    blacklist += [id for id, seq in rule._recursive_search_of_rules()]


                attendance_obj=self.env['hr.attendance']
                attendance_ids=self.env['hr.attendance'].search([])
                count = 0
                ot=0
                deduct_amount =0
                fmt = '%Y-%m-%d'


                d1 = datetime.strptime(self.date_from, fmt)
                d2 = datetime.strptime(self.date_to, fmt)
                fmt="%Y-%m-%d %H:%M:%S"
                daysDiff =(d2-d1).days + 1
                month_salary=self.contract_id.wage
                one_day=(self.contract_id.wage/daysDiff)
                one_hour_salary=one_day/8
                half_hour_salary=-(one_hour_salary/2)

                print "Days left     ",daysDiff
                print "month_salary         ",month_salary
                print "one Hour salary          ",one_hour_salary
                print "half and hour salary             ",half_hour_salary
                
                #This is For Deducting Salary for late attendance

                for ids in attendance_ids:
                    for obj in attendance_obj.browse(ids.id):
                        if obj.employee_id.id == contract.employee_id.id :
                            if obj.check_in and obj.check_out:
                                d3=datetime.strptime(obj.check_in, fmt)
                                d4=datetime.strptime(obj.check_out, fmt)
                                
                                # d1 = d1.date()
                                # d2=d2.date()
                                # d3=d3.date()
                                # d4= d4.date()
                                print "type       123      ",d1<=d3<=d4<=d2
                                # err
                                if d1<=d3<=d4<=d2:
                                    if obj.checkin_diff > 0.5:
                                        count += 1


                    
                    if count >=1:
                        search_rule=self.env['hr.salary.rule'].search([])
                        for k in search_rule:
                            for i in self.env['hr.salary.rule'].browse(k.id):
                                if i.name == "Late Attendance":
                                    if count >=1:
                                        # half_hour_salary = - half_hour_salary
                                        i.write({'amount_fix':half_hour_salary,'quantity':count})
                                    else:
                                        i.write({'amount_fix':half_hour_salary,'quantity':0})

                                    key2=i.code + '-' + str(contract.id)
                                    #compute the amount of the rule
                                    amount, qty, rate = i.compute_rule(localdict)
                                    #check if there is already a rule computed with that code
                                    previous_amount = i.code in localdict and localdict[i.code] or 0.0
                                    #set/overwrite the amount computed for this rule in the localdict
                                    tot_rule = amount * qty * rate / 100.0
                                    localdict[i.code] = tot_rule
                                    rules_dict[i.code] = i
                                    #sum the amount for its salary category
                                    localdict = _sum_salary_rule_category(localdict, i.category_id, tot_rule - previous_amount)
                                    #create/overwrite the rule in the temporary results
                                    print "tot_rule - previous_amount               ",tot_rule - previous_amount
                                    # amount= - amount
                                    result_dict[key2] = {
                                        'salary_rule_id': i.id,
                                        'contract_id': contract.id,
                                        'name': i.name,
                                        'code': i.code,
                                        'category_id': i.category_id.id,
                                        'sequence': i.sequence,
                                        'appears_on_payslip': i.appears_on_payslip,
                                        'condition_select': i.condition_select,
                                        'condition_python': i.condition_python,
                                        'condition_range': i.condition_range,
                                        'condition_range_min': i.condition_range_min,
                                        'condition_range_max': i.condition_range_max,
                                        'amount_select': i.amount_select,
                                        'amount_fix': i.amount_fix,
                                        'amount_python_compute': i.amount_python_compute,
                                        'amount_percentage': i.amount_percentage,
                                        'amount_percentage_base': i.amount_percentage_base,
                                        'register_id': i.register_id.id,
                                        'amount': amount,
                                        'employee_id': contract.employee_id.id,
                                        'quantity':qty,
                                       'rate': rate,
                                    }

                #This code is half stage and Get ids who is doing OT
                for ids in attendance_ids:
                    for obj in attendance_obj.browse(ids.id):
                        if obj.employee_id.id == contract.employee_id.id :
                            print datetime.strptime(obj.check_in, fmt)
                            if obj.check_in and obj.check_out:
                                d3=datetime.strptime(obj.check_in, fmt)
                                d4=datetime.strptime(obj.check_out, fmt)
                                # d1 =d1.date() 
                                # d2 = d2.date()
                                # d3 =d3.date()
                                # d4 =d4.date()

                                if d1<=d3<=d4<=d2:
                                    if obj.checkout_diff > 0.5:
                                        ot += 1    
                    if ot >=1:
                        search_rule=self.env['hr.salary.rule'].search([])
                        for k in search_rule:
                            for i in self.env['hr.salary.rule'].browse(k.id):
                                if i.name == "OT #1.5":
                                    if count >=1:
                                        for ids in attendance_ids:
                                            for obj in attendance_obj.browse(ids.id):
                                                s_date = obj.check_in
                                                dt_obj = dt.datetime.strptime(s_date,'%Y-%m-%d %H:%M:%S')
                                                
                                                day = calendar.day_name[dt_obj.weekday()]
                                                days = ["Monday","Tuesday","Wednesday","Thursday","Friday"]
                                                if day in days :
                                                    salary=one_hour_salary*1.5 *obj.checkout_diff
                                                else :
                                                    salary=one_hour_salary*2.0 *obj.checkout_diff
                                                salary = + salary
                                                i.write({'amount_fix':salary,'quantity':count})
                                    else:
                                        i.write({'amount_fix':0,'quantity':0})

                                    key2=i.code + '-' + str(contract.id)
                                    #compute the amount of the rule
                                    amount, qty, rate = i.compute_rule(localdict)
                                    #check if there is already a rule computed with that code
                                    previous_amount = i.code in localdict and localdict[i.code] or 0.0
                                    #set/overwrite the amount computed for this rule in the localdict
                                    tot_rule = amount * qty * rate / 100.0
                                    localdict[i.code] = tot_rule
                                    rules_dict[i.code] = i
                                    #sum the amount for its salary category
                                    localdict = _sum_salary_rule_category(localdict, i.category_id, tot_rule - previous_amount)
                                    #create/overwrite the rule in the temporary results
                                    print "tot_rule - previous_amount               ",tot_rule, previous_amount
                                    # amount= - amount
                                    result_dict[key2] = {
                                        'salary_rule_id': i.id,
                                        'contract_id': contract.id,
                                        'name': i.name,
                                        'code': i.code,
                                        'category_id': i.category_id.id,
                                        'sequence': i.sequence,
                                        'appears_on_payslip': i.appears_on_payslip,
                                        'condition_select': i.condition_select,
                                        'condition_python': i.condition_python,
                                        'condition_range': i.condition_range,
                                        'condition_range_min': i.condition_range_min,
                                        'condition_range_max': i.condition_range_max,
                                        'amount_select': i.amount_select,
                                        'amount_fix': i.amount_fix,
                                        'amount_python_compute': i.amount_python_compute,
                                        'amount_percentage': i.amount_percentage,
                                        'amount_percentage_base': i.amount_percentage_base,
                                        'register_id': i.register_id.id,
                                        'amount': amount,
                                        'employee_id': contract.employee_id.id,
                                        'quantity':qty,
                                        'rate': rate,
                                    }



        return [value for code, value in result_dict.items()]

                    
