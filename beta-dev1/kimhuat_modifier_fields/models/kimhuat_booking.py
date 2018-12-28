from odoo import models, api, fields
import datetime


class kimhuat_booking_order(models.Model):
    _inherit = 'sale.order'

    contract_id = fields.Many2one('account.analytic.account', String="Contract")
    job_location = fields.Char(string="Job Location")
    job_category_id = fields.Many2one('booking.job.category',string="Job Category")
    job_detail     = fields.Text(string="Job details")
    job_detail_id  = fields.Many2one('booking.job.category.detail','Job details')
    reminder       = fields.Many2many('calendar.alarm',string="Reminder")
    remarks        = fields.Text(string='Remarks')
    customer_history_ids = fields.One2many('booking.order.line','booking_order_id',copy=True)
    quotation_title = fields.Char(string='Quotation Title')
    client_order_ref2 = fields.Char(string='Customer Reference')
    work_order_count = fields.Integer(string='Work Order', compute='_compute_work_order')

    @api.multi
    @api.depends('procurement_group_id')
    def _compute_work_order(self):
        for order in self:
            order.picking_ids = self.env['stock.picking'].search(
                [('group_id', '=', order.procurement_group_id.id)]) if order.procurement_group_id else []
            order.work_order_count = len(order.picking_ids)

    # Inherit fuction form booking_service_V2
    @api.multi
    def action_confirm_record(self):
        for record in self:
            record.action_confirm()
            record.state_booking = 'sale'
            pickings = record.mapped('picking_ids')
            if pickings:
                self.pick_id = pickings[0].id
                for picking in pickings:
                    picking.state = 'pending'
                    picking.scheduled_start = record.start_date
                    picking.scheduled_end = record.end_date
                    picking.service_rendered = record.job_detail
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

    def cron_reminder_send_mail(self):
        booking_ids = self.env['sale.order'].search([('is_booking','=',True),('state', '=', 'sale')])
        for booking_id in booking_ids:
            if booking_id.reminder:
                for reminder in booking_id.reminder:
                    flag = False
                    booking_date = datetime.datetime.strptime(booking_id.start_date, '%Y-%m-%d %H:%M:%f')
                    if reminder.interval == 'minutes':
                        date = datetime.datetime.today() + datetime.timedelta(minutes=reminder.duration)
                        if date and date.year == booking_date.year and date.month == booking_date.month and date.day == booking_date.day and date.hour == booking_date.hour and date.minute == booking_date.minute:
                            flag = True
                    if reminder.interval == 'hours':
                        date = datetime.datetime.today() + datetime.timedelta(hours=reminder.duration)
                        if date and date.year == booking_date.year and date.month == booking_date.month and date.day == booking_date.day and date.hour == booking_date.hour and date.minute == booking_date.minute:
                            flag = True
                    if reminder.interval == 'days':
                        date = datetime.datetime.today() + datetime.timedelta(days=reminder.duration)
                        if date and date.year == booking_date.year and date.month == booking_date.month and date.day == booking_date.day and date.hour == booking_date.hour and date.minute == booking_date.minute:
                            flag = True

                    if flag == True:
                        if booking_id.partner_id and booking_id.partner_id.email:
                            booking_id.send_mail_reminder(booking_id.partner_id.email,booking_id.partner_id.name,booking_id)
                        if booking_id.team_employees:
                            for enployee in booking_id.team_employees:
                                if enployee and enployee.employee_id and enployee.employee_id.work_email:
                                    booking_id.send_mail_reminder(enployee.employee_id.work_email,enployee.employee_id.name,booking_id)

    def send_mail_reminder(self,email,name,booking):
        email_from = self.company_id.email or 'Administrator <admin@example.com>'
        email_to = email
        subject = 'You have a Booking Order start day %s'%(booking.start_date)
        message = """
            <html>
                <head>
                    Dear %s,
                </head>
                <body>
                    You have a Booking Order start day: %s<br/><br/>

                    <strong>Thank you</strong>
                </body>
            <html>""" % (name, booking.start_date)

        vals = {
            'state': 'outgoing',
            'subject': subject,
            'body_html': '<pre>%s</pre>' % message,
            'email_to': email_to,
            'email_from': email_from,
        }
        if vals:
            email_id = self.env['mail.mail'].create(vals)
            if email_id:
                email_id.send()



    @api.onchange('job_category_id')
    def onchange_job_category(self):
        if self.job_category_id:
            self.job_detail = self.job_category_id.job_detail

    @api.model
    def create(self, vals):
        if vals.get('client_order_ref2', False):
            vals.update({
                'client_order_ref' : vals.get('client_order_ref2')
            })
        res = super(kimhuat_booking_order, self).create(vals)
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
            current_year = datetime.datetime.now().strftime('%y')
            name_booking = "BR/%s/%s" % (current_year, '{0:03}'.format(name_number_current))
            res.write({
                'name': name_booking,
                'name_number': name_number_current
            })
        return res
    @api.multi
    def write(self,vals):
        if vals.get('client_order_ref2', False):
            vals.update({
                'client_order_ref': vals.get('client_order_ref2')
            })
        res = super(kimhuat_booking_order, self).write(vals)
        return res

    @api.onchange('partner_id')
    def onchage_customer(self):
        if self.partner_id:
            customer_history_ids = self.env['sale.order'].search(
                [('partner_id', '=', self.partner_id.id), ('state', '=', 'sale')])
            self.customer_history_ids = None
            for customer_history_id in customer_history_ids:
                self.customer_history_ids += self.customer_history_ids.new({
                    'order_number': customer_history_id.name,
                    'date_order': customer_history_id.date_order,
                    'salesperson': customer_history_id.user_id,
                    'amount_total': customer_history_id.amount_total,
                })
        if self.partner_id:
            self.street2 = self.partner_id.street2
            self.street = self.partner_id.street
            self.city = self.partner_id.city
            self.state_id = self.partner_id.state_id
            self.zip = self.partner_id.zip
            self.country_id = self.partner_id.country_id
            self.phone = self.partner_id.phone
            self.email = self.partner_id.email

        if self.partner_id:
            if self.date_order:
                return {'domain': {'contract_id': [('date_start', '<=', self.date_order),('date_end', '>=', self.date_order)]}}
            else:
                return {}
        else:
            return {'domain': {'contract_id': []}}

    @api.onchange('date_order')
    def onchanger_date_order(self):
        if self.date_order:
            date_order = datetime.datetime.strptime(self.date_order, '%Y-%m-%d %H:%M:%S')
            self.validity_date = (date_order + datetime.timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
        if self.partner_id and self.date_order:
            return {
                'domain': {'contract_id': [('date_start', '<=', self.date_order), ('date_end', '>=', self.date_order)]}}
        else:
            return {'domain': {'contract_id': []}}

    @api.multi
    def action_view_work_order(self):
        '''
        This function returns an action that display existing delivery orders
        of given sales order ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        '''
        action = self.env.ref('booking_service_V2.work_order_action').read()[0]

        pickings = self.mapped('picking_ids')
        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)]
        elif pickings:
            action['views'] = [(self.env.ref('kimhuat_modifier_fields.view_work_order_form').id, 'form')]
            action['res_id'] = pickings.id
        return action

kimhuat_booking_order()

class job_category_booking(models.Model):
    _name = 'booking.job.category'

    name = fields.Char(String="Name")
    job_detail = fields.Text(string='Job Detail')
    job_detail_ids = fields.One2many('booking.job.category.detail','job_category_id','Job Detail')

class job_detail_category_booking(models.Model):
    _name = 'booking.job.category.detail'

    name = fields.Char(string='Job Detail')
    job_category_id = fields.Many2one('booking.job.category','Job Category')

class kimhuat_booking_order_history(models.Model):
    _name = 'booking.order.line'

    order_number = fields.Char()
    date_order = fields.Datetime()
    salesperson = fields.Many2one('res.users')
    amount_total = fields.Float()
    booking_order_id = fields.Many2one('sale.order')

class kimhuat_booking_order_service_chit(models.Model):
    _name = 'booking.service.chit'

    no_number = fields.Char(string="No", readonly=True)
    brand = fields.Char(string="Brand")
    model_make = fields.Char(string="Model/Make")
    serial = fields.Char(string="Serial")
    type = fields.Char(string="Type")
    on_coil_temp = fields.Char(string="On Coil Temp")
    off_coil_temp = fields.Char(string="Off Coil Temp")
    suctn = fields.Char(string="Suctn P/sure")
    work_order_id = fields.Many2one('stock.picking')

class booking_pcf_service_chit_tree_1(models.Model):
    _name = 'booking.pcf.service.chit.tree.1'

    type_of_aircon = fields.Many2one('product.type', string="Type of Aircon")
    units_to_service = fields.Integer(string="No. of units to Service")
    units_serviced = fields.Integer(string="No. of units Serviced")
    work_order_id = fields.Many2one('stock.picking')

class booking_service_chit_tree_2(models.Model):
    _name = 'booking.pcf.service.chit.tree.2'

    type_of_fan = fields.Many2one('type.of.fan', string="Type of Fan")
    units_to_service = fields.Integer(string="No. of units to Service")
    units_serviced = fields.Integer(string="No. of units Serviced")
    work_order_id = fields.Many2one('stock.picking')

class booking_pcf_service_chit_tree_3(models.Model):
    _name = 'booking.pcf.service.chit.tree.3'

    brand = fields.Char(string="Brand")
    model_no = fields.Char(string="Model No")
    type = fields.Char(string="Type")
    serial_no = fields.Char(string="Serial No")
    location = fields.Char(string="Location")
    work_order_id = fields.Many2one('stock.picking')

class kimhuat_work_order(models.Model):
    _inherit = 'stock.picking'

    contract_id = fields.Many2one('account.analytic.account', String="Contract",related='sale_id.contract_id')
    job_house_no = fields.Char(string="House No", related='sale_id.job_house_no')
    job_level_no = fields.Char(string="Level No", related='sale_id.job_level_no')
    job_unit_no  = fields.Char(string="Unit No", related='sale_id.job_unit_no')
    job_street = fields.Char(related='sale_id.job_street')
    job_street2 = fields.Char(related='sale_id.job_street2')
    job_zip = fields.Char(change_default=True,related='sale_id.job_zip')
    job_city = fields.Char(related='sale_id.job_city')
    job_state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',related='sale_id.job_state_id')
    job_country_id = fields.Many2one('res.country', string='Country', ondelete='restrict',related='sale_id.job_country_id')
    job_location = fields.Char(string="Job Location",related='sale_id.job_location')
    job_category_id = fields.Many2one('booking.job.category',string="Job Category",related='sale_id.job_category_id')
    job_detail     = fields.Text(string="Job details",related='sale_id.job_detail')
    job_detail_id  = fields.Many2one('booking.job.category.detail','Job details',related='sale_id.job_detail_id')

    picking_house_no = fields.Char(string="House No",)
    picking_level_no = fields.Char(string="Level No",)
    picking_unit_no = fields.Char(string="Unit No", )
    picking_street = fields.Char()
    picking_street2 = fields.Char()
    picking_zip = fields.Char(change_default=True,)
    picking_city = fields.Char()
    picking_state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',)
    picking_country_id = fields.Many2one('res.country', string='Country', ondelete='restrict',)
    deliver_to_job_site = fields.Boolean(string="Deliver to Job Site")


    reminder       = fields.Many2many('calendar.alarm',string="Reminder")
    remarks        = fields.Text(string='Remarks')

    service_chit = fields.One2many('booking.service.chit', 'work_order_id')


    symptoms_observations = fields.Text(string="Symptoms & Observations")
    service_rendered = fields.Text(string="Service Rendered")
    recommendations = fields.Text(string="Recommendations")
    payment_mode = fields.Many2one('payment.mode', string="Payment Mode")
    payment_made = fields.Integer(string="Payment Made")

    air_filter_cleaned = fields.Boolean(string="Air Filter Cleaned")
    bearings_oiled = fields.Boolean(string="Bearings Oiled")
    coils_cleaned = fields.Boolean(string="Coils Cleaned")
    condenser_coil_cleaned = fields.Boolean(string="Condenser Coil Cleaned")
    controls_checked = fields.Boolean(string="Controls Checked")
    discharged_pressure_checked = fields.Boolean(string="Discharged Pressure Checked")
    drain_tray_drain_pipe_cleaned = fields.Boolean(string="Drain Tray / Drain Pipe Cleaned")
    drives_checked = fields.Boolean(string="Drives Checked")
    evaporator_coil = fields.Boolean(string="Evaporator Coil")
    fan_blower_cleaned = fields.Boolean(string="Fan Blower Cleaned")
    fan_coil_cover_cleaned = fields.Boolean(string="Fan Coil Cover Cleaned")
    flushed_drainage = fields.Boolean(string="Flushed Drainage")
    suction_pressure_checked = fields.Boolean(string="Suction Pressure Checked")
    thermostat_checked = fields.Boolean(string="Thermostat Checked")
    pumps_checked = fields.Boolean(string="Pumps Checked")

    pcf_service_chit_tree_1_ids = fields.One2many('booking.pcf.service.chit.tree.1', 'work_order_id')
    pcf_service_chit_tree_2_ids = fields.One2many('booking.pcf.service.chit.tree.2', 'work_order_id')
    pcf_service_chit_tree_3_ids = fields.One2many('booking.pcf.service.chit.tree.3', 'work_order_id')

    header = fields.Text(string="Comments / Complaint / Follow up")
    time_in_pcf = fields.Float(string='Time In')
    time_out_pcf = fields.Float(string='Time Out')
    state = fields.Selection([
        ('draft', 'Draft'), ('cancel', 'Cancelled'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting Availability'),
        ('partially_available', 'Partially Available'), ('pending', 'Pending'),
        ('assigned', 'Available'),('started', 'Started'), ('done', 'Done')], string='Status', compute='_compute_state',
        copy=False, index=True, readonly=True, store=True, track_visibility='onchange',
        help=" * Draft: not confirmed yet and will not be scheduled until confirmed\n"
             " * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n"
             " * Waiting Availability: still waiting for the availability of products\n"
             " * Partially Available: some products are available and reserved\n"
             " * Ready to Transfer: products reserved, simply waiting for confirmation.\n"
             " * Transferred: has been processed, can't be modified or cancelled anymore\n"
             " * Cancelled: has been cancelled, can't be confirmed anymore")
    reschedule_reason = fields.Text(
        string='Reason for Reschedule', help='Reason for the reschedule.',
        copy=False)
    is_reschedule = fields.Boolean(
        string='Is Reschedule?', help='Technical field to identify reschedule',
        copy=False)
    replacement = fields.Char('Replacement')
    observations = fields.Char('Observations')
    recommendation = fields.Char('Recommendation')
    repair = fields.Char('Repair')
    photo = fields.Binary('Photo',attachment=True)
    signature = fields.Binary('Customer Signature')
    signature_full_name = fields.Char('Signature Full Name')
    signature_date = fields.Date('Signature Date')
    service_signature = fields.Binary('Service Man Sign')
    service_signature_full_name = fields.Char('Signature Full Name')
    service_signature_date = fields.Date('Signature Sign Date')
    booking_installation_id = fields.One2many('booking.installation','work_order_id')
    stamp = fields.Binary('Stamp')

    @api.onchange('signature')
    def onchange_signature(self):
        if self.signature:
            self.signature_date = fields.datetime.today()


    @api.onchange('job_detail')
    def onchanger_job_detail_id(self):
        if self.job_detail:
            self.service_rendered = self.job_detail

    @api.onchange('job_category_id')
    @api.depends('job_category_id')
    def onchange_job_category(self):
        if self.job_category_id:
            self.job_detail = self.job_category_id.job_detail

    @api.multi
    def action_set_to_draft(self):
        bo_orders = self.filtered(lambda b: b.state_booking in ['cancel', 'sent'])
        bo_orders.write({
            'state_booking': 'draft',
            'procurement_group_id': False,
            'pick_id': False,
            'state': 'draft',
        })
        return bo_orders.mapped('order_line').mapped('procurement_ids').write({'sale_line_id': False})

    ## Copy of the method from Booking order
    # Same from the BO method

    @api.model
    def get_partners_auto_allocate(self, record, team_id):
        # Prepare partner lists
        ## Copy method of get_partners
        # TODO Please update this method with get_partners
        partners = self.env['res.partner'].browse([])

        # for employee in record.team_employees:
        for employee in team_id.team_employees:
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

        if team_id.team_leader:
            if team_id.team_leader.user_id and team_id.team_leader.user_id.partner_id:
                partner = team_id.team_leader.user_id.partner_id
            else:
                partner = self.env['res.partner'].create({'name': team_id.team_leader.name})
                user = self.env['res.users'].create({
                    'login': team_id.team_leader.name,
                    'partner_id': partner and partner.id,
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

        book_setting = self.env.ref('booking_service_V2.setting_data')
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

    @api.multi
    def action_start(self):
        for record in self:
            partners = self.get_partners(record)
            record.actual_start = fields.Datetime.now()
            record.state = 'started'

    @api.multi
    def action_validate(self):
        for record in self:
            if record.state == 'assigned' or record.state == 'started':
                record.actual_end = fields.Datetime.now()
                record.state = 'done'

kimhuat_work_order()

class booking_installation(models.Model):
    _name = 'booking.installation'

    location = fields.Char(string="Location")
    designation_cu = fields.Char(string="Designation CU")
    designation_fcu = fields.Char(string="Designation FCU")
    type = fields.Char(string="Type")
    model_cu = fields.Char(string="Model CU")
    model_fcu = fields.Char(string="Model FCU")
    serial_no_cu = fields.Char(string="Serial No. CU")
    serial_no_fcu = fields.Char(string="Serial No. FCU")

    work_order_id = fields.Many2one('stock.picking')

