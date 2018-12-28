
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime

class Working_order(models.Model):
    _inherit = "stock.picking"

    is_a_booking = fields.Boolean('Is Booking')
    scheduled_start =fields.Datetime('Scheduled Start Date')
    scheduled_end =fields.Datetime('Scheduled End Date')
    actual_start=fields.Datetime('Actual Start')
    actual_end=fields.Datetime('Actual End')
    booking_team_id = fields.Many2one('booking.team',string="Team")
    team_leader_id = fields.Many2one('hr.employee',string="Team Leader")
    employee_ids = fields.Many2many('hr.employee',string="Employess")
    equipment_serial_ids = fields.Many2many('equipment.serial',string="Equipments")
    state = fields.Selection([
        ('draft', 'Draft'), ('cancel', 'Cancelled'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting Availability'),
        ('partially_available', 'Partially Available'),
        ('assigned', 'Started'), ('done', 'Done')], string='Status', compute='_compute_state',
        copy=False, index=True, readonly=True, store=True, track_visibility='onchange',
        help=" * Draft: not confirmed yet and will not be scheduled until confirmed\n"
             " * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n"
             " * Waiting Availability: still waiting for the availability of products\n"
             " * Partially Available: some products are available and reserved\n"
             " * Ready to Transfer: products reserved, simply waiting for confirmation.\n"
             " * Transferred: has been processed, can't be modified or cancelled anymore\n"
             " * Cancelled: has been cancelled, can't be confirmed anymore")



    @api.multi
    def start(self):
        self.write({'state':'assigned'})
        self.actual_start=datetime.now()    
        
    @api.multi
    def check(self):
        for record in self:
            employees = []
            bulid_string = ''
            if self.team_leader_id.has_event() and "Employee %s, "%(self.team_leader_id.name) not in bulid_string:
                bulid_string = "%sEmployee %s, "%(bulid_string,self.team_leader_id.name)
            for employee in self.employee_ids:
                if employee.has_event()  and "Employee %s, "%(self.team_leader_id.name) not in bulid_string:
                    bulid_string = "%sEmployee %s, "%(bulid_string,employee.name)
            for equipment_serial in self.equipment_serial_ids:
                if equipment_serial.has_event():
                    bulid_string = "%sEquipment %s, "%(bulid_string,equipment_serial.product_id.name)
            if len(bulid_string) >= 2:
                bulid_string = bulid_string[:len(bulid_string)-2]
                bulid_string = "%s has an event on %s"%(bulid_string,datetime.now())
                raise ValidationError(_(bulid_string))

    @api.multi
    def do_new_transfer(self):
        res=super(Working_order,self).do_new_transfer()
        self.actual_end=datetime.now()
        return res


    @api.multi
    def write(self,vals):
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
        
        
        return super(Working_order,self).write(vals)


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
        print vals
    	return super(Working_order, self).create(vals)

    @api.onchange('booking_team_id')
    def onchange_booking_team(self):
    	if not self.booking_team_id:
    		return
    	
    	self.team_leader_id = self.booking_team_id.team_leader_id
    	self.employee_ids = self.booking_team_id.employee_ids
    	self.equipment_serial_ids = self.booking_team_id.equipment_serial_ids
