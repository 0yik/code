# -*- coding: utf-8 -*-
from openerp import api, exceptions, fields, models, _
import datetime


class WorkOrderReminders(models.Model):
    _name = 'work.order.reminder.app'
    _description = 'Send Reminders to App'

    @api.multi
    def send_update_to_app(self,user_id,worker_type):
        employee_id = self.env['hr.employee'].search([('user_id', '=', user_id)], limit=1).ids
        if not employee_id:
            employee_id = self.env['hr.employee'].search([('resource_id.user_id', '=', user_id)], limit=1).ids

        date_today = fields.Datetime.from_string(fields.Datetime.now())
        from_date = (date_today + datetime.timedelta(days=1)).replace(
            hour=00, minute=00, second=01)
        to_date = (date_today + datetime.timedelta(days=1)).replace(
            hour=23, minute=59, second=59)

        work_order_ids = []
        if (worker_type == "team_lead"):
            work_order_ids = self.env['stock.picking'].search(
                [('team_leader', 'in', employee_id),('scheduled_start', '>=', fields.Datetime.to_string(from_date)),('scheduled_start', '<=', fields.Datetime.to_string(to_date))],order='id desc')
        else:
            work_order_employee_ids = self.env['working.order.employee'].search([('employee_id', 'in', employee_id)])
            for temp_obj in work_order_employee_ids:
                if  temp_obj.order_id.scheduled_start >= fields.Datetime.to_string(from_date) and temp_obj.order_id.scheduled_start <= fields.Datetime.to_string(to_date):
                    work_order_ids.append(temp_obj.order_id)

        work_order_data = []
        for work_order_obj in  work_order_ids:
            vals = {}
            vals['work_order_id'] = work_order_obj.id
            vals['work_order_name'] = work_order_obj.name
            vals['booking_no'] = work_order_obj.origin if work_order_obj.origin else ""
            vals['scheduled_start'] = work_order_obj.scheduled_start if work_order_obj.scheduled_start else ""
            vals['scheduled_end'] = work_order_obj.scheduled_end if work_order_obj.scheduled_end else ""
            vals['actual_start'] = work_order_obj.actual_start if work_order_obj.actual_start else ""
            vals['actual_end'] = work_order_obj.actual_end if work_order_obj.actual_end else ""
            vals['duration'] = work_order_obj.duration_app

            # Types of service
            service_types = []
            for move_obj in work_order_obj.move_lines:
                service_types.append(move_obj.product_id.name)
            vals["types_of_service"] = service_types

            vals['work_location'] = work_order_obj.work_location if work_order_obj.work_location else ""
            vals['customer_name'] = work_order_obj.partner_id.name
            vals['mobile_no'] = work_order_obj.partner_id.mobile if work_order_obj.partner_id.mobile else ""
            vals['status'] = work_order_obj.state
            vals['vehicle_no'] = work_order_obj.vehicle_new_id.name if work_order_obj.vehicle_new_id else ""
            equipment_list = {}
            for book_line_obj in work_order_obj.equip_ids:
                tmp_vals = {}
                tmp_vals["id"] = book_line_obj.id
                tmp_vals[
                    "image"] = book_line_obj.equipment_id.image_medium if book_line_obj.equipment_id.image_medium else ""
                tmp_vals["checked"] = book_line_obj.checked
                equipment_list[book_line_obj.equipment_id.name] = tmp_vals
            vals['list_of_equipments'] = equipment_list

            vals['team_name'] = work_order_obj.team.name if work_order_obj.team else ""
            vals['team_leader'] = work_order_obj.team_leader.name if work_order_obj.team_leader else ""

            team_workers = []
            for team_worker_obj in work_order_obj.team_employees:
                team_workers.append(team_worker_obj.employee_id.name)
            partner_name = ''
            try:
                partner_name = work_order_obj.partner_id.name.encode('utf-8')
            except:
                partner_name = work_order_obj.partner_id.name
            if work_order_obj.work_location:
                work_location = ''
                try:
                    work_location = work_order_obj.work_location.encode('utf-8')
                except:
                    work_location = work_order_obj.work_location
                subject = 'Reminder : Your work order' + str(work_order_obj.name) + ' with ' + str(
                    partner_name or '') + ', ' + str(work_location)  + ' is scheduled on (' + str(
                    work_order_obj.scheduled_start) + '). Thank You.'
            else:
                subject = 'Reminder : Your work order ' + str(work_order_obj.name) + ' with ' + str(
                    partner_name or '') + ', is scheduled on (' + str(
                    work_order_obj.scheduled_start) + '). Thank You.'
            vals['workers'] = team_workers
            vals['remarks'] = work_order_obj.remarks if work_order_obj.remarks else ""
            vals['subject'] = subject
            vals['state'] ='Reminder'
            work_order_data.append(vals)

        return work_order_data

WorkOrderReminders()
