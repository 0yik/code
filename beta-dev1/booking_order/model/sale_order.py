from odoo import models, fields, api
from datetime import datetime
from datetime import timedelta
from pytz import timezone
import pytz
class SaleOrder(models.Model):
    
    _inherit = "sale.order"

    is_booking = fields.Boolean('Is a Booking')

    booking_team_id = fields.Many2one('booking.team',string="Team")
    team_leader_id = fields.Many2one('hr.employee',string="Team Leader")
    employee_ids = fields.Many2many('hr.employee',string="Employess")
    equipment_serial_ids = fields.Many2many('equipment.serial',string="Equipments")
    booking_start = fields.Datetime("Booking Start")
    booking_end = fields.Datetime("Booking End")

    @api.model
    def create(self,vals):
    	emp_list = vals.pop('employee_ids',[])
    	equipment_list = vals.get('equipment_serial_ids',[])
        vals.pop('equipment_serial_ids',[])
        if len(equipment_list) >= 1:
            if type(equipment_list[0][2]) is dict:
                qe_ls = [6,False,[]]
                for eq_list in equipment_list:
                    qe_ls[2].append(eq_list[1])
                equipment_list = qe_ls
            else:
                equipment_list = equipment_list[0]
        else:
            equipment_list = equipment_list[0]
    	emp_ids = []
    	quip_ids = []

    	for employee in emp_list:
            if type(employee[2]) is list:
                for emp_id in employee[2]:
                    emp_ids.append(emp_id)
            else:
                emp_ids.append(employee[2])
    	if emp_ids:
    		vals.update({'employee_ids':[(6,0,emp_ids)]})
    	for equipment in equipment_list[2]:
    		quip_ids.append(equipment)
    	if quip_ids:
    		vals.update({'equipment_serial_ids':[(6,0,quip_ids)]})
    	return super(SaleOrder, self).create(vals)
    	
    @api.multi
    def write(self,vals):
        # print vals
        emp_list_val=vals.get('employee_ids')
        equipment_list_val=vals.get('equipment_serial_ids')
        if emp_list_val:
            emp_list = vals.pop('employee_ids',[])
            emp_ids = []
            for employee in emp_list:
                if type(employee[2]) is list:
                    for emp_id in employee[2]:
                        emp_ids.append(emp_id)
                else:
                    emp_ids.append(employee[2])
            if emp_ids:
                vals.update({'employee_ids':[(6,0,emp_ids)]})
            
        if equipment_list_val:
            quip_ids = []
            equipment_list = vals.pop('equipment_serial_ids',[])
            for equipment in equipment_list:
                if type(equipment[2]) is list:
                    for eqp_id in equipment[2]:
                        quip_ids.append(eqp_id)
                else:
                    quip_ids.append(equipment[2])
            if quip_ids:
                vals.update({'equipment_serial_ids':[(6,0,quip_ids)]})
        return super(SaleOrder,self).write(vals)

    @api.onchange('booking_team_id')
    def onchange_booking_team(self):
    	if not self.booking_team_id:
    		return
    	
    	self.team_leader_id = self.booking_team_id.team_leader_id
    	self.employee_ids = self.booking_team_id.employee_ids
    	self.equipment_serial_ids = self.booking_team_id.equipment_serial_ids


class BookingTeam(models.Model):

	_name = 'booking.team'

	_description = "Team information"

	name = fields.Char("Name",required=True)
	team_leader_id = fields.Many2one('hr.employee',string="Team Leader")
	employee_ids = fields.Many2many('hr.employee',string="Employess")
	equipment_serial_ids = fields.Many2many('equipment.serial',string="Equipments")

class EquipmentSerial(models.Model):
    _name = 'equipment.serial'

    product_id = fields.Many2one('product.template',string="Product")
    serial_id = fields.Many2one('stock.production.lot',string="Serial")
    
    @api.multi
    def has_event(self):
        if not self:
            return
        datetime_now = datetime.utcnow()
        event = self.serial_id.calendar_id
        event = self.env['calendar.event'].with_context(tz='UTC').browse(event.id)
        event_start_time = event.start_datetime and datetime.strptime(event.start_datetime, '%Y-%m-%d %H:%M:%S')
        if event_start_time:
            event_end_time = event_start_time + timedelta(hours=event.duration)
            time_record =  self.env['booking.order.settings'].search([],limit=1)
            effective_start_time = event_start_time - timedelta(minutes=time_record.pre_booking)
            effective_end_time = event_end_time + timedelta(hours=time_record.post_booking)
            if datetime_now >= effective_start_time and datetime_now <= effective_end_time:
                return True
                
        return False