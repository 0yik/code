# encoding: utf-8
from openerp import api, exceptions, fields, models, _
import datetime
import pytz
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class RescheduleBooking(models.TransientModel):
    _inherit = 'reschedule.booking'

    @api.multi
    def action_reschedule(self):
        calendar_event_pool = self.env['calendar.event']
        bo_pool = self.env['sale.order']
        for obj in self:
            stock_obj = self.env['stock.picking'].browse(
                self._context.get('active_ids'))
            for wo_obj in stock_obj:
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

                # Search calendar event and deactive it
                calendar_obj = calendar_event_pool.search(
                    [('name', '=', wo_obj.origin)])
                #if not found then we search on the basis of name of WO
                if not calendar_obj:
                    calendar_obj = calendar_obj.search(
                        [('name', '=', wo_obj.name)]
                    )
                if calendar_obj:
                    calendar_obj.write({'active': False})
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
                # function for app
                partners = stock_obj.get_partners(wo_obj)
                address = stock_obj.get_work_order_address(wo_obj)
                if address:
                    subject = 'Your work order(' + str(wo_obj.name) + ') with (' + str(
                        wo_obj.partner_id.name.encode('utf-8') or '') + '), (' + str(address.encode('utf-8')) +') is rescheduled on (' + str(
                        wo_obj.scheduled_start) + ') at (' + str(wo_obj.scheduled_end) + '). Thank You.'
                else:
                    subject = 'Your work order(' + str(wo_obj.name) + ') with (' + str(
                        wo_obj.partner_id.name.encode('utf-8') or '') + ') is rescheduled on (' + str(
                        wo_obj.scheduled_start) + ') at (' + str(wo_obj.scheduled_end) + '). Thank You.'
                vals = {}
                vals['work_order_id'] = wo_obj.id
                vals['customer_id'] = wo_obj.partner_id.id if wo_obj.partner_id else False
                vals['booking_name'] = wo_obj.origin if wo_obj.origin else ''
                vals['work_location'] = address if address else ''
                vals['team_id'] = wo_obj.team.id if wo_obj.team else False
                vals['team_leader_id'] = wo_obj.team_leader.id if wo_obj.team_leader else False
                vals['team_employees_ids'] = [(6, 0, partners.ids)]
                vals['subject'] = subject
                vals['state'] = 'reschedule'
                vals['remarks'] = wo_obj.remarks if wo_obj.remarks else ''
                vals['reschedule_startdate'] = obj.start_date
                vals['reschedule_enddate'] = obj.end_date
                vals['created_date'] = fields.Datetime.now()
                obj.env['work.order.notification'].create(vals)

        return {'type': 'ir.actions.act_window_close'}


RescheduleBooking()
