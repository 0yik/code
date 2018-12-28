from odoo import models, api, fields,_
from odoo.exceptions import ValidationError
import datetime

class sales_order(models.Model):
    _inherit = 'sale.order'

    pick_id = fields.Many2one('stock.picking', "Work Order", copy=False)

    @api.multi
    def action_confirm_record(self):
        for record in self:
            record.action_confirm()
            record.state_booking = 'sale'
            pickings = record.mapped('picking_ids')
            if pickings:
                record.pick_id = pickings[0].id
                for picking in pickings:
                    picking.state = 'pending'
                    picking.scheduled_start = record.start_date
                    picking.scheduled_end = record.end_date
                    picking.service_rendered = record.job_detail
                    picking.remarks = record.remarks or ''
                    # picking.actual_start = record.start_date
                    # picking.actual_end = record.end_date
                    picking.team = record.team
                    picking.team_leader = record.team_leader
                    for employee_line in record.team_employees:
                        data = {
                            'employee_id': employee_line.employee_id.id,
                            'order_id': picking.id
                        }
                        picking.team_employees.create(data)
                    # picking.team_employees  = record.team_employees

                    # bug fixed for product_id product.id
                    # for product_line in record.equipment_ids:
                    #     data = {
                    #         'product_id': product_line.product_id.id,
                    #         'lot_id': product_line.lot_id.id,
                    #         'order_id': picking.id
                    #     }
                    #     picking.product_ids.create(data)

    @api.multi
    def action_create_calendar(self):
        for record in self:
            # Prepare serial numbers
            serial_numbers = record.equipment_ids.mapped(lambda r: r.lot_id)
            address = record.pick_id.get_work_order_address(record.pick_id) if record.pick_id else ''
            # Prepare partners
            partners = self.get_partners(record)
            data = {
                'name': record.name,
                'allday': False,
                'start_datetime': record.start_date,
                'stop_datetime': record.end_date,
                'duration': 1,
                'location': address if address else '',
                'start': record.start_date,
                'stop': record.end_date,
                'partner_ids': [(6, 0, partners.ids)],
                'serial_numbers_ids': [(6, 0, serial_numbers.ids)],
                'work_order_id': record.pick_id.id,
                'booking_order_id': record.id,
            }
            calendar_obj = self.env['calendar.event'].sudo().create(data)
            record.calendar_id = calendar_obj.id
            if record.pick_id:
                work_order_id = record.pick_id
                vals = {}
                address = work_order_id.get_work_order_address(work_order_id)
                try:
                    partner_name = work_order_id.partner_id.name.encode('utf-8')
                except:
                    partner_name = work_order_id.partner_id.name
                if address:
                    try:
                        addr = address.encode('utf-8')
                    except:
                        addr = address

                    subject = 'Your work order(' + str(work_order_id.name) + ') with (' + str(
                        partner_name or '') + '), (' + str(
                        addr) + ') has been scheduled on (' + str(
                        work_order_id.scheduled_start[0:10]) + '). Thank You.'
                else:
                    subject = 'Your work order(' + str(work_order_id.name) + ') with (' + str(
                        partner_name or '') + ') has been scheduled on (' + str(
                        work_order_id.scheduled_start[0:10]) + '). Thank You.'
                vals['customer_id'] = work_order_id.partner_id.id if work_order_id.partner_id else False
                vals['work_order_id'] = work_order_id.id
                vals['booking_name'] = work_order_id.origin if work_order_id.origin else ''
                vals['work_location'] = address if address else ''
                vals['team_id'] = work_order_id.team.id if work_order_id.team else False
                vals['team_employees_ids'] = [(6, 0, calendar_obj.partner_ids.ids)]
                vals['subject'] = subject
                vals['remarks'] = work_order_id.remarks if work_order_id.remarks else ''
                vals['state'] = 'Pending'
                vals['created_date'] = fields.Datetime.now()
                self.env['work.order.notification'].create(vals)

    @api.multi
    def action_todo(self):
        if not self.order_line:
            raise ValidationError(_('Please select the order lines for this booking order.'))
        else:
            try:
                self.action_check()
            except ValidationError as e:
                if e.name == 'Everyone is available for the booking':
                    self.action_confirm_record()
                    self.action_create_calendar()
                    # create work order notification

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

sales_order()