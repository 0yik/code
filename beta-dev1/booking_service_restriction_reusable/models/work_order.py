# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class work_order_resable(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def action_todo(self):
        try:
            self.action_check()
        except ValidationError as e:
            if e.name == 'Everyone is available for the booking':
                self.action_create_calendar()

                booking_setting_obj = self.env['booking.settings'].search([], order='id desc', limit=1)
                booking_work_order = self.env['stock.picking'].search(
                    [('is_booking', '=', True), ('id', '!=', self.id), ('state', '=', 'pending')])
                allowed = False
                for work_order in booking_work_order:
                    employees_exist = False
                    for sales_order_employees in self.team_employees:
                        for work_order_employees in work_order.team_employees:
                            if sales_order_employees.employee_id.id == work_order_employees.employee_id.id:
                                employees_exist = True

                    equipments_exist = False
                    for sales_order_employees in self.product_ids:
                        for work_order_employees in work_order.product_ids:
                            if sales_order_employees.product_id == work_order_employees.product_id and sales_order_employees.lot_id == work_order_employees.lot_id:
                                equipments_exist = True

                    time_exist = False
                    if self.scheduled_start >= work_order.scheduled_start and self.scheduled_start < work_order.scheduled_end:
                        time_exist = True
                    if self.scheduled_end > work_order.scheduled_start and self.scheduled_end <= work_order.scheduled_end:
                        time_exist = True
                    if work_order.scheduled_start >= self.scheduled_start and work_order.scheduled_start < self.scheduled_end:
                        time_exist = True
                    if work_order.scheduled_end > self.scheduled_start and work_order.scheduled_end <= self.scheduled_end:
                        time_exist = True

                    if time_exist == True:
                        if employees_exist == True and booking_setting_obj.block_by_worker == True:
                            allowed = True
                            break
                        if equipments_exist == True and booking_setting_obj.blook_by_equipment == True:
                            allowed = True
                            break
                if allowed == False:
                    self.action_confirm()
                    self.is_validated = True
                    self.state = 'pending'

            else:
                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'work.order.wizard',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {'default_noti': e.name + ', are you sure you want to validate?'}
                }
        return True


class work_order_wizard_resable(models.TransientModel):
    _inherit = 'work.order.wizard'

    @api.multi
    def action_confirm(self):
        context = self.env.context
        if context.get('active_id', False) and context.get('active_model', False) == 'stock.picking':
            picking = self.env['stock.picking'].browse(context.get('active_id'))
            picking.action_create_calendar()

            booking_setting_obj = self.env['booking.settings'].search([], order='id desc', limit=1)
            booking_work_order = self.env['stock.picking'].search(
                [('is_booking', '=', True), ('id', '!=', picking.id), ('state', '=', 'pending')])
            allowed = False
            for work_order in booking_work_order:
                employees_exist = False
                for sales_order_employees in picking.team_employees:
                    for work_order_employees in work_order.team_employees:
                        if sales_order_employees.employee_id.id == work_order_employees.employee_id.id:
                            employees_exist = True

                equipments_exist = False
                for sales_order_employees in picking.product_ids:
                    for work_order_employees in work_order.product_ids:
                        if sales_order_employees.product_id == work_order_employees.product_id and sales_order_employees.lot_id == work_order_employees.lot_id:
                            equipments_exist = True

                time_exist = False
                if picking.scheduled_start >= work_order.scheduled_start and picking.scheduled_start < work_order.scheduled_end:
                    time_exist = True
                if picking.scheduled_end > work_order.scheduled_start and picking.scheduled_end <= work_order.scheduled_end:
                    time_exist = True
                if work_order.scheduled_start >= picking.scheduled_start and work_order.scheduled_start < picking.scheduled_end:
                    time_exist = True
                if work_order.scheduled_end > picking.scheduled_start and work_order.scheduled_end <= picking.scheduled_end:
                    time_exist = True

                if time_exist == True:
                    if employees_exist == True and booking_setting_obj.block_by_worker == True:
                        allowed = True
                        break
                    if equipments_exist == True and booking_setting_obj.blook_by_equipment == True:
                        allowed = True
                        break
            if allowed == False:
                picking.action_confirm()
                picking.is_validated = True
                picking.state = 'pending'
        return True