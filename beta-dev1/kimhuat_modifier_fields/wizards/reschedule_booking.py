# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _
import datetime
import pytz
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class RescheduleBooking(models.TransientModel):
    _name = 'reschedule.booking'
    _description = 'Re-Schedule Booking'

    start_date = fields.Datetime(
        string='Scheduled Start Date & Time',
        help='Reschedule start date time',
        required=True, )
    end_date = fields.Datetime(
        string='Scheduled End Date & Time',
        help='Reschedule end date time.',
        required=True, )
    reschedule_reason = fields.Text(
        string='Reason for Reschedule',
        help='Reason for the reschedule.', required=True, )

    @api.onchange('start_date')
    def onchange_start_date(self):
        for record in self:
            if record.start_date:
                start_date = fields.Datetime.from_string(record.start_date)
                end_date = start_date + datetime.timedelta(hours=1)
                record.end_date = end_date
            else:
                record.end_date = False

    @api.multi
    def action_reschedule(self):
        calendar_event_pool = self.env['calendar.event']
        bo_pool = self.env['sale.order']
        for obj in self:
            for wo_obj in self.env['stock.picking'].browse(
                    self._context.get('active_ids')):
                if obj.start_date >= obj.end_date:
                    raise exceptions.UserError(
                        _('Start Date can\'t be equal or greater than end date.'))
                # first we check that existing selected team is available
                # if it is not available then we auto alocate team
                is_available = True
                is_available = wo_obj.action_check_auto_allocate(
                    wo_obj, wo_obj.team, obj.start_date, obj.end_date)
                # if is_available:
                # second checking the team is availabe on that day?
                # if not team available then we will update record by
                # auto allocate logic
                #     wo_obj.allocate_team(obj.start_date, obj.end_date, wo_obj, from_reschedule=True)
                reason = ''
                if not obj.env.user.tz:
                    raise exceptions.UserError(
                        _('Please add time zone in user. You can set Timezone under Preferences menu.'))
                user_tz = obj.env.user.tz or pytz.utc
                local = pytz.timezone(user_tz)
                reason += obj.reschedule_reason + '\n'
                reason += 'Previous Scheduled Start Date & Time: ' + datetime.datetime.strftime(
                    pytz.utc.localize(datetime.datetime.strptime(
                        wo_obj.scheduled_start,
                        DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),"%d/%m/%Y %H:%M:%S") + '\n'
                #reason += 'Old Scheduled Start Date & Time: ' + wo_obj.scheduled_start + '\n'
                #reason += 'Old Scheduled End Date & Time: ' + wo_obj.scheduled_end + '\n'
                reason += 'Previous Scheduled End Date & Time: ' + datetime.datetime.strftime(
                    pytz.utc.localize(datetime.datetime.strptime(
                        wo_obj.scheduled_end,
                        DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),"%d/%m/%Y %H:%M:%S") + '\n'
                wo_obj.is_reschedule = True
                wo_obj.reschedule_start_date = obj.start_date
                wo_obj.scheduled_start= obj.start_date
                wo_obj.reschedule_end_date = obj.end_date
                wo_obj.scheduled_end = obj.end_date
                #wo_obj.reschedule_reason = obj.reschedule_reason
                wo_obj.reschedule_reason = reason

                # Search calendar event and reschedule it
                calendar_obj = calendar_event_pool.search(
                    [('name', '=', wo_obj.origin)])
                #if not found then we search on the basis of name of WO
                if not calendar_obj:
                    calendar_obj = calendar_obj.search(
                        [('name', '=', wo_obj.name)]
                    )
                if calendar_obj:
                    #calendar_obj.write({'active': False})
                    calendar_obj.write({'start': obj.start_date,
                                        'stop': obj.end_date,
                                        })
                bo_obj = bo_pool.search(
                    [('name', '=', wo_obj.origin)])
                if bo_obj:
                    reason = ''
                    reason += obj.reschedule_reason + '\n'
                    reason += 'Previous Appointment Start Date & Time: ' + datetime.datetime.strftime(
                    pytz.utc.localize(datetime.datetime.strptime(
                        bo_obj.start_date,
                        DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(
                            local),"%d/%m/%Y %H:%M:%S") + '\n'
                    #bo_obj.start_date + '\n'
                    #reason += 'Old Appointment End Date & Time: ' + bo_obj.end_date + '\n'
                    reason += 'Previous Appointment End Date & Time: ' + datetime.datetime.strftime(
                    pytz.utc.localize(datetime.datetime.strptime(
                        bo_obj.end_date,
                        DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(
                            local),"%d/%m/%Y %H:%M:%S") + '\n'
                    #bo_obj.end_date + '\n'
                    bo_obj.write({
                        'is_reschedule': True,
                        #'reschedule_reason': obj.reschedule_reason,
                        'reschedule_reason': reason,
                        'reschedule_start_date': obj.start_date,
                        'start_date': obj.start_date,
                        'reschedule_end_date': obj.end_date,
                        'end_date': obj.end_date,
                    })
        return {'type': 'ir.actions.act_window_close'}


RescheduleBooking()
