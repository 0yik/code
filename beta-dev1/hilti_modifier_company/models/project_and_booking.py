# -*- coding: utf-8 -*-

from __future__ import division
from odoo import models, fields, api, _
import time
import pytz
from datetime import date, datetime, timedelta, time, date
import calendar
from odoo.exceptions import UserError, ValidationError, Warning
from unittest2.test.test_program import RESULT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_TIME_FORMAT
from mako.pyparser import reserved

class project_project(models.Model):
    _inherit = 'project.project'


    partner_ids = fields.Many2many('res.partner','rela_pr_partner','project_id','partner_id', string="Customers")
    account_manager_id = fields.Many2one('res.partner', string="Account Manager", domain="[('type_of_user', '=', 'hilti_account_manager')]")
    tester_ids = fields.Many2many('res.partner', string="Reserved Testers", domain="[('type_of_user', '=', 'hilti_tester')]")
    email = fields.Char(string="Email")
    booking_ids = fields.One2many('project.booking', 'project_id', string="Booking")
    required_sic = fields.Boolean('Require SIC')
    is_new_project = fields.Boolean('Is New Project?')
    location_id = fields.Many2one('location.location', "Location")
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    postal_code = fields.Many2one('postal.code', related="location_id.postal_code", string="Postal Code")
    status = fields.Selection(
    [('draft', 'Draft'),
        ('approved', 'Approved'),
    ], string='Status', default='draft')

    @api.model
    def search_browse(self, domain, fields):
        query = self._where_calc(domain)
        from_clause, where_clause, where_clause_params = query.get_sql()
        query_str = 'SELECT %s FROM ' % ",".join(fields) + from_clause + (where_clause and (" WHERE %s" % where_clause) or '')
        self._cr.execute(query_str, where_clause_params)
        return self._cr.dictfetchall()


class locatino_location(models.Model):
    _inherit = 'location.location'

    project_id = fields.Many2one('project.project')

class project_booking(models.Model):
    _name = 'project.booking'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _rec_name='booking_no'
    _order = 'id DESC'


    @api.onchange('project_id')
    def onchange_project_address(self):
        if self.project_id and self.project_id.location_id:
            self.location_id = self.project_id.location_id


    def _get_partner_company(self):
        all_comapny = self.env['res.partner'].search([('type_of_user', '=', 'hilti_customer')])
        record_list = [a.id for a in all_comapny if a.company_type == 'company']
        if record_list:
            return [('id', 'in', record_list)]
        else:
            return [('id', 'in', [])]

    @api.multi
    @api.onchange('company_id')
    def _get_partner_contact(self):
        partner_pool = self.env['res.partner']
        p_ids = []
        if self.company_id and self._context and 'come_from_default' not in self._context.keys():
            self.partner_id = False
            #self.update({'domain': {'partner_id': [('id', 'in', p_ids)]}})
            #return {'domain': {'partner_id': [('parent_id', '=', self.company_id and self.company_id.id)]}}
            partner_search = partner_pool.search([('id', 'child_of', [self.company_id.id]),
                                 ('type_of_user', '=', 'hilti_customer')])
            p_ids = [partner.id for partner in partner_search]
            domain = {'partner_id': [('id', 'in', p_ids)]}
            result = {'domain': domain}
            return result #{'domain': {'partner_id': [('id', 'in', partner_search and partner_search.ids or [])]}}
        else:
            #self.update({'domain': {'partner_id': [('id', 'in', p_ids)]}})
            partner_search = partner_pool.search([('type_of_user', '=', 'hilti_customer')])
            p_ids = [partner.id for partner in partner_search]
            return {'domain': {'partner_id': [('id', 'in', p_ids)]}}


    booking_no = fields.Char('Booking Number')
    partner_id = fields.Many2one('res.partner', string="Login")
    company_id = fields.Many2one('res.partner', domain=_get_partner_company, string="Customer")
    #start_time = fields.Datetime('Start Time')
    #end_time = fields.Datetime('End Time')
    #booking_date = fields.Date('Booking Date')
    project_id = fields.Many2one('project.project', string="Project")
    location_id = fields.Many2one('location.location', string="Location")
    user_tester_id = fields.Many2one('res.users', string="Tester")
    tester_id = fields.Many2one('res.partner', string="Tester", related='user_tester_id.partner_id', domain="[('type_of_user', '=', 'hilti_tester')]")
    tester_phone = fields.Char(string="Tester Mobile Number", related='tester_id.phone', store=True)
    sid_required = fields.Boolean('SIC Required')
    contact_id = fields.Char(string="Contact Name")
    contact_number = fields.Char(string="Contact Number")
    status = fields.Selection(
    [
        ('pending', 'Pending'),
        ('started', 'Started'),
        ('rescheduled', 'Re-Scheduled'),
        ('reconfirmed', 'Re-Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='pending')
    user_id = fields.Many2one('res.users', string="User")
    postal_code = fields.Many2one('postal.code', related="location_id.postal_code", string="Postal Code", store=True)
    address = fields.Text('Address', related="location_id.address")
    is_final = fields.Boolean('Is Final')
    final_start_dtime = fields.Datetime('Booking Start Date & Time')
    final_end_dtime = fields.Datetime('Booking End Date & Time')
    delayed_remarks_cust = fields.Text('Delayed remarks')

    @api.model
    def create(self, vals):
        group_hilti_admin = self.env.user.has_group('hilti_modifier_accessrights.group_hilti_admin')
        import datetime
        now = datetime.datetime.now().strftime ("%Y-%m-%d")
        from datetime import datetime
        d1 = datetime.strptime(str(now), "%Y-%m-%d")
        customer_booking_days = self.env['ir.values'].get_default('admin.configuration', 'customer_booking_days')
        vip_partner = False
        if vals and 'partner_id' in vals.keys():
            project = self.env['res.partner'].search([('id', '=', vals['partner_id'])])
            if project.is_vip == True:
                vip_partner = True
        if vals and vals['is_final'] == False and vip_partner == False and group_hilti_admin == False:
            if vals['booking_type'] in ['normal'] and 'time_booking_ids' in vals.keys() and vals['time_booking_ids'] and vals['time_booking_ids'][0] and vals['time_booking_ids'][0][2]:
                if vals['time_booking_ids'][0][2]['booking_date']:
                    from datetime import datetime
                    d1 = datetime.strptime(str(now), "%Y-%m-%d")
                    d2 = datetime.strptime(vals['time_booking_ids'][0][2]['booking_date'], "%Y-%m-%d")
                    if customer_booking_days and customer_booking_days > 0:
                        if int(customer_booking_days) > abs((d2 - d1).days):
                            raise Warning(_("Staff are not allowed to book %s days in advance for this Customer due to the restriction of Penalty days for Non-VIP Customers. Please inform the Customer / contact your admin for further assistance.") % customer_booking_days)
            else:
                if vals['booking_type'] in ['special', 'sic'] and vals['start_date_time']:
                    import datetime
                    dt = datetime.datetime.strptime(vals['start_date_time'],'%Y-%m-%d %H:%M:%S')
                    d3 = dt.date()
                    from datetime import datetime
                    d2 = datetime.strptime(str(d3), "%Y-%m-%d")
                    if customer_booking_days and customer_booking_days > 0:
                        if int(customer_booking_days) > abs((d2 - d1).days):
                            raise Warning(_("Staff are not allowed to book %s days in advance for this Customer due to the restriction of Penalty days for Non-VIP Customers. Please inform the Customer / contact your admin for further assistance.") % customer_booking_days)

        vals['booking_no'] = self.env['ir.sequence'].next_by_code('project.booking') or _('New')
        if vals and 'partner_id' in vals:
            user_id_current = self.env['res.users'].search([('partner_id', '=', vals['partner_id'])])
            if user_id_current:
                vals['user_id'] =  user_id_current.id
        result = super(project_booking, self).create(vals)
        return result

    @api.multi
    def write(self, vals):
        if vals and 'status' in vals.keys():
            if vals['status'] == 'cancelled':
                vals.update({'user_tester_id': False, 'tester_id': False})
                if self.booking_type == 'normal':
                    for a in self.time_booking_ids:
                        a.unlink()
        if vals and 'partner_id' in vals:
            user_id_current = self.env['res.users'].search([('partner_id', '=', vals['partner_id'])])
            if user_id_current:
                vals['user_id'] =  user_id_current.id
        res = super(project_booking, self).write(vals)
        import datetime
        now = datetime.datetime.now().strftime ("%Y-%m-%d")
        from datetime import datetime
        d1 = datetime.strptime(str(now), "%Y-%m-%d")
        customer_booking_days = self.env['ir.values'].get_default('admin.configuration', 'customer_booking_days')
        if vals and 'is_final' in vals.keys():
            if vals['is_final'] == True:
                if self.booking_type in ['normal']:
                    from datetime import datetime
                    d1 = datetime.strptime(str(now), "%Y-%m-%d")
                    d2 = False
                    for nn in self.time_booking_ids:
                        if d2 == False:
                            d2 = datetime.strptime(str(nn.booking_date), "%Y-%m-%d")
                    if customer_booking_days and customer_booking_days > 0:
                        if not int(customer_booking_days) < abs((d2 - d1).days):
                            self.status = 'reconfirmed'
                    else:
                        self.status = 'reconfirmed'
                if self.booking_type in ['special', 'sic'] and self.start_date_time:
                    import datetime
                    local = pytz.timezone(self.env.user.tz)
                    convert_time = datetime.datetime.strptime(self.start_date_time,'%Y-%m-%d %H:%M:%S')
                    start_date = local.localize(convert_time, is_dst=None).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                    dt = datetime.datetime.strptime(start_date,'%Y-%m-%d %H:%M:%S')
                    d3 = dt.date()
                    from datetime import datetime
                    d2 = datetime.strptime(str(d3), "%Y-%m-%d")
                    if customer_booking_days and customer_booking_days > 0:
                        if not int(customer_booking_days) < abs((d2 - d1).days):
                            self.status = 'reconfirmed'
                    else:
                        self.status = 'reconfirmed'
        return res
