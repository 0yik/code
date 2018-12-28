from odoo import models, api, fields,_
from odoo.exceptions import ValidationError
import datetime

class sales_order(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_create_calendar(self):
        res = super(sales_order,self).action_create_calendar()
        for record in self:
            if record.pick_id:
                work_order_id = record.pick_id
                vals = {}
                partner_name = ''
                try:
                    partner_name = work_order_id.partner_id.name.encode('utf-8')
                except:
                    partner_name = work_order_id.partner_id.name
                if work_order_id.work_location:
                    work_location = ''
                    try:
                        work_location = work_order_id.work_location.encode('utf-8')
                    except:
                        work_location = work_order_id.work_location
                    subject = 'Your work order ' + str(work_order_id.name) + ' with ' + str( partner_name  )+ ', ' \
                              + str(work_location) + ' has been scheduled on (' + \
                              str(work_order_id.scheduled_start) + '). Thank You.'
                else:
                    subject = 'Your work order ' + str(work_order_id.name) + ' with ' + str(
                        partner_name or '') + ' has been scheduled on (' + str(
                        work_order_id.scheduled_start) + '). Thank You.'
                vals['customer_id'] = work_order_id.partner_id.id if work_order_id.partner_id else False
                vals['work_order_id'] = work_order_id.id
                vals['booking_name'] = work_order_id.origin if work_order_id.origin else ''
                vals['work_location'] = record.work_location if record.work_location else ''
                vals['team_id'] = work_order_id.team.id if work_order_id.team else False
                vals['team_employees_ids'] = [(6, 0, record.calendar_id.partner_ids.ids)]
                vals['subject'] = subject
                vals['remarks'] = work_order_id.remarks if work_order_id.remarks else ''
                vals['state'] = 'Pending'
                vals['created_date'] = fields.Datetime.now()
                self.env['work.order.notification'].create(vals)
        return res

sales_order()