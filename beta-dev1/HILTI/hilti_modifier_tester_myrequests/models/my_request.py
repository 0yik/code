# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
from openerp.exceptions import except_orm, Warning


class ot_request(models.Model):
    _name = 'ot.request'
    
    ot_start_date = fields.Datetime('Start Date & Time')
    ot_end_date = fields.Datetime('End Date & Time')
    duration = fields.Char('Duration')
    t_re_id = fields.Many2one('my.request')
    duration_compute = fields.Char('Duration', compute='_compute_duration_req')

    @api.one
    def _compute_duration_req(self):
        self.duration_compute = self.duration
    
    @api.onchange('ot_start_date', 'ot_end_date')
    @api.depends('ot_start_date', 'ot_end_date')
    def onchange_datetime(self):
        if self.ot_start_date and self.ot_end_date:
            import datetime
            first  = datetime.datetime.strptime(self.ot_start_date, "%Y-%m-%d %H:%M:%S")
            last = datetime.datetime.strptime(self.ot_end_date, "%Y-%m-%d %H:%M:%S")
            if first.date() == last.date():
                diff = last - first
                total_hm = abs(diff)
                self.duration = total_hm

class tester_myreqest(models.Model):
    _name = 'my.request'
    _rec_name = 'req_no'
    
    req_no = fields.Char('Req No.')
    partner_id = fields.Many2one('res.partner', string="Tester")
    req_type = fields.Selection([('unavailability', 'Unavailability'), ('overtime', 'Overtime')])
    description = fields.Text('Description')
    start_date = fields.Datetime('Start Date &;amp Time')
    end_date = fields.Datetime('End Date &;amp Time')
    full_start_date = fields.Date('Start Date')
    full_end_date = fields.Date('End Date')
    days = fields.Char('Days')
    is_half_leave = fields.Boolean("Half day")
    duration = fields.Char('Duration')
    days_compute = fields.Char('Duration', compute='_compute_days')
    duration_compute = fields.Char('Duration', compute='_compute_duration')
    status = fields.Selection([('draft', 'Draft'), ('awaitinapprovel', 'Awaiting Approval'), ('approved', 'Approved'), ('reject', 'Reject')],
                              string='Status', default='draft')
    ot_req_ids = fields.One2many('ot.request', 't_re_id', string="Overtime Request")
    
    
    @api.one
    def _compute_duration(self):
        self.duration_compute = self.duration
        
    @api.one
    def _compute_days(self):
        self.days_compute = self.days
    
    
    @api.model
    def create(self, vals):
        vals['req_no'] = self.env['ir.sequence'].next_by_code('my.request') or _('New')
        user = self.env['res.users'].browse(self.env.uid)
        vals['partner_id'] = user.partner_id and user.partner_id.id
        result = super(tester_myreqest, self).create(vals)
        if result and result.req_type == 'overtime' and result.ot_req_ids:
            total_time = [str(time.duration) for time in result.ot_req_ids]
            totalSecs = 0
            for tm in total_time:
                timeParts = [int(s) for s in tm.split(':')]
                totalSecs += (timeParts[0] * 60 + timeParts[1]) * 60 + timeParts[2]
            totalSecs, sec = divmod(totalSecs, 60)
            hr, min = divmod(totalSecs, 60)
            result.duration = "%d:%02d:%02d" % (hr, min, sec)
        return result
    
    @api.multi
    def write(self, vals):
        res = super(tester_myreqest, self).write(vals)
        if vals and 'ot_req_ids' in vals.keys() and self.req_type == 'overtime':
            total_time = [str(time.duration) for time in self.ot_req_ids]
            totalSecs = 0
            for tm in total_time:
                timeParts = [int(s) for s in tm.split(':')]
                totalSecs += (timeParts[0] * 60 + timeParts[1]) * 60 + timeParts[2]
            totalSecs, sec = divmod(totalSecs, 60)
            hr, min = divmod(totalSecs, 60)
            self.duration = "%d:%02d:%02d" % (hr, min, sec)
        return res

    
    def waiting_approvel(self):
        if self.req_type == 'overtime':
            self.status = 'approved'
        else:
            self.status = 'awaitinapprovel'
        
        
    def state_approvel(self):
        self.status = 'approved'
        
        
    def state_reject(self):
        self.status = 'reject'
        
    @api.onchange('req_type')
    def onchange_req_type(self):
        if self.req_type == 'overtime':
            self.is_half_leave = True
        if self.req_type == 'unavailability':
            self.is_half_leave = False
        
    
    @api.onchange('start_date', 'end_date', 'full_start_date', 'full_end_date')
    @api.depends('start_date', 'end_date', 'full_start_date', 'full_end_date')
    def onchange_date(self):
        if self.start_date and self.end_date and self.is_half_leave == True :
            import datetime
            first  = datetime.datetime.strptime(self.start_date, "%Y-%m-%d %H:%M:%S")
            last = datetime.datetime.strptime(self.end_date, "%Y-%m-%d %H:%M:%S")
            if first.date() == last.date():
                diff = datetime.datetime.strptime(self.start_date, "%Y-%m-%d %H:%M:%S") - datetime.datetime.strptime(self.end_date, "%Y-%m-%d %H:%M:%S")
                total_hm = abs(diff)
                self.duration = total_hm
        if self.full_start_date and self.full_end_date and self.is_half_leave == False:
            from datetime import datetime
            date_format = "%Y-%m-%d"
            a = datetime.strptime(self.full_start_date, date_format)
            b = datetime.strptime(self.full_end_date, date_format)
            delta = b - a
            self.days = int(delta.days) + 1
            
            
            
