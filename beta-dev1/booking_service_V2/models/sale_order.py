# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from odoo.exceptions import ValidationError
import datetime


class sale_order_inherit(models.Model):
    _inherit = 'sale.order'

    is_booking = fields.Boolean('Is a booking')
    is_booking_sub = fields.Boolean()
    team = fields.Many2one('booking.team')
    team_leader = fields.Many2one('hr.employee', string='Team leader', store=True)
    team_employees = fields.One2many('booking.order.employee', 'order_id', string='Employees', store=True)
    equipment_ids = fields.One2many('booking.order.product', 'order_id', string='Equipments', store=True)
    start_date = fields.Datetime('Start Date')
    end_date = fields.Datetime('End Date')
    name_number = fields.Integer()

    state_booking = fields.Selection([
                                    ('draft', 'Draft'),
                                    ('sent', 'Quotation Sent'),
                                    ('sale', 'Booking Order'),
                                    ('done', 'Locked'),
                                    ('cancel', 'Cancelled'),
    ])


    @api.model
    def create(self, vals):
        res = super(sale_order_inherit, self).create(vals)
        if res.is_booking == True:
            res.update({
                'is_booking_sub': res.is_booking,
            })
            sales_order_obj = self.env['sale.order'].search([('id', '!=', res.id), ('is_booking', '=', True)],
                                                            order='id desc', limit=1)
            if not sales_order_obj:
                name_number_current = 1
            else:
                name_number_current = sales_order_obj.name_number + 1
            current_year = datetime.datetime.now().strftime('%Y')
            name_booking = "BO/%s/%s" % (current_year, '{0:05}'.format(name_number_current))
            res.write({
                'name': name_booking,
                'name_number': name_number_current
            })
        return res

    @api.model
    def default_get(self, fields):
        res = super(sale_order_inherit, self).default_get(fields)
        if 'is_booking' in res:
            res.update({
                'is_booking_sub' : res['is_booking'] ,
                'state_booking'  : 'draft' ,
                })
        return res



    @api.multi
    def write(self,vals):
        if 'is_booking' in vals and vals['is_booking'] == True:
            vals['is_booking_sub'] = True
        res = super(sale_order_inherit, self).write(vals)
        return res

    @api.model
    def get_partners(self, record):
        # Prepare partner lists
        partners = self.env['res.partner'].browse([])

        for employee in record.team_employees:
            if employee.employee_id.user_id and employee.employee_id.user_id.partner_id:
                partner = employee.employee_id.user_id.partner_id
            else:
                partner = self.env['res.partner'].create({'name': employee.employee_id.name})
                user = self.env['res.users'].create({
                    'login': employee.employee_id.name,
                    'partner_id': partner and partner.id,
                })
                employee.employee_id.user_id = user
            partners += partner

        if record.team_leader:
            if record.team_leader.user_id and record.team_leader.user_id.partner_id:
                partner = record.team_leader.user_id.partner_id
            else:
                partner = self.env['res.partner'].create({'name': record.team_leader.name})
                user = self.env['res.users'].create({
                    'login': record.team_leader.name,
                    'partner_id': partner and partner.id,
                })
                record.team_leader.user_id = user
            partners += partner

        return partners

    @api.multi
    def action_check(self):
        for record in self:
            start_date = fields.Datetime.from_string(record.start_date)
            end_date = fields.Datetime.from_string(record.end_date)

            book_setting = self.env.ref('booking_service_V2.setting_data')
            pre_book_time = int(book_setting.pre_booking_time)
            post_book_time = int(book_setting.post_booking_time)

            booking_start = (start_date - datetime.timedelta(minutes=post_book_time)).strftime('%Y-%m-%d %H:%M:%S')
            booking_end = (end_date + datetime.timedelta(minutes=pre_book_time)).strftime('%Y-%m-%d %H:%M:%S')

            # Prepare serial numbers
            serial_numbers = record.equipment_ids.mapped(lambda r: r.lot_id)

            # Prepare partners
            partners = self.get_partners(record)

            # Search conflict partners
            partner_names = []
            events = self.env['calendar.event'].search([
                ('partner_ids', 'in', partners.ids),
                ('start', '<=', booking_end), ('stop', '>=', booking_start),
            ])
            for event in events:
                for partner in event.partner_ids:
                    if partner.id in partners.ids:
                        if partner.name not in partner_names:
                            partner_names.append(partner.name)

            # Search conflict equipments
            equipment_names = []
            events = self.env['calendar.event'].search([
                ('serial_numbers_ids', 'in', serial_numbers.ids),
                ('start', '<=', booking_end), ('stop', '>=', booking_start),
            ])
            for event in events:
                for equipment in event.serial_numbers_ids:
                    if equipment.id in serial_numbers.ids:
                        if equipment.name not in equipment_names:
                            equipment_names.append(equipment.name)

            # Show validation message
            if len(partner_names) > 0 or len(equipment_names) > 0:
                validation_message = ''
                if len(partner_names) > 0:
                    validation_message += 'Employee: %s ' %(', '.join(partner_names), )
                    if len(equipment_names) > 0:
                        validation_message += 'and/or '

                if len(equipment_names) > 0:
                    validation_message += 'Serial Number: %s ' %(', '.join(equipment_names),)
                raise ValidationError(validation_message + ' has an event on that day and time')
            else:
                raise ValidationError('Everyone is available for the booking')

    @api.multi
    def action_todo(self):
        try:
            self.action_check()
        except ValidationError as e:
            if e.name == 'Everyone is available for the booking':
                self.action_create_calendar()
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

    @api.multi
    def action_create_calendar(self):
        for record in self:
            # Prepare serial numbers
            serial_numbers = record.equipment_ids.mapped(lambda r: r.lot_id)

            # Prepare partners
            partners = self.get_partners(record)

            data = {
                'name': record.name,
                'allday': False,
                'start_datetime': record.start_date,
                'stop_datetime': record.end_date,
                'duration': 1,
                'start': record.start_date,
                'stop': record.end_date,
                'partner_ids': [(6, 0, partners.ids)],
                'serial_numbers_ids': [(6, 0, serial_numbers.ids)],
            }
            self.env['calendar.event'].sudo().create(data)

    @api.multi
    def action_cancel(self):
        super(sale_order_inherit, self).action_cancel()
        self.write({'state_booking': 'cancel'})

    @api.multi
    def action_done(self):
        super(sale_order_inherit, self).action_done()
        self.write({'state_booking': 'done'})

    @api.multi
    def action_confirm_record(self):
        for record in self:
            record.action_confirm()
            record.state_booking = 'sale'
            pickings = record.mapped('picking_ids')
            if pickings:
                for picking in pickings:
                    picking.state = 'pending'
                    picking.scheduled_start = record.start_date
                    picking.scheduled_end = record.end_date
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
                    for product_line in record.equipment_ids:
                        data = {
                            'product_id': product_line.product_id.id,
                            'lot_id': product_line.lot_id.id,
                            'order_id': picking.id
                        }
                        picking.product_ids.create(data)

    @api.onchange('team')
    def _onchange_team(self):
        # for record in self:
        teams = self.env['booking.team'].search([('id', '=', self.team.id)])
        self.team_leader = teams.team_leader

        team_employees = self.team_employees.browse([])
        for employee in teams.team_employees:
            team_employees += self.team_employees.new({
                'employee_id': employee.employee_id,
            })
        self.team_employees = team_employees

        equipment_ids = self.equipment_ids.browse([])
        for product in teams.product_ids:
            equipment_ids += self.equipment_ids.new({
                'product_id': product.product_id and product.product_id.id,
                'lot_id': product.lot_id and product.lot_id.id,
            })
        self.equipment_ids = equipment_ids

    @api.onchange('start_date')
    def onchange_start_date(self):
        for record in self:
            if record.start_date:
                start_date = fields.Datetime.from_string(record.start_date)
                end_date = start_date + datetime.timedelta(hours=1)
                record.end_date = end_date
            else:
                record.end_date = False


class booking_order_product(models.Model):
    _name = 'booking.order.product'

    product_id = fields.Many2one('product.template', string="Equipments", domain=[('is_equipment', '=', True)],
                                 required=True)
    lot_id = fields.Many2one('stock.production.lot', string="Serial Number")
    order_id = fields.Many2one('sale.order')

    @api.onchange('product_id')
    def onchange_product_id(self):
        return {
            'domain': {
                'lot_id': [('product_id', '=', self.product_id.id)]
            }
        }

    @api.model
    def create(self, values):
        lot = values['lot_id']
        if lot is False:
            raise ValidationError("Serial Number can't be blank")
        record = super(booking_order_product, self).create(values)
        return record

    @api.model
    def write(self, values):
        lot = values['lot_id']
        if lot is False:
            raise ValidationError("Serial Number can't be blank")
        record = super(booking_order_product, self).write(values)
        return record

class booking_order_employee(models.Model):
    _name = 'booking.order.employee'

    employee_id = fields.Many2one('hr.employee', string="Employee")
    order_id = fields.Many2one('sale.order', string="Order")
