from odoo import api, fields, models, exceptions, _
import datetime
from lxml import etree
from odoo.exceptions import ValidationError


class biocare_modifier_field_booking(models.Model):
    _inherit = 'sale.order'
    _order = 'date_order desc, start_date desc, id desc'

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

    @api.multi
    @api.depends('team_employees')
    def _get_worker_name(self):
        for self_obj in self:
            self_obj.worker_name = ','.join([worker.employee_id.name for worker in self_obj.team_employees]) or ''


    work_location = fields.Many2one(
        'stock.location', string="Work Location",
        related='partner_id.property_stock_customer')
    work_location_address = fields.Char(string="Work Location")
    postal_code = fields.Char("Postal Code")
    pic_id = fields.Char(string="PIC", related='partner_id.mobile')
    work_order = fields.Char('Work Order')
    job_history = fields.Char('Job History')
    equip_ids = fields.One2many(
        comodel_name='list.equipment.line',
        inverse_name='order_id', string='Equipments', help='',
        default=_get_list_equipments, copy=True)

    # To idetify reschedle of BO
    is_reschedule = fields.Boolean(
        string='Is Reschedule?', help='Technical field to identify reschedule',
        copy=False)
    reschedule_start_date = fields.Datetime(
        string='Rescheduled Start Date & Time', help='Reschedule Start Time',
        copy=False)
    reschedule_end_date = fields.Datetime(
        string='Rescheduled End Date & Time', help='Reschedule End Time',
        copy=False)
    reschedule_reason = fields.Text(
        string='Reason for Reschedule', help='Reason for the reschedule.',
        copy=False)
    calendar_id = fields.Many2one(
        'calendar.event', string='Calendar')
    wo_count = fields.Integer(
        string='Delivery Orders', compute='_compute_wo_ids')
    worker_name = fields.Char("Worker", compute='_get_worker_name', store=True, )


    @api.multi
    @api.depends('procurement_group_id')
    def _compute_wo_ids(self):
        for order in self:
            order.picking_ids = self.env['stock.picking'].search(
                [('group_id', '=', order.procurement_group_id.id)]) if order.procurement_group_id else []
            order.wo_count = len(order.picking_ids)

    @api.constrains('order_line')
    def _check_reserved_service(self):
        """check for the reserved team in serice
           if reserved service then we only allow
           one service in line.
           if not reserved sservice then we will add
           multiple services in line
        """
        for self_obj in self:
            if len(self_obj.order_line) > 1:
                if any([line.product_id.reserved_team for line in self_obj.order_line if line.product_id.reserved_team ]):
                    raise ValidationError(_(
                        "Multiple services cannot be added in a booking order \
                        if the service has a reserved team to work."
                    ))

    @api.model
    def _prepare_add_missing_fields_bo(self, values):
        res = {}
        onchange_fields = ['work_location_address', 'postal_code',]
        if values.get('partner_id') and any(f not in values for f in onchange_fields):
            line = self.new(values)
            line._customer_address()
            for field in onchange_fields:
                if field not in values:
                    res[field] = line._fields[field].convert_to_write(line[field], line)
        return res

    @api.model
    def create(self, values):
        values.update(self._prepare_add_missing_fields_bo(values))
        return super(biocare_modifier_field_booking, self).create(values)

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

        self.update({'work_location_address': address,
                     'postal_code': self.partner_id.zip or False,
                     })

    @api.model
    def get_partners_auto_allocate(self, record, team_id):
        # Prepare partner lists
        # # Copy method of get_partners
        # TODO Please update this method with get_partners
        partners = self.env['res.partner'].browse([])

        # for employee in record.team_employees:
        for employee in team_id.team_employees:
            if employee.employee_id.user_id and employee.employee_id.user_id.partner_id:
                partner = employee.employee_id.user_id.partner_id
            else:
                partner = self.env['res.partner'].create(
                    {'name': employee.employee_id.name})
                user = self.env['res.users'].create({
                    'login': employee.employee_id.name,
                    'partner_id': partner and partner.id,
                    'name': employee.employee_id.name,
                })
                employee.employee_id.user_id = user
            partners += partner

        if team_id.team_leader:
            if team_id.team_leader.user_id and team_id.team_leader.user_id.partner_id:
                partner = team_id.team_leader.user_id.partner_id
            else:
                partner = self.env['res.partner'].create(
                    {'name': team_id.team_leader.name})
                user = self.env['res.users'].create({
                    'login': team_id.team_leader.name,
                    'partner_id': partner and partner.id,
                    'name': team_id.team_leader.name,
                })
                team_id.team_leader.user_id = user
            partners += partner

        return partners

    def action_check_auto_allocate(self, record, team_id):
        # # Copy method of action_check
        # TODO Please update this method with action_check
        # this method return False if all are available
        # and True if not available
        # for record in self:
        start_date = fields.Datetime.from_string(record.start_date)
        end_date = fields.Datetime.from_string(record.end_date)

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

        booking_start = (start_date - datetime.timedelta(
            minutes=post_book_time)).strftime('%Y-%m-%d %H:%M:%S')
        booking_end = (end_date + datetime.timedelta(
            minutes=pre_book_time)).strftime('%Y-%m-%d %H:%M:%S')

        # Prepare serial numbers
        serial_numbers = record.equipment_ids.mapped(lambda r: r.lot_id)

        # Prepare partners
        partners = self.get_partners_auto_allocate(record, team_id)

        # Search conflict partners
        partner_names = []
        events = self.env['calendar.event'].search([
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
                validation_message += 'Employee: %s ' % (', '.join(partner_names), )
                if len(equipment_names) > 0:
                    validation_message += 'and/or '

                if len(equipment_names) > 0:
                    validation_message += 'Serial Number: %s ' % (', '.join(equipment_names),)
                # raise ValidationError(validation_message + ' has an event on that day and time')
                return True
            else:
                # raise ValidationError('Everyone is available for the booking')
                return False

    @api.multi
    def allocate_team(self):
        '''Auto allocation of the team by checking for the
        nearer zone and availability of the team'''
        zone_pool = self.env['zone.zone']
        zone_ids = zone_pool.search([])
        if not self.order_line:
            raise ValidationError(_('Please enter the service details for the Team.'))
        sic_team_free = []
        team_assign = False
        all_allocated_team = [] # ALL allocated team for normal services
        allocated_services = self.env['product.product'].search(
            [('reserved_team', '=', True)])

        for service in allocated_services:
            for team in service.team_ids:
                if team.id not in all_allocated_team:
                    all_allocated_team.append(team.id)

        print "ALL ALLOCATED TEAM ID", all_allocated_team

        # prepare arry if VAC type service added in line and also
        # we have only allocate team which are not reserverd for special
        # service
        allocate_team_product = []
        if len(self.order_line) == 1:
            for line in self.order_line:
                if line.product_id.reserved_team:
                    allocate_team_product = [team.id for team in line.product_id.team_ids]
        if not zone_ids:
            raise exceptions.UserError(
                _('There are no zone available please create it.'))
        for order in self:
            if order.team:
                raise exceptions.UserError(
                    _("Team is already allocated for the booking."))
            if not order.postal_code:
                raise exceptions.UserError(
                    _('Please add postal code for Customer %s.' % (
                        order.partner_id.name)))
            customer_zone = []
            team_availble_in_zone = {}
            for zone in zone_ids:
                for postal in zone.postal_code_ids:
                    if postal.name == str(map(str,str(order.postal_code))[0] + map(str,str(order.postal_code))[1]).zfill(2): #str(order.postal_code):
                        if customer_zone:
                            break
                        else:
                            customer_zone.append(zone)
            if customer_zone:
                slot_allocate = []
                no_one_booking_team = []
                for zone in customer_zone:
                    for team in zone.team_ids:
                        # Now we will check for the team is available or not
                        # Also we check that reserved team type service in line then
                        # we only allocate those team which are added in VAC type
                        # service

                        # first we check for normal case
                        if not team_assign and not allocate_team_product:
                            if not team.id in all_allocated_team:
                                check_result = self.action_check_auto_allocate(
                                    order, team)
                                if not check_result:
                                    order.team = team.id
                                    order._onchange_team()
                                    team_assign = True
                        # here we check for the special case
                        elif not team_assign and allocate_team_product:
                            if team.id in allocate_team_product:
                                check_result = self.action_check_auto_allocate(
                                order, team)
                                if not check_result:
                                    order.team = team.id
                                    order._onchange_team()
                                    team_assign = True
                        else:
                            continue
            # if still not allocate team then we will check in next nearest
            get_nearest_zone = []
            if not team_assign:
                for next_near_zone in customer_zone:
                    for zone in next_near_zone.seq_ids:
                        if zone.postal_code_id.name == str(map(str,str(order.postal_code))[0] + map(str,str(order.postal_code))[1]).zfill(2):
                            #get_nearest_zone = [zone for zone in zone.zone_ids]
                            for near_zone in zone.zone_ids:
                                get_nearest_zone.append(near_zone)
                for new_zone in get_nearest_zone:
                    for team in new_zone.team_ids:
                        # Now we will check for the team is available or not
                        # also normal case
                        if not team_assign and not allocate_team_product:
                            if not team.id in all_allocated_team:
                                check_result = self.action_check_auto_allocate(order, team)
                                if not check_result and not team_assign:
                                    order.team = team.id
                                    order._onchange_team()
                                    team_assign = True
                        # checking for special VAC type service product
                        if not team_assign and allocate_team_product:
                            if team.id in allocate_team_product:
                                check_result = self.action_check_auto_allocate(order, team)
                                if not check_result and not team_assign:
                                    order.team = team.id
                                    order._onchange_team()
                                    team_assign = True
                        else:
                            continue
            if not team_assign:
                raise exceptions.UserError(
                    _("Teams are not available for booking on this date.  Please try booking for another date."))

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(biocare_modifier_field_booking, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if self._context.get('default_is_booking') and view_type == 'tree':
            res['toolbar'].update( {'print': [], 'action': [], 'relate': []})
        if view_type == 'form' and self._context.get('default_is_booking'):
            #doc = etree.XML(res['arch'])
            #for node in doc.xpath("//button[@name='order_line']/form//field[@name='product_id']"):
            #    node.set('domain', "[('type', '=', 'service')]")
            res['fields']['order_line']['views']['tree']['fields']['product_id']['domain'].append(
                ('type', '=', 'service'))
            res['toolbar'].update( {'print': [], 'action': [], 'relate': []})
        elif view_type == 'form':
            res['fields']['order_line']['views']['tree']['fields']['product_id'].update(
                {'domain': [('type', 'in', ['service', 'consu', 'product']),
                            ('is_equipment', '=', False),
                            ('sale_ok', '=', True)]})
            return res
        else:
            return res
            #res['arch'] = etree.tostring(doc)
        return res

    @api.multi
    def action_create_calendar(self):
        for record in self:
            # Prepare serial numbers
            # commented due to vehicle manage by one team
            #serial_numbers = record.equipment_ids.mapped(lambda r: r.lot_id)
            serial_numbers = self.env['stock.production.lot'].search([('product_id', '=', self.vehicle_new_id.id)], limit=1)
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
                'partner_ids': [(6,0, partners and partners.ids or False)],
                'serial_numbers_ids': [(6, 0, serial_numbers and serial_numbers.ids or [])],
                'location': record.work_location_address,
                'work_order_id':record.pick_id.id,
                'booking_order_id': record.id,
            }
            calendar_obj = self.env['calendar.event'].sudo().create(data)
            record.calendar_id = calendar_obj.id

    @api.multi
    def action_todo(self):
        try:
            self.action_check()
        except ValidationError as e:
            if e.name == 'Everyone is available for the booking':

                booking_setting_obj = self.env['booking.settings'].search([], order='id desc', limit=1)
                booking_work_order = self.env['sale.order'].search(
                    [('is_booking', '=', True), ('id', '!=', self.id), ('state', '=', 'sale')])
                allowed = False
                for work_order in booking_work_order:
                    employees_exist = False
                    for sales_order_employees in self.team_employees:
                        for work_order_employees in work_order.team_employees:
                            if sales_order_employees.employee_id.id == work_order_employees.employee_id.id:
                                employees_exist = True

                    equipments_exist = False
                    for sales_order_employees in self.equipment_ids:
                        for work_order_employees in work_order.equipment_ids:
                            if sales_order_employees.product_id == work_order_employees.product_id and sales_order_employees.lot_id == work_order_employees.lot_id:
                                equipments_exist = True

                    time_exist = False
                    if self.start_date > work_order.start_date and self.start_date < work_order.end_date:
                        time_exist = True
                    if self.end_date > work_order.start_date and self.end_date < work_order.end_date:
                        time_exist = True
                    if work_order.start_date > self.start_date and work_order.start_date < self.end_date:
                        time_exist = True
                    if work_order.end_date > self.start_date and work_order.end_date < self.end_date:
                        time_exist = True

                    if time_exist == True:
                        if employees_exist == True and booking_setting_obj.block_by_worker == True:
                            allowed = True
                            break
                        if equipments_exist == True and booking_setting_obj.blook_by_equipment == True:
                            allowed = True
                            break
                if allowed == False:
                    self.action_confirm_record()
                    self.action_create_calendar()
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
    def action_draft_wo(self):
        bo_orders = self.filtered(lambda b:b.state_booking in ['cancel', 'sent'])
        bo_orders.write({
            'state_booking': 'draft',
            'procurement_group_id': False,
            'pick_id': False,
            'state': 'draft',
        })
        return bo_orders.mapped('order_line').mapped('procurement_ids').write({'sale_line_id': False})

    @api.multi
    def action_cancel(self):
        running_wo = self.picking_ids.filtered(lambda x: x.state == 'assigned')
        if running_wo:
            raise exceptions.UserError(
                _("You can not cancel Booking order because Workorder has been started."))
        super(biocare_modifier_field_booking, self).action_cancel()
        events = self.env['calendar.event'].search([
            ('booking_order_id', '=', self.id)
        ])
        if events:
            events.write({'active': False})



class Sale_order_line(models.Model):
    _inherit = 'sale.order.line'



Sale_order_line()


class biocare_modifier_fields_work_order(models.Model):
    _inherit = 'stock.picking'
    _order = "priority desc, scheduled_start desc, date asc, id desc"

    @api.multi
    @api.depends('team_employees')
    def _get_worker_name(self):
        for self_obj in self:
            self_obj.worker_name = ','.join([worker.employee_id.name for worker in self_obj.team_employees]) or ''


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

    @api.multi
    @api.depends('actual_start', 'actual_end')
    def _get_total_duration(self):
        """calculate total duartion of app"""
        for obj in self:
            if obj.actual_end and obj.actual_start:
                total = fields.Datetime.from_string(obj.actual_end) - fields.Datetime.from_string(obj.actual_start)
                obj.duration_app = total
            else:
                obj.duration_app = False

    duration_app = fields.Char(string='Duration', help='Total Duration App from actual start and actual end.',
                               compute='_get_total_duration')
    type_of_vehicle = fields.Char(string="Type of Vehicle")
    vehicle_name = fields.Char(string="Vehicle Name")
    remarks  = fields.Text(string="Remarks")
    equip_ids = fields.One2many(
        comodel_name='list.equipment.line',
        inverse_name='workorder_id', string='Equipments', help='',
        default=_get_list_equipments, copy=True)
    # To idetify reschedle of WO
    is_reschedule = fields.Boolean(
        string='Is Reschedule?', help='Technical field to identify reschedule',
        copy=False)
    reschedule_start_date = fields.Datetime(
        string='Rescheduled Start Date & Time', help='Reschedule Start Time',
        copy=False)
    reschedule_end_date = fields.Datetime(
        string='Rescheduled End Date & Time', help='Reschedule End Time',
        copy=False)
    reschedule_reason = fields.Text(
        string='Reason for Reschedule', help='Reason for the reschedule.',
        copy=False)

    worker_name = fields.Char("Worker", compute='_get_worker_name', store=True, )
    origin = fields.Char(
        'Source Document', index=True,
        states={'done': [('readonly', True)],
                'cancel': [('readonly', True)],
                'assigned': [('readonly', True)],
                'pending':   [('readonly', True)]},
        help="Reference of the document")

    partner_id = fields.Many2one(
        'res.partner', 'Partner',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)], 'assigned': [('readonly', True)]})

    ## Copy of the method from Booking order
    # Same from the BO method
    @api.model
    def get_partners_auto_allocate(self, record, team_id):
        # Prepare partner lists
        ## Copy method of get_partners
        #TODO Please update this method with get_partners
        partners = self.env['res.partner'].browse([])

        #for employee in record.team_employees:
        for employee in team_id.team_employees:
            if employee.employee_id.user_id and employee.employee_id.user_id.partner_id:
                partner = employee.employee_id.user_id.partner_id
            else:
                partner = self.env['res.partner'].create({'name': employee.employee_id.name})
                user = self.env['res.users'].create({
                    'login': employee.employee_id.name,
                    'partner_id': partner and partner.id,
                    'name': employee.employee_id.name,
                })
                employee.employee_id.user_id = user
            partners += partner

        if team_id.team_leader:
            if team_id.team_leader.user_id and team_id.team_leader.user_id.partner_id:
                partner = team_id.team_leader.user_id.partner_id
            else:
                partner = self.env['res.partner'].create({'name': team_id.team_leader.name})
                user = self.env['res.users'].create({
                    'login': team_id.team_leader.name,
                    'partner_id': partner and partner.id,
                    'name': team_id.team_leader.name,
                })
                team_id.team_leader.user_id = user
            partners += partner

        return partners

    def action_check_auto_allocate(self, record, team_id, start_date, end_date):
        # # Copy method of action_check
        #TODO Please update this method with action_check
        # this method return False if all are available
        # and True if not available
        # for record in self:

        # start_date = fields.Datetime.from_string(record.start_date)
        # end_date = fields.Datetime.from_string(record.end_date)

        start_date = fields.Datetime.from_string(start_date)
        end_date = fields.Datetime.from_string(end_date)
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

        booking_start = (start_date - datetime.timedelta(
            minutes=post_book_time)).strftime('%Y-%m-%d %H:%M:%S')
        booking_end = (end_date + datetime.timedelta(
            minutes=pre_book_time)).strftime('%Y-%m-%d %H:%M:%S')

        # Prepare serial numbers
        # serial_numbers = record.equipment_ids.mapped(lambda r: r.lot_id)
        serial_numbers = record.product_ids.mapped(lambda r: r.lot_id)

        # Prepare partners
        partners = self.get_partners_auto_allocate(record, team_id)

        # Search conflict partners
        partner_names = []
        events = self.env['calendar.event'].search([
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
                    validation_message += 'and/or '

                if len(equipment_names) > 0:
                    validation_message += 'Serial Number: %s ' % (', '.join(equipment_names),)
                # raise ValidationError(validation_message + ' has an event on that day and time')
                return True
            else:
                # raise ValidationError('Everyone is available for the booking')
                return False

    @api.model
    def allocate_team(self, st_date, end_date, pick_obj, from_reschedule=False):
        '''Auto allocation of the team by checking for the
        nearer zone and availability of the team'''
        zone_pool = self.env['zone.zone']
        zone_ids = zone_pool.search([])
        sic_team_free = []
        team_assign = False

        all_allocated_team = [] # ALL allocated team for normal services
        allocated_services = self.env['product.product'].search(
            [('reserved_team', '=', True)])

        for service in allocated_services:
            for team in service.team_ids:
                if team.id not in all_allocated_team:
                    all_allocated_team.append(team.id)

        # prepare arry if VAC type service added in line and also
        allocate_team_product = []
        sale_order_obj = self.env['sale.order'].sudo().search(
            [('name', '=', self.origin)], limit=1)
        if not sale_order_obj:
            raise ValidationError(_('No reference found for Booking order.\
                                        Sorry you can not reschedule this Workorder.'))
        if len(sale_order_obj.order_line) == 1:
            for line in sale_order_obj.order_line:
                if line.product_id.reserved_team:
                    allocate_team_product = [team.id for team in line.product_id.team_ids]

        if not zone_ids:
            raise exceptions.UserError(
                _('There are no zone available please create it.'))
        #for order in self:
        if pick_obj.team and not from_reschedule:
            raise exceptions.UserError(
                _("Team is already allocated for the booking."))
        if not pick_obj.postal_code:
            raise exceptions.UserError(
                _('Please add postal code for Customer %s.' % (
                    pick_obj.partner_id.name)))
        customer_zone = []
        team_availble_in_zone = {}
#       for zone in zone_ids:
#           for postal in zone.postal_code_ids:
#               if postal.name == str(pick_obj.postal_code):
#                   if customer_zone:
#                       break
#                   else:
#                       customer_zone.append(zone)
#       if customer_zone:
#           slot_allocate = []
#           no_one_booking_team = []
#           for zone in customer_zone:
#               for team in zone.team_ids:
#                   # Now we will check for the team is available or not
#                   if not team_assign:
#                       check_result = self.action_check_auto_allocate(
#                           pick_obj, team, st_date, end_date)
#                       if not check_result:
#                           pick_obj.team = team.id
#                           pick_obj._onchange_team()
#                           team_assign = True
#                   else:
#                       continue
#       # if still not allocate team then we will check in next nearest
#       if not team_assign:
#           for next_near_zone in customer_zone:
#               for zone in next_near_zone.seq_ids:
#                   for team in next_near_zone.team_ids:
#                       # Now we will check for the team is available or not
#                       check_result = self.action_check_auto_allocate(
#                           pick_obj, team, st_date, end_date)
#                       if not check_result and not team_assign:
#                           pick_obj.team = team.id
#                           pick_obj._onchange_team()
#                           team_assign = True
#                       else:
#                           continue

        for zone in zone_ids:
            for postal in zone.postal_code_ids:
                if postal.name == str(map(str,str(pick_obj.postal_code))[0] + map(str,str(pick_obj.postal_code))[1]).zfill(2): #str(pick_obj.postal_code):
                    if customer_zone:
                        break
                    else:
                        customer_zone.append(zone)
        if customer_zone:
            slot_allocate = []
            no_one_booking_team = []
            for zone in customer_zone:
                for team in zone.team_ids:
                    # Now we will check for the team is available or not
                    # Also we check that reserved team type service in line then
                    # we only allocate those team which are added in VAC type
                    # service

                    # first we check for normal case
                    if not team_assign and not allocate_team_product:
                        if not team.id in all_allocated_team:
                            check_result = self.action_check_auto_allocate(
                                pick_obj, team, st_date, end_date)
                            if not check_result:
                                pick_obj.team = team.id
                                pick_obj._onchange_team()
                                team_assign = True
                    # here we check for the special case
                    elif not team_assign and allocate_team_product:
                        if team.id in allocate_team_product:
                            check_result = self.action_check_auto_allocate(
                            pick_obj, team, st_date, end_date)
                            if not check_result:
                                pick_obj.team = team.id
                                pick_obj._onchange_team()
                                team_assign = True
                    else:
                        continue
        # if still not allocate team then we will check in next nearest
        get_nearest_zone = []
        # next_near_zone = []
        if not team_assign:
            for next_near_zone in customer_zone:
                for zone in next_near_zone.seq_ids:
                    if zone.postal_code_id.name == str(map(str,str(pick_obj.postal_code))[0] + map(str,str(pick_obj.postal_code))[1]).zfill(2):
                        for near_zone in zone.zone_ids:
                            get_nearest_zone.append(near_zone)
            # if next_near_zone:
            if get_nearest_zone:
                # for new_zone in get_nearest_zone.team_ids:
                for new_zone in get_nearest_zone:
                    # Now we will check for the team is available or not
                    # also checking for the VAC and normal case
                    for team in new_zone.team_ids:
                        if not team_assign and not allocate_team_product:
                            if not team.id in all_allocated_team:
                                check_result = self.action_check_auto_allocate(
                                    pick_obj, team, st_date, end_date)
                                if not check_result and not team_assign:
                                    pick_obj.team = team.id
                                    pick_obj._onchange_team()
                                    team_assign = True
                        elif not team_assign and allocate_team_product:
                            if team.id in allocate_team_product:
                                check_result = self.action_check_auto_allocate(
                                pick_obj, team, st_date, end_date)
                                if not check_result and not team_assign:
                                    pick_obj.team = team.id
                                    pick_obj._onchange_team()
                                    team_assign = True
                        else:
                            continue
        if not team_assign:
            raise exceptions.UserError(
                _("Teams are not available for booking on this date.  Please try booking for another date."))
    # # End of the copy method from BO

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(biocare_modifier_fields_work_order, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form' and self._context.get('default_is_booking'):
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//form"):
                node.set('create', 'false')
            for node in doc.xpath("//notebook/page[2]"):
                node.set('string', 'List of Services')
            #for node in doc.xpath("//notebook/page[1]"):
            #    node.set('invisible', 'True')
            for node in doc.xpath("//button[@name='action_validate']"):
                node.set('invisible', 'True')
            for node in doc.xpath("//field[@name='move_lines']"):
                node.set(
                    'context', "{ \
                    'address_in_id': partner_id,\
                    'tree_view_ref': 'biocare_field_modifier.view_move_picking_tree_wo',\
                    'form_view_ref': 'biocare_field_modifier.view_move_picking_form_wo',\
                    'default_picking_type_id': picking_type_id,\
                    'default_location_id': location_id,\
                    'default_location_dest_id': location_dest_id}")
                #res['fields']['move_lines']['views']['kanban']['fields']['product_id'].update({'domain': [('type', '=', 'service')]})
            res['arch'] = etree.tostring(doc)
        else:
            return res
        return res



