# -*- coding: utf-8 -*
from openerp import api, exceptions, fields, models, _
import datetime
import pytz
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.addons.auth_signup.models.res_partner import SignupError, now

class res_users(models.Model):
    _inherit = "res.users"

    @api.multi
    def get_user_data_app(self):
        if self.env.user.has_group('booking_service_V2.group_manager') or self.env.user.has_group('booking_service_V2.group_user'):
            vals={}
            vals["name"] = self.env.user.name
            vals["email"] = self.env.user.email if self.env.user.email else ""
            vals["image_medium"] = self.env.user.image_medium if self.env.user.image_medium else ""
            vals["mobile"] = self.env.user.mobile if self.env.user.mobile else ""
            vals["partner_id"] = self.env.user.partner_id.id
            return vals
        else:
            return False

    @api.multi
    def action_reset_password_app(self):
        """ create signup token for each user, and send their signup url by email """
        # prepare reset password signup
        create_mode = bool(self.env.context.get('create_user'))

        # no time limit for initial invitation, only for reset password
        expiration = False if create_mode else now(days=+1)

        self.mapped('partner_id').signup_prepare(signup_type="reset", expiration=expiration)

        # send email to users with their signup url
        template = False
        if create_mode:
            try:
                template = self.env.ref('auth_signup.set_password_email', raise_if_not_found=False)
            except ValueError:
                pass
        if not template:
            template = self.env.ref('auth_signup.reset_password_email')
        assert template._name == 'mail.template'

        for user in self:
            if not user.email:
                return "Cannot send email: user %s has no email address."
            else:
                template.with_context(lang=user.lang).send_mail(user.id, force_send=True, raise_exception=True)
                return "Password reset email sent for user <%s> to <%s>", user.login, user.email

    @api.multi
    def reset_password_from_mobile_app(self, login):
        """ retrieve the user corresponding to login (login or email),
            and reset their password
        """
        users = self.search([('login', '=', login)],limit=1)
        if users:
            return users.action_reset_password_app()
        else:
            return 'Invalid username or email.please contact your admin.'


res_users()

class work_order_notification(models.Model):
    _name = "work.order.notification"

    customer_id = fields.Many2one('res.partner','Customer')
    work_order_id = fields.Many2one('stock.picking','Work Order')
    booking_name = fields.Char('Booking Ref')
    work_location = fields.Char('Work Location')
    team_id = fields.Many2one('booking.team','Team')
    team_leader_id = fields.Many2one('hr.employee','Team Leader')
    team_employees_ids = fields.Many2many('res.partner')
    subject = fields.Char('Subject')
    remarks = fields.Char('Remarks')
    state = fields.Char('State')
    created_date = fields.Char('Created Date')
    reschedule_startdate = fields.Datetime('Reschedule Start Date')
    reschedule_enddate = fields.Datetime('Reschedule End Date')

    @api.multi
    def get_notification_data_app(self, user_id):
        notification = []
        partner_id = self.env['res.users'].browse(user_id).partner_id
        notification_ids = self.env['work.order.notification'].search([('team_employees_ids', 'in', partner_id.id)], order="id desc")
        for notification_obj in notification_ids:
            vals = {}
            vals['id'] = notification_obj.id
            vals['work_order_name'] = notification_obj.work_order_id.name if notification_obj.work_order_id else ""
            vals['booking_name'] = notification_obj.booking_name if notification_obj.booking_name else ""
            vals['created_date'] = notification_obj.created_date if notification_obj.created_date else ""
            vals['subject'] = notification_obj.subject
            notification.append(vals)
        return notification

work_order_notification()

class stock_picking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def get_wo_installation_app(self):
        wo_obj = self.search([('id','=', self.id)])
        install_list = []
        if wo_obj:
            for install in wo_obj.booking_installation_id:
                vals = {}
                vals['id'] = install.id
                vals['location'] = install.location or ''
                vals['designation_cu'] = install.designation_cu or ''
                vals['designation_fcu'] = install.designation_fcu or ''
                vals['model_cu'] = install.model_cu or ''
                vals['model_fcu'] =  install.model_fcu or''
                vals['serial_no_cu'] = install.serial_no_cu or ''
                vals['serial_no_fcu'] = install.serial_no_fcu or ''
                install_list.append(vals)
            return install_list
        else:
            return False


    @api.multi
    def update_wo_installation_app(self,vals):
        workorder_obj = self.search([('id', '=', self.id)], limit=1)
        # vals = [{"location":"loca-sig","designation_cu":"cu-001","designation_fcu":"fcu-dest",
        #         "model_cu":"cu-mod001", "model_fcu":"fcu-model-001","serial_no_cu":"serial-001-cu","serial_no_fcu":"serial-fcu-0023"},
        #         {"location":"loca-sig1","designation_cu":"cu-0011","designation_fcu":"fcu-dest1","model_cu":"cu-mod0011",
        #         "model_fcu":"fcu-model-0011","serial_no_cu":"serial-001-cu1","serial_no_fcu":"serial-fcu-00231"}]
        install_list = []
        if workorder_obj:
            for install in vals:
                install_vals = {}
                install_vals['location'] = install.get('location','')
                install_vals['designation_cu'] = install.get('designation_cu','')
                install_vals['designation_fcu'] = install.get('designation_fcu','')
                install_vals['model_cu'] = install.get('model_cu','')
                install_vals['model_fcu'] = install.get('model_fcu','')
                install_vals['serial_no_cu'] = install.get('serial_no_cu','')
                install_vals['serial_no_fcu'] = install.get('serial_no_fcu','')
                install_list.append((0,0,install_vals))
            if workorder_obj and install_list:
                workorder_obj.booking_installation_id = install_list
            return True
        else:
            return False

    @api.multi
    def removed_installation_app(self, booking_installation_id):
        wo_obj = self.search([('id', '=', self.id)])
        bi_obj = self.env['booking.installation'].search([('id', '=', booking_installation_id)])
        if wo_obj and bi_obj:
            wo_obj.booking_installation_id = [(2, bi_obj.id)]
            return True
        else:
            return False

    @api.multi
    def get_work_order_address(self, stock_obj):
        stock_obj = self.search([('id', '=', stock_obj.id)], limit=1, order="id desc")
        if stock_obj:
            job_house_no = ''
            job_level_no = ''
            job_unit_no = ''
            job_street = ''
            job_street2 = ''
            job_city = ''
            job_state_id = ''
            job_zip = ''
            job_country_id = ''

            if stock_obj.job_house_no:
                job_house_no = stock_obj.job_house_no + ','
            if stock_obj.job_level_no:
                job_level_no = stock_obj.job_level_no + ','
            if stock_obj.job_unit_no:
                job_unit_no = stock_obj.job_unit_no + ','
            if stock_obj.job_street:
                job_street = stock_obj.job_street + ','
            if stock_obj.job_street2:
                job_street2 = stock_obj.job_street2 + ','
            if stock_obj.job_city:
                job_city = stock_obj.job_city + ','
            if stock_obj.job_state_id:
                job_state_id = stock_obj.job_state_id.name + ','
            if stock_obj.job_country_id:
                job_country_id = stock_obj.job_country_id.name + ','
            if stock_obj.job_zip:
                job_zip = stock_obj.job_zip
            address = job_street + job_street2  + job_country_id + job_zip
            return address

    @api.multi
    def get_workorder_app(self,workorder_id):
        work_order_obj = self.search([('id','=',workorder_id)], order="id desc")
        if work_order_obj:
            address = work_order_obj.get_work_order_address(work_order_obj)
            vals = {}
            vals['work_order_id'] = work_order_obj.id
            vals['work_order_name'] = work_order_obj.name
            vals['booking_no'] = work_order_obj.origin or ''
            vals['partner_name'] = work_order_obj.partner_id.name if work_order_obj.partner_id else ''
            vals['scheduled_start'] = work_order_obj.scheduled_start or ''
            vals['scheduled_end'] = work_order_obj.scheduled_end or ''
            vals['actual_start'] = work_order_obj.actual_start or ''
            vals['actual_end'] = work_order_obj.actual_end or ''
            vals['team_name'] = work_order_obj.team.name if work_order_obj.team else ''
            emp = []
            for emp_obj in work_order_obj.team_employees:
                emp.append(emp_obj.employee_id.name)
            vals["team_employees"] = emp
            booking_order_obj = self.env['sale.order'].search([('name', '=', work_order_obj.origin)], limit=1)
            vals['phone_number'] = booking_order_obj.phone if booking_order_obj.phone else ''
            vals['mobile_number'] = work_order_obj.partner_id.mobile if work_order_obj.partner_id.mobile else ''
            vals['email'] = work_order_obj.partner_id.email if work_order_obj.partner_id.email else ''
            vals[
                'destination_location_zone'] = work_order_obj.location_dest_id.name if work_order_obj.location_dest_id else ''
            vals['scheduled_date'] = work_order_obj.min_date or ''
            vals['source_document'] = work_order_obj.origin or ''
            vals['contract_name'] = work_order_obj.contract_id.name if work_order_obj.contract_id else ''
            vals['job_site'] = address if address else ''
            vals['job_location'] = work_order_obj.job_location or ''
            vals['job_category'] = work_order_obj.job_category_id.name if work_order_obj.job_category_id else ''
            vals['job_details'] = work_order_obj.job_detail or ''
            reminder = []
            for rem in work_order_obj.reminder:
                reminder.append(rem.name)
            vals['reminder'] = reminder
            vals['remarks'] = booking_order_obj.remarks if booking_order_obj.remarks else ''
            state = ''
            if work_order_obj.state == 'pending':
                state = 'Pending'
            elif work_order_obj.state == 'started':
                state = 'Started'
            elif work_order_obj.state == 'done':
                state = 'Completed'
            elif work_order_obj.state == 'cancel':
                state = 'Cancelled'
            vals['status'] = state
            return vals

    @api.multi
    @api.depends('actual_start', 'actual_end')
    def _get_total_duration(self):
        """calculate total duartion of app"""
        for obj in self:
            if obj.actual_end and obj.actual_start:
                total = fields.Datetime.from_string(obj.actual_end) - fields.Datetime.from_string(obj.actual_start)
                dt = str(total).split(":")[0]
                if dt == '0':
                    total = "0"+str(total)
                obj.duration_app = total
            else:
                obj.duration_app = False

    duration_app = fields.Char(string='Duration', help='Total Duration App from actual start and actual end.',
        compute='_get_total_duration')

    @api.multi
    def action_start(self):
        res = super(stock_picking,self).action_start()
        for record in self:
            if record.state == 'started':
                partners = self.get_partners(record)
                address = record.get_work_order_address(record)
                vals = {}
                try:
                    partner_name = record.partner_id.name.encode('utf-8')
                except:
                    partner_name = record.partner_id.name
                if address:
                    try:
                        addr = address.encode('utf-8')
                    except:
                        addr = address
                    subject = 'Your work order('+str(record.name)+') with ('+str(partner_name or '')+'), ('+ str(addr) +') scheduled on ('+ str(record.scheduled_start[0:10]) + ') has been started.Thank You.'
                else:
                    subject = 'Your work order('+str(record.name)+') with ('+str(partner_name or '')+') scheduled on ('+str(record.scheduled_start[0:10]) + ') has been started.Thank You.'
                vals['work_order_id'] = record.id
                vals['customer_id'] = record.partner_id.id if record.partner_id else False
                vals['booking_name'] = record.origin if record.origin else ''
                vals['work_location'] = address if address else ''
                vals['team_id'] = record.team.id if record.team else False
                vals['team_employees_ids'] = [(6, 0, partners.ids)]
                vals['subject'] = subject
                # vals['phone'] = record.phone or ''
                vals['state'] = 'Started'
                vals['created_date'] = fields.Datetime.now()
                record.env['work.order.notification'].create(vals)
        return res

    # end function  for erp side
    @api.multi
    def action_validate_app(self):
        if self.signature and self.service_signature:
            for record in self:
                partners = self.get_partners(record)
                if record.state == 'assigned' or record.state == 'started':
                    super(stock_picking, record).action_validate()
                    address = record.get_work_order_address(record)
                    vals = {}
                    try:
                        partner_name = record.partner_id.name.encode('utf-8')
                    except:
                        partner_name = record.partner_id.name
                    if address:
                        try:
                            addr = address.encode('utf-8')
                        except:
                            addr = address
                        subject = 'Your work order(' + str(record.name) + ') with (' + str(
                            partner_name or '') + '), (' + str(addr) + ') scheduled on (' + str(
                            record.scheduled_start[0:10]) + ') has been completed successfully. Thank You.'
                    else:
                        subject = 'Your work order(' + str(record.name) + ') with (' + str(
                            partner_name or '') + ') scheduled on (' + str(record.scheduled_start [0:10]) + ') has been completed successfully. Thank You.'
                    vals['customer_id'] = record.partner_id.id if record.partner_id else False
                    vals['work_order_id'] = record.id
                    vals['booking_name'] = record.origin if record.origin else ''
                    vals['work_location'] = address if address else ''
                    vals['team_id'] = record.team.id if record.team else False
                    vals['team_employees_ids'] = [(6, 0, partners.ids)]
                    vals['subject'] = subject
                    vals['remarks'] = record.remarks if record.remarks else ''
                    vals['state'] = 'Completed'
                    vals['created_date'] = fields.Datetime.now()
                    record.env['work.order.notification'].create(vals)
                    return "Success"
        else:
            return "False"

    # end function  for erp side
    @api.multi
    def action_validate(self):
        for record in self:
            super(stock_picking, record).action_validate()
            partners = self.get_partners(record)
            address = record.get_work_order_address(record)
            vals = {}
            try:
                partner_name = record.partner_id.name.encode('utf-8')
            except:
                partner_name = record.partner_id.name
            if address:
                try:
                    addr = address.encode('utf-8')
                except:
                    addr = address
                subject = 'Your work order(' + str(record.name) + ') with (' + str(
                    partner_name or '') + '), (' + str(addr) + ') scheduled on (' + str(
                    record.scheduled_start[0:10]) + ') has been completed successfully. Thank You.'
            else:
                subject = 'Your work order(' + str(record.name) + ') with (' + str(
                    partner_name or '') + ') scheduled on (' + str(
                    record.scheduled_start[0:10]) + ') has been completed successfully. Thank You.'
            vals['customer_id'] = record.partner_id.id if record.partner_id else False
            vals['work_order_id'] = record.id
            vals['booking_name'] = record.origin if record.origin else ''
            vals['work_location'] = address if address else ''
            vals['team_id'] = record.team.id if record.team else False
            vals['team_employees_ids'] = [(6, 0, partners.ids)]
            vals['subject'] = subject
            vals['remarks'] = record.remarks if record.remarks else ''
            vals['state'] = 'Completed'
            vals['created_date'] = fields.Datetime.now()
            record.env['work.order.notification'].create(vals)


    @api.multi
    def get_work_orders(self, user_id,get_state):
        work_orders = []
        employee_id = self.env['hr.employee'].search([('resource_id.user_id', '=', user_id)], limit=1).ids
        if not employee_id:
            employee_id = self.env['hr.employee'].search([('user_id', '=', user_id)], limit=1).ids

        work_order_ids = self.env['stock.picking'].search([('team_employees.employee_id', 'in', employee_id), ("state", "=", get_state)], order="id desc")
        for work_order_obj in work_order_ids:
            vals = {}
            vals['work_order_id'] = work_order_obj.id
            vals['work_order_name'] = work_order_obj.name
            vals['booking_no'] = work_order_obj.origin or ''
            vals['partner_name'] = work_order_obj.partner_id.name if work_order_obj.partner_id else ''
            vals['scheduled_start'] = work_order_obj.scheduled_start or ''
            vals['scheduled_end'] = work_order_obj.scheduled_end or ''
            vals['actual_start'] = work_order_obj.actual_start or ''
            vals['actual_end'] = work_order_obj.actual_end or ''
            vals['team_name'] = work_order_obj.team.name if work_order_obj.team else ''
            emp = []
            for emp_obj in work_order_obj.team_employees:
                emp.append(emp_obj.employee_id.name)
            # address = str(work_order_obj.job_house_no or  '') +', '+ str(work_order_obj.job_level_no or  '') +', '+str(work_order_obj.job_unit_no or '') +', ' +str(work_order_obj.job_street or '') + ', '+str(work_order_obj.job_street2 or '') + ', '+ str(work_order_obj.job_city or '')+ ', ' +str(work_order_obj.job_state_id.name if work_order_obj.job_state_id else  '')+', ' +str(work_order_obj.job_zip)+ ', '+str(work_order_obj.job_country_id.name if work_order_obj.job_category_id else '')
            address = work_order_obj.get_work_order_address(work_order_obj)
            vals["team_employees"] = emp
            booking_order_obj = self.env['sale.order'].search([('name', '=', work_order_obj.origin)], limit=1)
            vals['phone_number'] = booking_order_obj.phone if booking_order_obj.phone else ''
            vals['mobile_number'] = work_order_obj.partner_id.mobile if work_order_obj.partner_id.mobile else ''
            vals['email'] = work_order_obj.partner_id.email if work_order_obj.partner_id.email else ''
            vals['destination_location_zone'] = work_order_obj.location_dest_id.name if work_order_obj.location_dest_id else ''
            vals['scheduled_date'] = work_order_obj.min_date or  ''
            vals['source_document'] = work_order_obj.origin or ''
            vals['contract_name'] = work_order_obj.contract_id.name if work_order_obj.contract_id else ''
            vals['job_site'] = address
            vals['job_location'] = work_order_obj.job_location or ''
            vals['job_category'] = work_order_obj.job_category_id.name if work_order_obj.job_category_id.name else ''
            vals['job_details'] = work_order_obj.job_detail or ''
            reminder = []
            for rem in work_order_obj.reminder:
                reminder.append(rem.name)
            vals['reminder'] = reminder
            vals['remarks'] = booking_order_obj.remarks if booking_order_obj.remarks else ''
            vals['status'] = work_order_obj.state
            # append order lines of booking order
            order_lines = []
            for lines in booking_order_obj.order_line:
                order_lines_dict = {}
                order_lines_dict['brand'] = lines.brand.name if lines.brand.name else ''
                order_lines_dict['type'] = lines.type.name if lines.type.name else ''
                order_lines_dict['product_id'] = lines.product_id.name if lines.product_id.name else ''
                order_lines_dict['product_uom_qty'] = lines.product_uom_qty or ''
                order_lines_dict['description'] = lines.description or ''
                order_lines.append(order_lines_dict)
            vals['order_lines'] = order_lines

            # kimhuat chit funds
            service_list = []
            service_vals = {}
            service_vals['air_filter_cleaned'] = work_order_obj.air_filter_cleaned or ''
            service_vals['bearings_oiled'] = work_order_obj.bearings_oiled or ''
            service_vals['coils_cleaned'] = work_order_obj.coils_cleaned or ''
            service_vals['condenser_coil_cleaned'] = work_order_obj.condenser_coil_cleaned or ''
            service_vals['controls_checked'] = work_order_obj.controls_checked or ''
            service_vals['discharged_pressure_checked'] = work_order_obj.discharged_pressure_checked or ''
            service_vals['drain_tray_drain_pipe_cleaned'] = work_order_obj.drain_tray_drain_pipe_cleaned or ''
            service_vals['drives_checked'] = work_order_obj.drives_checked or ''
            service_vals['evaporator_coil'] = work_order_obj.evaporator_coil or ''
            service_vals['fan_blower_cleaned'] = work_order_obj.fan_blower_cleaned or ''
            service_vals['fan_coil_cover_cleaned'] = work_order_obj.fan_coil_cover_cleaned or ''
            service_vals['flushed_drainage'] = work_order_obj.flushed_drainage or ''
            service_vals['suction_pressure_checked'] = work_order_obj.suction_pressure_checked or ''
            service_vals['thermostat_checked'] = work_order_obj.thermostat_checked or ''
            service_vals['pumps_checked'] = work_order_obj.pumps_checked or ''
            service_list.append(service_vals)
            vals['service'] = service_list
            work_orders.append(vals)
        return work_orders

    @api.multi
    def get_dashboard_notification_counts(self, user_id):
        vals={}
        date_today = fields.Datetime.from_string(fields.Datetime.now())
        from_date = (date_today + datetime.timedelta(days=1)).replace( hour=00, minute=00, second=01)
        to_date = (date_today + datetime.timedelta(days=1)).replace( hour=23, minute=59, second=59)

        employee_id = self.env['hr.employee'].search([('resource_id.user_id', '=', user_id)], limit=1).ids
        if not employee_id:
            employee_id = self.env['hr.employee'].search([('user_id', '=', user_id)], limit=1).ids
        work_order_ids = []
        work_order_employee_ids = self.env['working.order.employee'].search([('employee_id', 'in', employee_id)])
        pending_work_count = 0
        completed_work_count = 0
        reminder_work_count = 0
        notification_ids = self.env['work.order.notification'].search([('team_employees_ids', 'in', employee_id)])
        for temp_obj in work_order_employee_ids:
            if temp_obj.order_id.scheduled_start >= fields.Datetime.to_string(from_date) and temp_obj.order_id.scheduled_start <= fields.Datetime.to_string(to_date):
                reminder_work_count += 1
            if temp_obj.order_id.state == "pending":
                pending_work_count += 1
            elif temp_obj.order_id.state == "done":
                completed_work_count +=1
        vals["pending_work_order_count"] = pending_work_count
        vals["completed_work_order_count"] = completed_work_count
        vals["reminders_work_order_count"] = reminder_work_count
        vals["notification_count"] = len(notification_ids)
        return vals

    @api.multi
    def get_pcf_service_chit_app(self):
        pcf_service = []
        work_order_ids = self.search([('id', '=', self.id)], order="id desc")
        for work_order_obj in work_order_ids:
            vals = {}
            # PCF Chit funds
            pcf1_list = []
            for pcf1 in work_order_obj.pcf_service_chit_tree_1_ids:
                pcf1_dict = {}
                pcf1_dict['type_of_aircon'] = pcf1.type_of_aircon.name if pcf1.type_of_aircon.name else ''
                pcf1_dict['units_to_service'] = pcf1.units_to_service
                pcf1_dict['units_serviced'] = pcf1.units_serviced
                pcf1_dict['id'] = pcf1.id
                pcf1_list.append(pcf1_dict)
            vals['pcf_aircon'] = pcf1_list
            # pcf chit funds2
            pcf2_list = []
            for pcf2 in work_order_obj.pcf_service_chit_tree_2_ids:
                pcf2_dict = {}
                pcf2_dict['type_of_fan'] = pcf2.type_of_fan.name if pcf2.type_of_fan.name else ''
                pcf2_dict['units_to_service'] = pcf2.units_to_service or 0
                pcf2_dict['units_serviced'] = pcf2.units_serviced or 0
                pcf2_dict['id'] = pcf2.id
                pcf2_list.append(pcf2_dict)
            vals['pcf_fan'] = pcf2_list

            # pcf chit funds3
            pcf3_list = []
            for pcf3 in work_order_obj.pcf_service_chit_tree_3_ids:
                pcf3_dict = {}
                pcf3_dict['brand'] = pcf3.brand or ''
                pcf3_dict['model_no'] = pcf3.model_no or ''
                pcf3_dict['type'] = pcf3.type or ''
                pcf3_dict['serial_no'] = pcf3.serial_no or ''
                pcf3_dict['location'] = pcf3.location or ''
                pcf3_dict['id'] = pcf3.id
                pcf3_list.append(pcf3_dict)
            vals['pcf_equipment'] = pcf3_list
            vals['comments_complaints'] = work_order_obj.header or ''
            all_aircon = self.env['product.type'].search([])
            air_list = []
            for air in all_aircon:
                air_list.append(air.name)

            all_fan = self.env['type.of.fan'].search([])
            fan_list = []
            for fan in all_fan:
                fan_list.append(fan.name)

            all_fan = self.env['type.of.fan'].search_read([], ['name'])
            vals['all_aircon'] = air_list
            vals['all_fan'] = fan_list
            pcf_service.append(vals)
        return pcf_service

    @api.multi
    def update_pcf_aircon_app(self, vals):
        workorder_obj = self.search([('id', '=', self.id)], limit=1)
        if workorder_obj:
            aircon_list = []
            if vals:
                aircon_obj = self.env['product.type'].search([('name', '=', vals.get('type_of_aircon', ''))],limit=1)
                aircon_dict = {}
                aircon_dict['type_of_aircon'] = aircon_obj.id if aircon_obj else ''
                aircon_dict['units_to_service'] = vals.get('units_to_service', '')
                aircon_dict['units_serviced'] = vals.get('units_serviced', '')
                aircon_dict['work_order_id'] = workorder_obj.id
                aircon_list.append((0, 0, aircon_dict))

            if workorder_obj and aircon_list:
                workorder_obj.pcf_service_chit_tree_1_ids = aircon_list
                return True
        else:
            return False

    @api.multi
    def update_pcf_fan_app(self, vals):
        workorder_obj = self.search([('id', '=', self.id)], limit=1)
        if workorder_obj:
            fan_list = []
            if vals:
                fan_obj = self.env['type.of.fan'].search([('name', '=', vals.get('type_of_fan', ''))], limit=1)
                fan_dict = {}
                fan_dict['type_of_fan'] = fan_obj.id if fan_obj else ''
                fan_dict['units_to_service'] = vals.get('units_to_service', '')
                fan_dict['units_serviced'] = vals.get('units_serviced', '')
                fan_dict['work_order_id'] = workorder_obj.id
                fan_list.append((0, 0, fan_dict))

            if workorder_obj and fan_list:
                workorder_obj.pcf_service_chit_tree_2_ids = fan_list
                return True
        else:
            return False

    @api.multi
    def update_pcf_equipment_app(self, vals):
        workorder_obj = self.search([('id', '=', self.id)], limit=1)
        pcf3_list =[]
        if workorder_obj and vals:
            pcf3_dict = {}
            pcf3_dict['brand'] = vals.get('brand',  '')
            pcf3_dict['model_no'] = vals.get('model_no', '')
            pcf3_dict['type'] = vals.get('type' ,'')
            pcf3_dict['serial_no'] = vals.get('serial_no' ,'')
            pcf3_dict['location'] = vals.get('location' , '')
            pcf3_dict['work_order_id'] = workorder_obj.id
            pcf3_list.append((0, 0, pcf3_dict))

            if workorder_obj and pcf3_list:
                workorder_obj.pcf_service_chit_tree_3_ids = pcf3_list
                return True
        else:
            return False

    @api.multi
    def update_comment_app(self, comments):
        wo_obj = self.search([('id', '=', self.id)])
        if wo_obj and comments:
            wo_obj.header = comments
            return True
        else:
            return False

    @api.multi
    def removed_aircon_app(self, air_id):
        wo_obj = self.search([('id', '=', self.id)])
        aircon_obj = self.env['booking.pcf.service.chit.tree.1'].search([('id', '=', air_id)])
        if wo_obj and aircon_obj:
            wo_obj.pcf_service_chit_tree_1_ids = [(2, aircon_obj.id)]
            return True
        else:
            return False

    @api.multi
    def removed_fan_app(self, fan_id):
        wo_obj = self.search([('id', '=', self.id)])
        fan_obj = self.env['booking.pcf.service.chit.tree.2'].search([('id', '=', fan_id)])
        if wo_obj and fan_obj:
            wo_obj.pcf_service_chit_tree_2_ids = [(2, fan_obj.id)]
            return True
        else:
            return False

    @api.multi
    def removed_equipment_app(self, equipment_id):
        wo_obj = self.search([('id', '=', self.id)])
        equipment_obj = self.env['booking.pcf.service.chit.tree.3'].search([('id', '=', equipment_id)])
        if wo_obj and equipment_obj:
            wo_obj.pcf_service_chit_tree_3_ids = [(2, equipment_obj.id)]
            return True
        else:
            return False

    @api.multi
    def removed_comment_app(self):
        wo_obj = self.search([('id', '=', self.id)])
        if wo_obj:
            wo_obj.header = ''
            return True
        else:
            return False

    @api.multi
    def get_kimhuat_service_chit_app(self):
        work_order_obj = self.search([('id','=',self.id)])
        if work_order_obj:
            # kimhuat service chit funds
            service_vals = {}
            service_vals['air_filter_cleaned'] = work_order_obj.air_filter_cleaned or False
            service_vals['bearings_oiled'] = work_order_obj.bearings_oiled or False
            service_vals['coils_cleaned'] = work_order_obj.coils_cleaned or False
            service_vals['condenser_coil_cleaned'] = work_order_obj.condenser_coil_cleaned or False
            service_vals['controls_checked'] = work_order_obj.controls_checked or False
            service_vals['discharged_pressure_checked'] = work_order_obj.discharged_pressure_checked or False
            service_vals['drain_tray_drain_pipe_cleaned'] = work_order_obj.drain_tray_drain_pipe_cleaned or False
            service_vals['drives_checked'] = work_order_obj.drives_checked or False
            service_vals['evaporator_coil'] = work_order_obj.evaporator_coil or False
            service_vals['fan_blower_cleaned'] = work_order_obj.fan_blower_cleaned or False
            service_vals['fan_coil_cover_cleaned'] = work_order_obj.fan_coil_cover_cleaned or False
            service_vals['flushed_drainage'] = work_order_obj.flushed_drainage or False
            service_vals['suction_pressure_checked'] = work_order_obj.suction_pressure_checked or False
            service_vals['thermostat_checked'] = work_order_obj.thermostat_checked or False
            service_vals['pumps_checked'] = work_order_obj.pumps_checked or False
            # notes tab
            service_vals['replacement'] = work_order_obj.replacement or ''
            service_vals['observations'] = work_order_obj.observations or ''
            service_vals['recommendation'] = work_order_obj.recommendation or ''
            service_vals['repair'] = work_order_obj.repair or ''
            service_vals['service_rendered'] = work_order_obj.service_rendered or ''
            # attachment
            service_vals['photo'] = work_order_obj.photo or ''
            service_vals['stamp'] = work_order_obj.stamp or ''
            # customer signature
            service_vals['signature'] = work_order_obj.signature or ''
            service_vals['signature_full_name'] = work_order_obj.signature_full_name or  ''
            service_vals['signature_date'] = work_order_obj.signature_date or  ''

            # service man signature
            service_vals['service_signature'] = work_order_obj.service_signature or ''
            service_vals['service_signature_full_name'] = work_order_obj.service_signature_full_name or ''
            service_vals['service_signature_date'] = work_order_obj.service_signature_date or ''

            # Payment
            service_vals['payment_mode'] = work_order_obj.payment_mode or ''
            service_vals['payment_made'] = work_order_obj.payment_made or ''
            return service_vals
        else:
            return False

stock_picking()
