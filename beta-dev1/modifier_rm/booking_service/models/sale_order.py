# -*- coding: utf-8 -*-

from odoo import models,fields,api,_
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
class sale_order(models.Model):
    _inherit = 'sale.order'
    
    is_booking = fields.Boolean("Is A Booking",default=False)
    booking_team_id = fields.Many2one("booking.team",'Team')
    team_leader_id = fields.Many2one("hr.employee","Team leader")
    
    employee_ids = fields.Many2many("hr.employee","booking_team_sale_order_rel",'sale_order_id','employee_id',"Employees")
    equipments_ids = fields.One2many("equipment.lines",'sale_order_id','Equipments') 
    
    booking_start_date = fields.Datetime("Booking Start")
    booking_end_date = fields.Datetime("Booking End")
    
    @api.model
    def create(self,vals):
        employee_ids = vals.get('employee_ids',[])
        new_emp_ids = []
        for emp in employee_ids:
            if len(emp)==3 and emp[0]==1:
                new_emp_ids.append(emp[1])
        if new_emp_ids:
            vals.update({'employee_ids':[(6,0,new_emp_ids)]})
        return super(sale_order,self).create(vals)
    @api.multi
    def write(self,vals):
        employee_ids = vals.get('employee_ids',[])
        new_emp_ids = []
        for emp in employee_ids:
            if len(emp)==3 and emp[0]==1:
                new_emp_ids.append(emp[1])
        if new_emp_ids:
            vals.update({'employee_ids':[(6,0,new_emp_ids)]})        
        return super(sale_order,self).write(vals)
    
    @api.onchange("booking_team_id")
    def onchange_booking_team_id(self):
        if self.booking_team_id:
            if self.booking_team_id.team_leader_id:
                self.team_leader_id = self.booking_team_id.team_leader_id.id
            equipment_line = self.env['equipment.lines']
            equipment_lines = equipment_line.browse() 
            for equipment in self.booking_team_id.equipments_ids:
                equipment_lines += equipment.new({'product_id':equipment.product_id.id,
                                                  'serial_no_id':equipment.serial_no_id.id,
                                                  #'sale_order_id':self.id
                                                  }) 
            self.equipments_ids = equipment_lines
            self.employee_ids = [(6,0,self.booking_team_id.employee_ids.ids)] #self.booking_team_id.employee_ids  
            
    @api.onchange("booking_start_date")
    def onchange_booking_start_date(self):
        if self.booking_start_date:
            start_date = datetime.strptime(self.booking_start_date,"%Y-%m-%d %H:%M:%S")
            end_date = start_date +relativedelta(hours=1)
            self.booking_end_date = end_date.strftime("%Y-%m-%d %H:%M:%S")
            
    @api.multi
    def action_confirm(self):
        ctx = self._context.copy()
        ctx.update({'from_action_confirm':True})
        if not ctx.get('process_event_booking'):
            res = self.with_context(ctx).action_check_booking()
            if type(res)==dict:
                return res
        result = super(sale_order,self).action_confirm()
        if self.picking_ids and self.is_booking:
            equipment_lines = [] 
            for equipment in self.booking_team_id.equipments_ids:
                equipment_lines.append((0,0,{'product_id':equipment.product_id.id,
                                              'serial_no_id':equipment.serial_no_id.id,
                                              }))
                
            self.picking_ids.write({'is_booking':self.is_booking,
                                    'booking_team_id':self.booking_team_id and self.booking_team_id.id or False,
                                    'team_leader_id':self.team_leader_id and self.team_leader_id.id or False,
                                    'employee_ids':self.employee_ids and [(6,0,self.employee_ids.ids)] or False,
                                    'equipments_ids':equipment_lines,
                                    'scheduled_start_date':self.booking_start_date,
                                    'scheduled_end_date':self.booking_end_date,
                                    'actual_start_date':self.booking_start_date,
                                    'actual_end_date':self.booking_end_date,
                                    }) 
        return result 
    
    @api.multi
    def action_check_booking(self):
        ctx = self._context.copy()
        from_action_confirm = ctx.get("from_action_confirm")
        for order in self:
            equipments = order.equipments_ids.mapped("serial_no_id")
            domain = [
                        ('serial_number_ids', 'in', equipments.ids),
                    '|','&',
                        ('start_date', '>=', order.booking_start_date),
                        ('stop_date', '<=', order.booking_end_date),
                        '&',
                        ('start_datetime', '>=', order.booking_start_date),
                        ('stop_datetime', '<=', order.booking_end_date),
                    ]
            
            msg = ''
            events = self.env['calendar.event'].search(domain)
            if events:
                event_equipments = equipments & events.mapped('serial_number_ids')
                msg = ', '.join(map(lambda x:'Equipment '+x.name,event_equipments))
                msg += " has an event on that day and time."
                if not from_action_confirm:
                    raise ValidationError(_(msg))
                msg+=" Are you sure you want to validate?"
                
            else:
                if not from_action_confirm:
                    raise ValidationError(_("Everyone is available for the booking."))
            if from_action_confirm and msg:
                view_ref = self.env.ref('booking_service.view_booking_event_warning_form')
                view_id = view_ref and view_ref.id or False,
                
                ctx = self._context.copy()
                ctx.update({'warning_message':msg})
                return {
                    'type': 'ir.actions.act_window',
                    'name': _('Warning'),
                    'res_model': 'booking.event.warning',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': view_id,
                    'target': 'new',
                    'context': ctx,
                    }
        return True
          