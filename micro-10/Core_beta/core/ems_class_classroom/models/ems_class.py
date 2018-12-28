# -*- coding: utf-8 -*-
from odoo import fields, models, exceptions, api, _
from odoo.exceptions import UserError
from datetime import datetime
from datetime import timedelta
from dateutil import tz
import pytz

class EmsClass(models.Model):
    _name = 'ems.class'
    _description = "Class"
    #_rec_name = "subject_id"
    
    name = fields.Char('Name')
    subject_id = fields.Many2one('subject.subject','Subject', required=True)
    start_time = fields.Datetime('Start Time', required=True)
    end_time = fields.Datetime('End Time', required=True)
    intake_id = fields.Many2one('academic.year','Intake',required=True)
    teacher_id = fields.Many2one('hr.employee','Teacher', domain="[('is_school_teacher','=',True)]",required=True)
    classroom_id = fields.Many2one('ems.classroom','Classroom')
    recurrency = fields.Boolean('Recurrent')
    interval = fields.Integer('Repeat Every', help="Repeat every (Days/Week/Month/Year)")
    rrule_type = fields.Selection([('daily', 'Day(s)')], 'Recurrency', default='daily')
    end_type = fields.Selection([('count', 'Number of repetitions'), ('end_date', 'End date')], 'Recurrence Termination')
    count = fields.Integer('Repeat', help="Repeat x times")
    final_date = fields.Datetime('Repeat Until')
    mo = fields.Boolean('Mon')
    tu = fields.Boolean('Tue')
    we = fields.Boolean('Wed')
    th = fields.Boolean('Thu')
    fr = fields.Boolean('Fri')
    sa = fields.Boolean('Sat')
    su = fields.Boolean('Sun')
    starting_no = fields.Integer('Starting from Number')
    exclude_weekend = fields.Boolean(string='Exclude Weekend')
    exclude_public = fields.Boolean(string='Exclude Public Holiday')
    recurrenced = fields.Boolean('Recurrenced',readonly=True)
    
    @api.model
    def create(self, vals):
        subject_name = self.env['subject.subject'].browse(vals.get('subject_id')).name
        dt = datetime.strptime(str(vals.get('start_time')),"%Y-%m-%d %H:%M:%S") + timedelta(hours = 5 ,minutes = 30)
        date = str(str(dt).split(' ')[0]).split('-')
        name = subject_name +' '+ date[2]+'-'+date[1]+'-'+date[0]
        vals.update({'name': name})
        #class_ids = self.search([('classroom_id','=',vals.get('classroom_id'))])
        #if class_ids:
        #    for class_id in class_ids:
        #        class_date = str(class_id.start_time).split(' ')
        #        if class_date[0] == str(vals.get('start_time')).split(' ')[0]:
        #            raise UserError(_('The Classroom already created for this date'))
        rec = super(EmsClass, self).create(vals)
        return rec
    
    def exclude_public_holiday(self,new_start_date,new_end_date,interval):
        hr_holiday_lines_pool = self.env['hr.holiday.lines']
        date_dict = {}
        str_date = new_start_date.strftime('%Y-%m-%d')
        #print "\n\n@@@str_date=",str_date
        hr_holiday_lines_objs =  hr_holiday_lines_pool.search([('holiday_date','=',str_date)])
        #print "\n\nhr_holiday_lines_objs=",hr_holiday_lines_objs
        if hr_holiday_lines_objs:
            for hr_holiday_lines_obj in hr_holiday_lines_objs:
                if hr_holiday_lines_obj.holiday_id.state not in ['draft','refused','cancelled']:
                    weekday = new_start_date.weekday()
                    if weekday == 5:
                        new_start_date = new_start_date + timedelta(days=interval+2)
                        new_end_date = new_end_date + timedelta(days=interval+2)
                        date_dict.update({'new_start_date':new_start_date,'new_end_date':new_end_date})
                    elif weekday == 6:
                        new_start_date = new_start_date + timedelta(days=interval+1)
                        new_end_date = new_end_date + timedelta(days=interval+1)
                        date_dict.update({'new_start_date':new_start_date,'new_end_date':new_end_date})
                    else:
                        new_start_date = new_start_date + timedelta(days=1)
                        new_end_date = new_end_date + timedelta(days=1)
                        date_dict.update({'new_start_date':new_start_date,'new_end_date':new_end_date})
        return date_dict
        
    
    @api.multi
    def generate_recurrent(self):
        if self.recurrency:
            hr_holiday_lines_pool = self.env['hr.holiday.lines']
            #ems_class_ids = []
            interval = self.interval
            start_time = datetime.strptime(self.start_time, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.strptime(self.end_time, '%Y-%m-%d %H:%M:%S')
            end_type = self.end_type
            if end_type == 'end_date':
                final_date = datetime.strptime(self.final_date, '%Y-%m-%d %H:%M:%S')
                while start_time < final_date:
                    new_start_date = start_time + timedelta(days=interval)
                    new_end_date = end_time + timedelta(days=interval)
                    # Exclude Weekend
                    weekday = new_start_date.weekday()
                    if self.exclude_weekend:
                        if weekday == 5:
                            new_start_date = start_time + timedelta(days=interval+2)
                            new_end_date = end_time + timedelta(days=interval+2)
                        if weekday == 6:
                            new_start_date = start_time + timedelta(days=interval+1)
                            new_end_date = end_time + timedelta(days=interval+1)
                    
                    # Exclude Public Holiday
                    if self.exclude_public:
                        print "\n\n======new_start_date==",new_start_date
                        date_dict = self.exclude_public_holiday(new_start_date,new_end_date,interval)
                        if date_dict.has_key('new_start_date'):
                            print "\n\n###new_start_date=",date_dict['new_start_date']
                            str_date = date_dict['new_start_date'].strftime('%Y-%m-%d')
                            hr_holiday_lines_objs =  hr_holiday_lines_pool.search([('holiday_date','=',str_date)])
                            if hr_holiday_lines_objs:
                                date_dict = self.exclude_public_holiday(new_start_date,new_end_date,interval)
                                new_start_date = date_dict['new_start_date']
                                new_end_date = date_dict['new_end_date']
                                print "\n\n===new_start_date=",new_start_date,new_end_date
                            else:
                                new_start_date = date_dict['new_start_date']
                                new_end_date = date_dict['new_end_date']
                                weekday = new_start_date.weekday()
                                if weekday == 5:
                                    new_start_date = new_start_date + timedelta(days=2)
                                    new_end_date = new_end_date + timedelta(days=2)
                                if weekday == 6:
                                    new_start_date = new_start_date + timedelta(days=1)
                                    new_end_date = new_end_date + timedelta(days=1)
                                print "\n\n******new_start_date=",new_start_date,new_end_date
                                str_date = new_start_date.strftime('%Y-%m-%d')
                                hr_holiday_lines_objs =  hr_holiday_lines_pool.search([('holiday_date','=',str_date)])
                                if hr_holiday_lines_objs:
                                    date_dict = self.exclude_public_holiday(new_start_date,new_end_date,interval)
                                    new_start_date = date_dict['new_start_date']
                                    new_end_date = date_dict['new_end_date']
                    #####
                    start_time = new_start_date
                    end_time = new_end_date
                    print "\n\n======FINAL DATE",start_time,end_time
                    if start_time < final_date:
                        vals = {
                            'name': self.name,
                            'subject_id' : self.subject_id and self.subject_id.id or False,
                            'intake_id' : self.intake_id and self.intake_id.id or False,
                            'start_time' : new_start_date,
                            'end_time' : new_end_date,
                            'teacher_id' : self.teacher_id and self.teacher_id.id or False,
                            'classroom_id' : self.classroom_id and self.classroom_id.id or False,
                            'recurrenced': True,
                        }
                        self.create(vals)
            if end_type == 'count':
                count = self.count
                for i in range(count):
                    new_start_date = start_time + timedelta(days=interval)
                    new_end_date = end_time + timedelta(days=interval)
                    # Exclude Weekend
                    weekday = new_start_date.weekday()
                    if self.exclude_weekend:
                        if weekday == 5:
                            new_start_date = start_time + timedelta(days=interval+2)
                            new_end_date = end_time + timedelta(days=interval+2)
                        if weekday == 6:
                            new_start_date = start_time + timedelta(days=interval+1)
                            new_end_date = end_time + timedelta(days=interval+1)
                    
                    # Exclude Public Holiday
                    if self.exclude_public:
                        print "\n\n======new_start_date==",new_start_date
                        date_dict = self.exclude_public_holiday(new_start_date,new_end_date,interval)
                        if date_dict.has_key('new_start_date'):
                            print "\n\n###new_start_date=",date_dict['new_start_date']
                            str_date = date_dict['new_start_date'].strftime('%Y-%m-%d')
                            hr_holiday_lines_objs =  hr_holiday_lines_pool.search([('holiday_date','=',str_date)])
                            if hr_holiday_lines_objs:
                                date_dict = self.exclude_public_holiday(new_start_date,new_end_date,interval)
                                new_start_date = date_dict['new_start_date']
                                new_end_date = date_dict['new_end_date']
                                print "\n\n===new_start_date=",new_start_date,new_end_date
                            else:
                                new_start_date = date_dict['new_start_date']
                                new_end_date = date_dict['new_end_date']
                                weekday = new_start_date.weekday()
                                if weekday == 5:
                                    new_start_date = new_start_date + timedelta(days=2)
                                    new_end_date = new_end_date + timedelta(days=2)
                                if weekday == 6:
                                    new_start_date = new_start_date + timedelta(days=1)
                                    new_end_date = new_end_date + timedelta(days=1)
                                print "\n\n******new_start_date=",new_start_date,new_end_date
                                str_date = new_start_date.strftime('%Y-%m-%d')
                                hr_holiday_lines_objs =  hr_holiday_lines_pool.search([('holiday_date','=',str_date)])
                                if hr_holiday_lines_objs:
                                    date_dict = self.exclude_public_holiday(new_start_date,new_end_date,interval)
                                    new_start_date = date_dict['new_start_date']
                                    new_end_date = date_dict['new_end_date']
                    #####
                    start_time = new_start_date
                    end_time = new_end_date
                    vals = {
                        'name': self.name,
                        'subject_id' : self.subject_id and self.subject_id.id or False,
                        'intake_id' : self.intake_id and self.intake_id.id or False,
                        'start_time' : new_start_date,
                        'end_time' : new_end_date,
                        'teacher_id' : self.teacher_id and self.teacher_id.id or False,
                        'classroom_id' : self.classroom_id and self.classroom_id.id or False,
                        'recurrenced': True,
                    }
                    self.create(vals)
            self.write({'recurrenced': True})
        return True
    
    
    
