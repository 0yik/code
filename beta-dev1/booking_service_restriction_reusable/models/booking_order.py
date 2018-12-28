# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class booking_order_resable(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_todo(self):
        try:
            self.action_check()
        except ValidationError as e:
            if e.name == 'Everyone is available for the booking':
                self.action_create_calendar()

                booking_setting_obj = self.env['booking.settings'].search([], order='id desc', limit=1)
                booking_work_order = self.env['sale.order'].search(
                    [('is_booking', '=', True), ('id', '!=', self.id),('state','=','sale')])
                allowed = False
                for work_order in booking_work_order:
                    employees_exist = False
                    for sales_order_employees in self.team_employees:
                        for work_order_employees in work_order.team_employees:
                            if sales_order_employees.employee_id.id == work_order_employees.employee_id.id:
                                employees_exist = True

                    equipments_exist = False
                    for sales_order_employees in self.equipment_ids:
                        for work_order_employees in work_order.equipment_ids:
                            if sales_order_employees.product_id == work_order_employees.product_id and sales_order_employees.lot_id == work_order_employees.lot_id:
                                equipments_exist = True

                    time_exist = False
                    if self.start_date > work_order.start_date and self.start_date < work_order.end_date:
                        time_exist = True
                    if self.end_date > work_order.start_date and self.end_date < work_order.end_date:
                        time_exist = True
                    if work_order.start_date > self.start_date and work_order.start_date < self.end_date:
                        time_exist = True
                    if work_order.end_date > self.start_date and work_order.end_date < self.end_date:
                        time_exist = True

                    if time_exist == True:
                        if employees_exist == True and booking_setting_obj.block_by_worker == True:
                            allowed = True
                            break
                        if equipments_exist == True and booking_setting_obj.blook_by_equipment == True:
                            allowed = True
                            break
                if allowed == False:
                    self.action_confirm_record()
            else:
                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'booking.order.wizard',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {'default_noti': e.name + ', are you sure you want to validate?'}
                }
        return True


class booking_order_wizard_resable(models.TransientModel):
    _inherit = 'booking.order.wizard'

    @api.multi
    def action_confirm(self):
        context = self.env.context
        if context.get('active_id', False) and context.get('active_model', False) == 'sale.order':
            booking = self.env['sale.order'].browse(context.get('active_id'))
            booking.action_create_calendar()

            booking_setting_obj = self.env['booking.settings'].search([], order='id desc', limit=1)
            booking_work_order = self.env['sale.order'].search([('is_booking', '=', True),('id','!=',booking.id),('state','=','sale')])
            allowed = False
            for work_order in booking_work_order:
                employees_exist = False
                for sales_order_employees in booking.team_employees:
                    for work_order_employees in work_order.team_employees:
                        if sales_order_employees.employee_id.id == work_order_employees.employee_id.id:
                            employees_exist = True

                equipments_exist = False
                for sales_order_employees in booking.equipment_ids:
                    for work_order_employees in work_order.equipment_ids:
                        if sales_order_employees.product_id == work_order_employees.product_id and sales_order_employees.lot_id == work_order_employees.lot_id:
                            equipments_exist = True

                time_exist = False
                if booking.start_date > work_order.start_date and booking.start_date < work_order.end_date:
                    time_exist = True
                if booking.end_date > work_order.start_date and booking.end_date < work_order.end_date:
                    time_exist = True
                if work_order.start_date > booking.start_date and work_order.start_date < booking.end_date:
                    time_exist = True
                if work_order.end_date > booking.start_date and work_order.end_date < booking.end_date:
                    time_exist = True



                if time_exist == True:
                    if employees_exist == True and booking_setting_obj.block_by_worker == True:
                        allowed = True
                        break
                    if equipments_exist == True and booking_setting_obj.blook_by_equipment == True:
                        allowed = True
                        break
            if allowed == False:
                booking.action_confirm_record()

        return True



