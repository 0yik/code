# encoding: utf-8
from openerp import api, exceptions, fields, models, _
import datetime
import pytz
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class RescheduleBooking(models.TransientModel):
    _inherit = 'reschedule.booking'

    @api.multi
    def action_reschedule(self):
        res = super(RescheduleBooking, self).action_reschedule()
        for obj in self:
            record = self.env['stock.picking'].browse(self._context.get('active_ids'))
            stock_obj = self.env['stock.picking'].search([('id','=',record.id)],order='id desc')
            for wo_obj in stock_obj:
                # function for app
                partners = stock_obj.get_partners(wo_obj)
                loc = wo_obj.work_location

                partner_name = ''
                try:
                    partner_name = wo_obj.partner_id.name.encode('utf-8')
                except:
                    partner_name = wo_obj.partner_id.name
                if wo_obj.work_location:
                    work_location = ''
                    try:
                        work_location = wo_obj.work_location.encode('utf-8')
                    except:
                        work_location = wo_obj.work_location

                    subject = 'Your work order ' + str(wo_obj.name) + ' with ' + str(
                        partner_name or '')  + str(work_location) + ' is rescheduled on (' + str(
                        wo_obj.scheduled_start) + '). Thank You.'
                else:
                    subject = 'Your work order ' + str(wo_obj.name) + ' with ' + str(
                        partner_name or '') + ' is rescheduled on (' + str(
                        wo_obj.scheduled_start) + '). Thank You.'
                vals = {}
                vals['work_order_id'] = wo_obj.id
                vals['customer_id'] = wo_obj.partner_id.id if wo_obj.partner_id else False
                vals['booking_name'] = wo_obj.origin if wo_obj.origin else ''
                vals['work_location'] = wo_obj.work_location if wo_obj.work_location else ''
                vals['team_id'] = wo_obj.team.id if wo_obj.team else False
                vals['team_leader_id'] = wo_obj.team_leader.id if wo_obj.team_leader else False
                vals['team_employees_ids'] = [(6, 0, partners.ids)]
                vals['subject'] = subject
                vals['state'] = 'Reschedule'
                vals['remarks'] = wo_obj.remarks if wo_obj.remarks else ''
                vals['reschedule_startdate'] = obj.start_date
                vals['reschedule_enddate'] = obj.end_date
                vals['created_date'] = fields.Datetime.now()
                obj.env['work.order.notification'].sudo().create(vals)

        return res


RescheduleBooking()
