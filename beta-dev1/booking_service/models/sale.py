# -*- coding: utf-8 -*-

from odoo import models,fields,api,_
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError

class SaleEmployees(models.Model):
    _name = 'sale.employees'
    
    employee_id = fields.Many2one('hr.employee','Employee')
    sale_id = fields.Many2one('sale.order','Sale')
    picking_id = fields.Many2one('stock.picking')
    
class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    is_booking = fields.Boolean("Is Booking")
    booking_team_id = fields.Many2one("team.management",'Team')
    leader_id = fields.Many2one("hr.employee","Team leader")
#     employee_ids = fields.Many2many("hr.employee","sale_order_employees_rel",'sale_id','employee_id',"Employees")
    employee_ids = fields.One2many('sale.employees','sale_id','Employees')
    equipments_ids = fields.One2many("team.equipmemnts",'sale_id','Equipments') 
    date_start = fields.Datetime("Booking Start Date")
    date_end = fields.Datetime("Booking End Date")
        
    @api.onchange("booking_team_id")
    def booking_team_change(self):
        team_id = self.booking_team_id
        if team_id:
            if team_id.leader_id:
                self.leader_id = team_id.leader_id.id 
            equipment_lines = self.env['team.equipmemnts'].browse() 
            for equipment in self.booking_team_id.team_equipments:
                equipment_lines += equipment.new({'product_id':equipment.product_id.id,'serial_no':equipment.serial_no.id}) 
            self.equipments_ids = equipment_lines
            sale_employee = self.env['sale.employees']
            employees = self.env['sale.employees'].browse()
            for employee in team_id.team_employees:
                employees += sale_employee.new({'employee_id':employee.id})
            self.employee_ids = employees
            
    @api.onchange("date_start")
    def date_start_change(self):
        if self.date_start: 
            start_date = datetime.strptime(self.date_start,"%Y-%m-%d %H:%M:%S")
            end_date = start_date +relativedelta(hours=1)
            self.date_end = end_date.strftime("%Y-%m-%d %H:%M:%S")
            
#     def check_date_overlapping(self,start_date,end_date):

    @api.multi
    def button_check(self):
        ctx = self._context.copy()
        from_action_confirm = ctx.get("from_action_confirm")
        for order in self:
            order_serial_numbers = []
            for equipment in order.equipments_ids:
                order_serial_numbers.append(equipment.serial_no.id)
            order_employees = []
            for empl in order.employee_ids:
                order_employees.append(empl.employee_id.id)
                
            lower_date = datetime.strptime(order.date_start,"%Y-%m-%d %H:%M:%S")
            lower_date = lower_date.date()
            higher_date = datetime.strptime(order.date_end,"%Y-%m-%d %H:%M:%S")
            higher_date = higher_date.date()
            events =  self.env['calendar.event'].search(['|',('employee_ids','in',order_employees),('serial_ids', 'in', order_serial_numbers)])
            event_overlaps = []
            #Here We have compared event overlapping on base of date only, not on datetime
            #So if any event is over earlier then start time of order booking, but the date is same
            #Such event will be consider as Overlap event
            for event in events:
                #We have take Start and Stop date interval of each event and check that its duration has overlapped on order booking dates or not.
                #Suppose, any event is from 14th SEP 2017 to 17th SEP 2017, we have take all dates between this range and compare it wth booking date range of order.
                if event.start_datetime:
                    event_start_date = datetime.strptime(event.start_datetime,"%Y-%m-%d %H:%M:%S")
                    event_start_date = event_start_date.date()
                    event_stop_date = datetime.strptime(event.stop_datetime,"%Y-%m-%d %H:%M:%S")
                    event_stop_date = event_stop_date.date()
                    for day in range((event_stop_date - event_start_date).days + 1):
                        event_date = (event_start_date + timedelta(days=day))
                        if event_date >= lower_date and event_date <= higher_date:  
                            event_overlaps.append(event)
            msg = ''
            event_serial_numbers = []
            event_employees = []
#             events = self.env['calendar.event'].search(domain)
            
            for event in event_overlaps:
                event_serial_numbers += map(int,event.serial_ids)
                event_employees += map(int,event.employee_ids) 
            if event_serial_numbers:
                combine_equipments = set(order_serial_numbers) & set(event_serial_numbers)
                combine_equipments = self.env['stock.production.lot'].browse(list(combine_equipments))
                msg = ', '.join(map(lambda x:'Equipment '+x.name +" ,",combine_equipments))
            if event_employees:
                combine_employees = set(order_employees) & set(event_employees)
                combine_employees = self.env['hr.employee'].browse(combine_employees)
#                 event_equipments = combine_equipments & events.mapped('serial_number_ids')
                msg += ', '.join(map(lambda x:'Employee '+x.name + " ,",combine_employees))
            if msg:
                msg += " has an event on that day and time."
                msg+=" Are you sure you want to validate?"
            
                if not from_action_confirm:
                    raise ValidationError(_(msg))            
            else:
                if not from_action_confirm:
                    raise ValidationError(_("Everyone is available for the booking."))
            if from_action_confirm and msg:
                view_ref = self.env.ref('booking_service.event_overlap_warning_form')
                view_id = view_ref and view_ref.id or False,
                ctx = self._context.copy()
                ctx.update({'warning_message':msg})
                return {
                    'type': 'ir.actions.act_window',
                    'name': _('Event Overlap Warning'),
                    'res_model': 'event.overlap.warning',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': view_id,
                    'target': 'new',
                    'context': ctx,
                    }
        return True
            
            
    @api.multi
    def action_confirm(self):
        ctx = self._context.copy()
        ctx.update({'from_action_confirm':True})
        if not ctx.get('process_event_booking'):
            res = self.with_context(ctx).button_check()
            if type(res)==dict:
                return res
        result = super(SaleOrder,self).action_confirm()
        if self.picking_ids and self.is_booking:
            equipment_lines = [] 
            for equipment in self.booking_team_id.equipments_ids:
                equipment_lines.append((0,0,{'product_id':equipment.product_id.id,
                                              'serial_no':equipment.serial_no.id,
                                              }))
            employee_lines = []
            for employee in self.booking_team_id.employee_ids:
                employee_lines.append((0,0,{'employee_id':employee.employee_id.id}))                
                
            self.picking_ids.write({
                                    'is_booking':self.is_booking,
                                    'booking_team_id':self.booking_team_id and self.booking_team_id.id or False,
                                    'leader_id':self.team_leader_id and self.team_leader_id.id or False,
                                    'start_date_schedule':self.date_start,
                                    'end_date_schedule':self.date_end,
                                    'start_date_actual':self.date_start,
                                    'end_date_actual':self.date_end,                                    
                                    'equipments_ids':equipment_lines,
                                    'employee_ids':employee_lines,
                                    }) 
        return result 
              