# -*- coding: utf-8 -*-
from openerp import api, exceptions, fields, models, _
import datetime


class WorkOrderReminders(models.Model):
    _name = 'work.order.reminder.app'
    _description = 'Send Reminders to App'

    @api.multi
    def send_update_to_app(self,user_id):
        employee_id = self.env['hr.employee'].search([('resource_id.user_id', '=', user_id)], limit=1).ids
        if not employee_id:
            employee_id = self.env['hr.employee'].search([('user_id', '=', user_id)], limit=1).ids

        date_today = fields.Datetime.from_string(fields.Datetime.now())
        from_date = (date_today + datetime.timedelta(days=1)).replace(hour=00, minute=00, second=01)
        to_date = (date_today + datetime.timedelta(days=1)).replace(hour=23, minute=59, second=59)

        work_order_ids = []
        work_order_employee_ids = self.env['working.order.employee'].search([('employee_id', 'in', employee_id)])
        for temp_obj in work_order_employee_ids:
            if  temp_obj.order_id.scheduled_start >= fields.Datetime.to_string(from_date) and temp_obj.order_id.scheduled_start <= fields.Datetime.to_string(to_date):
                work_order_ids.append(temp_obj.order_id)
        work_order_data = []
        for work_order_obj in  work_order_ids:
            address = work_order_obj.get_work_order_address(work_order_obj)
            vals = {}
            vals['work_order_id'] = work_order_obj.id
            vals['work_order_name'] = work_order_obj.name
            try:
                partner_name = work_order_obj.partner_id.name.encode('utf-8')
            except:
                partner_name = work_order_obj.partner_id.name
            if address:
                try:
                    addr = address.encode('utf-8')
                except:
                    addr = address
                subject = 'Your work order(' + str(work_order_obj.name) + ') with (' + str(
                    partner_name or '') + '), (' + str(addr)  + ') is on (' + str(
                    work_order_obj.scheduled_start[0:10]) + '). Thank You.'
            else:
                subject = 'Your work order(' + str(work_order_obj.name) + ') with (' + str(
                    partner_name or '') + '), is on (' + str(
                    work_order_obj.scheduled_start[0:10]) + '). Thank You.'

            vals['subject'] = subject
            vals['state'] ='Reminder'
            work_order_data.append(vals)

        return work_order_data

WorkOrderReminders()
