# -*- coding: utf-8 -*-

import time
import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning

class FleetRequest(models.Model):
    _name = 'fleet.request'
    _description = 'Fleet Request'
    _order = 'id desc'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    
#     @api.model
#     def _get_years(self):
#         yearl = []
#         for i in range(1950, 2025):
#             yearl.append((i, i))
#         return yearl
    
    
    year_selecion = [(i, i) for i in range(1950, 2025)]
    
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('fleet.request') or 'New'
        return super(FleetRequest, self).create(vals)
    
    @api.multi
    @api.depends('timesheet_line_ids.unit_amount')
    def _compute_total_spend_hours(self):
        for rec in self:
            spend_hours = 0.0
            for line in rec.timesheet_line_ids:
                spend_hours += line.unit_amount
            rec.total_spend_hours = spend_hours
    
    @api.onchange('project_id')
    def onchnage_project(self):
        for rec in self:
            rec.analytic_account_id = rec.project_id.analytic_account_id
          
    @api.one
    def set_to_close(self):
        if self.is_close != True:
            self.is_close = True
            self.close_date = fields.Datetime.now()#time.strftime('%Y-%m-%d')
            self.state = 'closed'
            template = self.env.ref('fleet_repair_request_management.email_template_fleet_repair_requested')
            template.send_mail(self.id, force_send=True)
            
    @api.one
    def set_to_reopen(self):
        if self.is_close != False:
            self.is_close = False
            self.state = 'open'
    
    name = fields.Char(
        string='Number', 
        required=False,
        default='New',
        copy=False, 
        readonly=True, 
    )
    state = fields.Selection(
        [('new','New'),
         ('need_to_repair','Need To Repair'),
         ('communication_claim_opening','Communication Claim Opening'),
         ('workshop_choice','Workshop Choice'),
         ('workshop_entry','Workshop Entry/Out Schedule Contact'),
         ('budget_evaluation','Budget Evaluation'),
         ('authorization','Authorization'),
         ('expert','Expert'),
         ('reparation','Reparation'),
         ('workshop_management_system','Workshop Management System'),
         ('billing','Billing'),
         ('delivery_output_date','Delivery Output Date'),
         ('vehicle_tracking_customer_satisfaction','Vehicle Tracking Customer Satisfaction'),
         ('open','Open'),
         ('closed','Closed')],
        track_visibility='onchange',
        default='new',
        copy=False, 
    )
#     customer_id = fields.Many2one(
#         'res.partner',
#         string="Customer", 
#         required=True,
#     )
    email = fields.Char(
        string="Email",
        required=True
    )
    phone = fields.Char(
        string="Phone"
    )
    category = fields.Selection(
        [('technical', 'Technical'),
        ('functional', 'Functional'),
        ('repair', 'Repair')],
        string='Category',
    )
    subject = fields.Char(
        string="Subject"
    )
    description = fields.Text(
        string="Description"
    )
    priority = fields.Selection(
        [('0', 'Low'),
        ('1', 'Middle'),
        ('2', 'High')],
        string='Priority',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
    )
    request_date = fields.Datetime(
        string='Create Date',
        default=fields.Datetime.now,
        copy=False,
    )
    close_date = fields.Datetime(
        string='Close Date',
    )
    user_id = fields.Many2one(
        'res.users',
        string='Technician',
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Department'
    )
    timesheet_line_ids = fields.One2many(
        'account.analytic.line',
        'fleet_request_id',
        string='Timesheets',
    )
    is_close = fields.Boolean(
        string='Is Repair Closed ?',
        track_visibility='onchange',
        default=False,
        copy=False,
    )
    total_spend_hours = fields.Float(
        string='Total Hours Spent',
        compute='_compute_total_spend_hours'
    )
    project_id = fields.Many2one(
        'project.project',
        string='Project',
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
    )
    team_id = fields.Many2one(
        'fleet.team',
        string='Fleet Team',
    )
    team_leader_id = fields.Many2one(
        'res.users',
        string='Team Leader',
#         related ='team_id.leader_id',
#         store=True,
    )
    #invoice_line_ids = fields.One2many(
        #'support.invoice.line',
        #'support_id',
        #string='Invoice Lines',
    #)
    journal_id = fields.Many2one(
        'account.journal',
         string='Invoice Journal',
     )
    invoice_id = fields.Many2one(
        'account.invoice',
         string='Invoice Reference',
         copy='False',
     )
    is_invoice_created = fields.Boolean(
        string='Is Invoice Created',
        default=False,
    )
    task_id = fields.Many2one(
        'project.task',
        string='Task',
        readonly = True,
    )
    is_task_created = fields.Boolean(
        string='Is Task Created ?',
        default=False,
    )
    company_id = fields.Many2one(
        'res.company', 
        default=lambda self: self.env.user.company_id, 
        string='Company',
        readonly=True,
     )
    comment = fields.Text(
        string='Customer Comment',
        readonly=True,
    )
    rating = fields.Selection(
        [('poor', 'Poor'),
        ('average', 'Average'),
        ('good', 'Good'),
        ('very good', 'Very Good'),
        ('excellent', 'Excellent')],
        string='Customer Rating',
        readonly=True,
    )
    
    #@api.multi
    #@api.depends('analytic_account_id',
                 #'total_consumed_hours',
                 #'total_consumed_hours',
                 #'remaining_hours')
    #def compute_total_hours(self):
        #total_remaining_hours = 0.0
        #for rec in self:
            #rec.total_purchase_hours = rec.analytic_account_id.total_purchase_hours
            #rec.total_consumed_hours = rec.analytic_account_id.total_consumed_hours
            #rec.remaining_hours = rec.analytic_account_id.remaining_hours
    
    total_purchase_hours = fields.Float(
        string='Total Purchase Hours',
        compute='compute_total_hours',
        store=True,
    )
    total_consumed_hours = fields.Float(
        string='Total Consumed Hours',
        compute='compute_total_hours',
        store=True,
    )
    remaining_hours = fields.Float(
        string='Remaining Hours',
        compute='compute_total_hours',
        store=True,
    )
    service_type_ids = fields.Many2many(
        'fleet.service.type',
        string='Service Type',
    )
    
    year = fields.Selection(
        selection=year_selecion,
        string='Year',
    )
    
    model = fields.Many2one(
        'fleet.vehicle.model',
        string="Model",
    )
    mileage = fields.Char(
        string="Current Mileage",
    )
    license_plate = fields.Char(
        string="License Plate",
    )
    make_id = fields.Many2one(
        'fleet.vehicle.model.brand',
        string='Make',
    )
    vehicle_id = fields.Many2one(
        'fleet.vehicle',
        string='Vehicle',
        copy=False,
    )
    vehicle_service_ids = fields.One2many(
        'fleet.vehicle.log.services',
        'fleet_repair_id',
        string='Vehicle Services',
        copy=False,
    )
    repair_id = fields.Many2one(
        'mrp.repair',
        string='Repair Reference',
        copy=False,
        readonly=True,
    )
    event_id = fields.Many2one(
        'calendar.event',
        string='Meeting Reference',
        copy=False,
    )
    
    @api.multi
    @api.depends('vehicle_service_ids')
    def _vehicle_services_count(self):
        for rec in self:
            rec.vehicle_services_count = len(rec.vehicle_service_ids)
            
    vehicle_services_count = fields.Integer(
        compute='_vehicle_services_count', 
        string="Vehicle Services",
        store=True,
    )
    
    @api.multi
    def action_create_fleet_task(self):
        for rec in self:
            fleet_task = {
            'name' : rec.subject +'('+rec.name+')',
            'user_id' : rec.user_id.id,
            'date_deadline' : rec.close_date,
            'project_id' : rec.project_id.id,
            'partner_id' : rec.partner_id.id,
            'description' : rec.description,
            'fleet_id' : rec.id,
            }
            fleet_task_id= self.env['project.task'].sudo().create(fleet_task)
            vals = {
            'task_id' : fleet_task_id.id,
            'is_task_created' : True,
            }
            rec.write(vals)

    @api.multi
    def create_vehicle(self):
        for rec in self:
            if rec.model and rec.license_plate:
                vals = {
                'partner_id': rec.partner_id.id,
                'model_id' : rec.model.id,
                'license_plate' : rec.license_plate,
                'fleet_repair_id' : rec.id,
                }
                fleet_vehicle= self.env['fleet.vehicle'].create(vals)
                rec.vehicle_id = fleet_vehicle.id,
            else:
                raise Warning(_('Please Select The Model and License Plate.'))
    
    @api.multi
    def create_repair_order(self):
        repair = self.env['mrp.repair']
        repair_location = repair._default_stock_location()
        for rec in self:
            if rec.vehicle_id.product_id:
                vals = {
                'partner_id' : rec.partner_id.id,
                'vehicle_id' : rec.vehicle_id.id,
                'product_id' : rec.vehicle_id.product_id.id,
                'product_uom': rec.vehicle_id.product_id.uom_id.id,
                'location_dest_id' : repair_location,
                'fleet_repair_id' : rec.id,
                }
                fleet_vehicle= self.env['mrp.repair'].create(vals)
                vals = {
                'repair_id' : fleet_vehicle.id,
                }
                rec.write(vals)
            else:
                raise Warning(_('Please Set The Related Product on Fleet Vehicles.'))
    
    @api.multi
    def show_fleet_task(self):
        for rec in self:
            res = self.env.ref('project.action_view_task')
            res = res.read()[0]
            res['domain'] = str([('id','=',rec.task_id.id)])
        return res
    
    @api.multi
    def show_repair_order(self):
        for rec in self:
            res = self.env.ref('mrp_repair.action_repair_order_tree')
            res = res.read()[0]
            res['domain'] = str([('id','=',rec.repair_id.id)])
        return res
    
    @api.multi
    def show_fleet_vehicle(self):
        for rec in self:
            res = self.env.ref('fleet.fleet_vehicle_action')
            res = res.read()[0]
            res['domain'] = str([('id','=',rec.vehicle_id.id)])
        return res
    
    @api.multi
    def show_fleet_appointment(self):
        for rec in self:
            res = self.env.ref('calendar.action_calendar_event')
            res = res.read()[0]
            res['domain'] = str([('id','=',rec.event_id.id)])
        return res
    
    @api.multi
    def show_fleet_vehicle_service(self):
        for rec in self:
            res = self.env.ref('fleet.fleet_vehicle_log_services_action')
            res = res.read()[0]
            res['domain'] = str([('fleet_repair_id','=',rec.id)])
        return res
    
    @api.multi
    def show_analytic_account(self):
        for rec in self:
            res = self.env.ref('analytic.action_account_analytic_account_form')
            res = res.read()[0]
            res['domain'] = str([('id','=',rec.analytic_account_id.id)])
        return res
    
class HrTimesheetSheet(models.Model):
    _inherit = 'account.analytic.line'

    fleet_request_id = fields.Many2one(
        'fleet.request',
        domain=[('is_close','=',False)],
        string='Fleet Request',
    )
    billable = fields.Boolean(
        string='Billable',
        default=True,
    )

    # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
