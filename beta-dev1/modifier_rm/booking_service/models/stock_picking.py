# -*- coding: utf-8 -*-

from odoo import models,fields,api
from datetime import datetime
from odoo.exceptions import ValidationError
from __builtin__ import True

class stock_picking(models.Model):
    _inherit = 'stock.picking'
    
    is_booking = fields.Boolean("Is A Booking",default=False)
    
    scheduled_start_date = fields.Datetime("Scheduled Start")
    scheduled_end_date = fields.Datetime("Scheduled End")
    actual_start_date = fields.Datetime("Actual Start")
    actual_end_date = fields.Datetime("Actual End")
    
    booking_team_id = fields.Many2one("booking.team",'Team')
    team_leader_id = fields.Many2one("hr.employee","Team leader")
    
    employee_ids = fields.Many2many("hr.employee","booking_team_stock_picking_rel",'picking_id','employee_id',"Employees")
    equipments_ids = fields.One2many("equipment.lines",'picking_id','Equipments')
    
    
    @api.model
    def create(self,vals):
        employee_ids = vals.get('employee_ids',[])
        new_emp_ids = []
        for emp in employee_ids:
            if len(emp)==3 and emp[0]==1:
                new_emp_ids.append(emp[1])
        if new_emp_ids:
            vals.update({'employee_ids':[(6,0,new_emp_ids)]})
        return super(stock_picking,self).create(vals)
    
    @api.multi
    def write(self,vals):
        employee_ids = vals.get('employee_ids',[])
        new_emp_ids = []
        for emp in employee_ids:
            if len(emp)==3 and emp[0]==1:
                new_emp_ids.append(emp[1])
        if new_emp_ids:
            vals.update({'employee_ids':[(6,0,new_emp_ids)]})        
        return super(stock_picking,self).write(vals)
    
    @api.multi
    def action_start_work_order(self):
        
        return
    @api.multi
    def do_new_transfer(self):
        if self.state=='assigned':
            self.actual_end_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return super(stock_picking,self).do_new_transfer()
    
    
    @api.multi
    def action_confirm(self):
        ctx = self._context.copy()
        ctx.update({'from_action_confirm':True})
        if not ctx.get('process_event_booking'):
            res = self.with_context(ctx).action_check_booking()
            if type(res)==dict:
                return res
        result = super(stock_picking,self).action_confirm()
        return result 
    
    @api.multi
    def action_check_booking(self):
        ctx = self._context.copy()
        from_action_confirm = ctx.get("from_action_confirm")
        for picking in self:
            equipments = picking.equipments_ids.mapped("serial_no_id")
            domain = [
                        ('serial_number_ids', 'in', equipments.ids),
                    '|','&',
                        ('start_date', '>=', picking.scheduled_start_date),
                        ('stop_date', '<=', picking.scheduled_end_date),
                        '&',
                        ('start_datetime', '>=', picking.scheduled_start_date),
                        ('stop_datetime', '<=', picking.scheduled_end_date),
                    ]
            msg = ''
            events = self.env['calendar.event'].search_count(domain)
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
      