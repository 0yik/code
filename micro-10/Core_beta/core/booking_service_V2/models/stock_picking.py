# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import datetime
from odoo.exceptions import ValidationError, Warning


class stock_picking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    @api.depends('actual_start', 'actual_end')
    def _get_total_hours(self):
        """docstring for _get_total_hours"""
        for obj in self:
            if obj.actual_end and obj.actual_start:
                duration = abs(datetime.datetime.strptime(obj.actual_end, "%Y-%m-%d %H:%M:%S") - datetime.datetime.strptime(obj.actual_start, "%Y-%m-%d %H:%M:%S"))
                obj.total_time = abs((duration.total_seconds() / 60) / 60)
            else:
                obj.total_time = False

    @api.model
    def _get_list_equipments(self):
        equip_ids = []
        list_ids = self.env['list.equipment'].search([], limit=1)
        if list_ids:
            equip_ids = []
            for equip in list_ids.equipment_ids:
                equip_ids.append((0, 0, {
                    'equipment_id': equip.equipment_id.id
                }))
        return equip_ids

    is_booking = fields.Boolean('Is a booking')
    scheduled_start = fields.Datetime('Scheduled Start Date & Time', required=False)
    scheduled_end = fields.Datetime('Scheduled End Date & Time', required=False)
    actual_start = fields.Datetime('Actual Start Date & Time', required=False, readonly=True)
    actual_end = fields.Datetime('Actual End Date & Time', required=False, readonly=True)
    total_time = fields.Float(
        string='Duration',
        help='Total Duration from actual start and actual end.',
        compute='_get_total_hours',
    )
    team = fields.Many2one('booking.team', ondelete='restrict')
    team_leader = fields.Many2one('hr.employee', string='Team leader', ondelete='restrict')
    team_employees = fields.One2many(
        'working.order.employee', 'order_id',
        string='Employees', store=True)
    product_ids = fields.One2many('working.order.product', 'order_id', string='Equipments', store=True)
    vehicle_new_id = fields.Many2one(comodel_name='product.product', string='Vehicle', help='Add Vehicle')
    is_validated = fields.Boolean('Validated', default=False)
    work_location = fields.Char(string='Work Location', size=64, help='Address from booking order.')
    postal_code = fields.Char(string='Postal Code', size=64, help='')
    mobile_no = fields.Char(string="Contact Number")
    location_dest_id = fields.Many2one(
        'stock.location', "Destination Location Zone",
        default=lambda self: self.env['stock.picking.type'].browse(self._context.get('default_picking_type_id')).default_location_dest_id,
        readonly=True, required=False,
        states={'draft': [('readonly', False)]})
    equip_ids = fields.One2many(
        comodel_name='list.equipment.line',
        inverse_name='workorder_id', string='Equipments', help='',
        default=_get_list_equipments, copy=True)

    state = fields.Selection([
        ('draft', 'Draft'), ('cancel', 'Cancelled'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting Availability'),
        ('partially_available', 'Partially Available'),
        ('pending', 'Pending'),
        ('assigned', 'Started'), ('done', 'Done')], string='Status', compute='_compute_state',
        copy=False, index=True, readonly=True, store=True, track_visibility='onchange',
        help=" * Draft: not confirmed yet and will not be scheduled until confirmed\n"
             " * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n"
             " * Waiting Availability: still waiting for the availability of products\n"
             " * Partially Available: some products are available and reserved\n"
             " * Ready to Transfer: products reserved, simply waiting for confirmation.\n"
             " * Transferred: has been processed, can't be modified or cancelled anymore\n"
             " * Cancelled: has been cancelled, can't be confirmed anymore")

    @api.onchange('partner_id')
    def _customer_address(self):
        street = ''
        street2 = ''
        city = ''
        state = ''
        country = ''
        zip = ''
        if self.partner_id.street:
            street = self.partner_id.street + ','
        if self.partner_id.street2:
            street2 = self.partner_id.street2 + ','
        if self.partner_id.city:
            city = self.partner_id.city + ','
        if self.partner_id.state_id.name:
            state = self.partner_id.state_id.name + ','
        if self.partner_id.country_id.name:
            country = self.partner_id.country_id.name + ','
        if self.partner_id.zip:
            zip = self.partner_id.zip
        address = street + street2 + city + state + country + zip

        self.update({#'work_location': address,
                     'postal_code': self.partner_id.zip or False,
                     'mobile_no': self.partner_id.mobile or False,
                     })


    @api.model
    def create(self, values):
        booking_order = self.env['sale.order'].search([
            ('is_booking', '=', True),
            ('name', '=', values.get('origin')),
        ], limit=1)
        if booking_order and booking_order.id:
            values.update({
                'is_booking': True,
            })
        record = super(stock_picking, self).create(values)
        return record

    @api.onchange('is_booking')
    def onchange_is_booking(self):
        for record in self:
            if record.is_booking:
                booking_orders = self.env['sale.order'].search([
                    ('is_booking', '=', True),
                    ('name', '=', record.origin),
                ])
                for booking_order in booking_orders:
                    record.scheduled_start = booking_order.start_date
                    record.scheduled_end = booking_order.end_date
                    record.actual_start = booking_order.start_date
                    record.actual_end = booking_order.end_date
                    record.team = booking_order.team
                    record.team_leader = booking_order.team_leader
                    record.team_employees = booking_order.team_employees
                    record.product_ids = booking_order.equipment_ids
                    record.vehicle_new_id = booking_order.vehicle_new_id and booking_order.vehicle_new_id.id or False
                    record._customer_address()
                    record.work_location = booking_order.work_location_address
                    record.mobile_no = booking_order.pick_id
                    record.postal_code = booking_order.postal_code

    @api.multi
    def action_start(self):
        for record in self:
            record.actual_start = fields.Datetime.now()
            #record.actual_end = fields.Datetime.now()
            record.state = 'assigned'
            record.move_lines.write({'state': 'assigned'})

    @api.multi
    def action_validate(self):
        for record in self:
            if record.state == 'assigned':
                record.actual_end = fields.Datetime.now()
                record.state = 'done'
                record.move_lines.write({'state': 'done'})

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
                    'name': employee.employee_id.name
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
                    'name': record.team_leader.name,
                })
                record.team_leader.user_id = user
            partners += partner

        return partners

    @api.multi
    def action_check(self):
        for record in self:
            if not record.team:
                raise Warning(_('Please add team in Team.'))
            scheduled_start = fields.Datetime.from_string(record.scheduled_start)
            scheduled_end = fields.Datetime.from_string(record.scheduled_end)

            '''
            try:
                book_setting = self.env.ref('booking_service_V2.setting_data')
            except Exception as e:
                raise ValidationError(_('Please define Pre and Post Booking Time in Settings.'))
            '''
            book_setting = self.env['booking.settings'].search([], order='id desc', limit=1)
            if not book_setting:
                raise ValidationError(_("Please define booking settings."))

            if not book_setting.pre_booking_time:
                raise ValidationError(_('Please define Pre Booking Time in Settings.'))

            if not book_setting.post_booking_time:
                raise ValidationError(_('Please define Post Booking Time in Settings.'))

            pre_book_time = int(book_setting.pre_booking_time)
            post_book_time = int(book_setting.post_booking_time)

            booking_start = (scheduled_start - datetime.timedelta(minutes=post_book_time)).strftime('%Y-%m-%d %H:%M:%S')
            booking_end = (scheduled_end + datetime.timedelta(minutes=pre_book_time)).strftime('%Y-%m-%d %H:%M:%S')

            # Prepare serial numbers
            #serial_numbers = record.product_ids.mapped(lambda r: r.lot_id)
            serial_numbers = self.env['stock.production.lot'].search([('product_id', '=', self.vehicle_new_id.id)], limit=1)
            # Prepare partner lists
            partners = self.get_partners(record)

            # Search conflict partners
            partner_names = []
            events = self.env['calendar.event'].search([
                ('name', '!=', record.origin),
                ('partner_ids', 'in', partners.ids),
                ('start', '<=', booking_end), ('stop', '>=', booking_start),
                ('active', '=', True),
            ])

            for event in events:
                for partner in event.partner_ids:
                    if partner.id in partners.ids:
                        if partner.name not in partner_names:
                            partner_names.append(partner.name)

            # Search conflict equipments
            equipment_names = []
            events = self.env['calendar.event'].search([
                ('name', '!=', record.origin),
                ('serial_numbers_ids', 'in', serial_numbers.ids),
                ('start', '<=', booking_end), ('stop', '>=', booking_start),
                ('active', '=', True),
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
                    validation_message += 'Serial Number: %s ' %(', '.join(equipment_names),)
                raise ValidationError(validation_message + ' has an event on that day and time')
            else:
                raise ValidationError("Everyone is available for the booking")

    @api.multi
    def action_todo(self):
        try:
            self.action_check()
        except ValidationError as e:
            if e.name == 'Everyone is available for the booking':
                self.action_create_calendar()
                self.action_confirm()
                if self.is_booking:
                    self.is_validated = True
                self.state = 'pending'
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
            # Prepare partners
            partners = self.get_partners(record)
        data = {
            'name': record.name,
            'allday': False,
            'start_datetime': record.scheduled_start,
            'stop_datetime': record.scheduled_end,
            'start': record.scheduled_start,
            'stop': record.scheduled_end,
            'partner_ids': [(6, 0, partners.ids)],
        }
        self.env['calendar.event'].sudo().create(data)

    @api.onchange('team')
    def _onchange_team(self):
        # for record in self:
        teams = self.env['booking.team'].search([('id', '=', self.team.id)])
        self.team_leader = teams.team_leader
        self.vehicle_new_id = teams.vehicle_new_id and teams.vehicle_new_id.id or False

        team_employees = self.team_employees.browse([])
        for employee in teams.team_employees:
            team_employees += self.team_employees.new({
                'employee_id': employee.id,
            })
        self.team_employees = team_employees

        equipment_ids = self.product_ids.browse([])
        for product in teams.product_ids:
            equipment_ids += self.product_ids.new({
                'product_id': product.product_id and product.product_id.id,
                'lot_id': product.lot_id and product.lot_id.id,
            })
        self.product_ids = equipment_ids

class working_order_product(models.Model):
    _name = 'working.order.product'

    product_id = fields.Many2one('product.template', string="Equipments", domain=[('is_equipment', '=', True)], required=False)
    lot_id = fields.Many2one('stock.production.lot', string="Serial Number")
    order_id = fields.Many2one('stock.picking')

    @api.onchange('product_id')
    def onchange_product_id(self):
        return {
            'domain': {
                'lot_id': [('product_id', '=', self.product_id.id)]
            }
        }

  # @api.model
  # def create(self, values):
  #     lot = values['lot_id']
  #     if lot is False:
  #         raise ValidationError("Serial Number can't be blank")
  #     record = super(working_order_product, self).create(values)
  #     return record

  # @api.model
  # def write(self, values):
  #     lot = values['lot_id']
  #     if lot is False:
  #         raise ValidationError("Serial Number can't be blank")
  #     record = super(working_order_product, self).write(values)
  #     return record

class working_order_employee(models.Model):
    _name = 'working.order.employee'

    employee_id = fields.Many2one('hr.employee', string="Employee")
    order_id = fields.Many2one('stock.picking', string="Order")
