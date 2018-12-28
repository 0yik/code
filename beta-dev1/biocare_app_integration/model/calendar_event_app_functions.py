from odoo import api, fields, models


class calendar_event(models.Model):
    _inherit = "calendar.event"

    @api.multi
    def get_calendar_data_app(self,partner_id):
        calendar_data = []
        calendar_events = self.env['calendar.event'].search([('partner_ids','in',partner_id)])
        for cal_obj in calendar_events:
            vals={}
            vals['meeting_subject'] = cal_obj.name
            attendees = []
            for attendees_obj in cal_obj.partner_ids:
                attendees.append(attendees_obj.name)
            vals['attendees'] = attendees

            serial_numbers = []
            for serial_obj in cal_obj.serial_numbers_ids:
                serial_numbers.append(serial_obj.name)
            vals['serial_numbers'] = serial_numbers

            vals['starting_at'] = cal_obj.start_datetime
            vals['duration'] = cal_obj.duration
            vals['location'] = cal_obj.location if cal_obj.location else ''
            vals['description'] = cal_obj.description
            vals['work_order_name'] = cal_obj.work_order_id.name if cal_obj.work_order_id else ''
            vals['work_order_id'] = cal_obj.work_order_id.id if cal_obj.work_order_id else False
            vals['booking_order_id'] = cal_obj.booking_order_id.id if cal_obj.booking_order_id else False
            vals['vehicle_no'] = cal_obj.booking_order_id.vehicle_new_id.name if cal_obj.booking_order_id.vehicle_new_id.name else False
            state = ''
            if cal_obj.work_order_id.state == 'pending':
                state = 'Pending'
            elif cal_obj.work_order_id.state == 'assigned':
                state = 'Started'
            elif cal_obj.work_order_id.state == 'done':
                state = 'Completed'
            elif cal_obj.work_order_id.state == 'cancel':
                state = 'Cancelled'
            vals['wo_status'] = state
            vals['wo_duration_app'] = cal_obj.work_order_id.duration_app if cal_obj.work_order_id.duration_app else ''
            vals['wo_start_date'] = cal_obj.work_order_id.scheduled_start if cal_obj.work_order_id.scheduled_start else ''
            vals['wo_end_date'] = cal_obj.work_order_id.scheduled_end if cal_obj.work_order_id.scheduled_end else ''
            service_types = []
            for move_obj in cal_obj.work_order_id.move_lines:
                service_types.append(move_obj.name)
            vals["types_of_service"] = service_types
            calendar_data.append(vals)
        return calendar_data