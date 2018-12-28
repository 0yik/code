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
        team_lead_id = self.env['ir.model.data'].sudo().xmlid_to_res_id('booking_service_V2.group_teamleader')
        groups_ids = self.env.user.groups_id.ids
        if(team_lead_id in groups_ids):
            vals={}
            vals["user_state"] = "Team Leader"
            vals["name"] = self.env.user.name
            vals["email"] = self.env.user.email if self.env.user.email else ""
            vals["image_medium"] = self.env.user.image_medium if self.env.user.image_medium else ""
            vals["mobile"] = self.env.user.mobile if self.env.user.mobile else ""
            vals["partner_id"] = self.env.user.partner_id.id
            vals["show_notification"] = self.env.user.show_notification
            return vals
        else:
            team_worker_id = self.env['ir.model.data'].sudo().xmlid_to_res_id('booking_service_V2.group_worker')
            if (team_worker_id in groups_ids):
                vals = {}
                vals["user_state"] = "Team Worker"
                vals["name"] = self.env.user.name
                vals["email"] = self.env.user.email if self.env.user.email else ""
                vals["image_medium"] = self.env.user.image_medium if self.env.user.image_medium else ""
                vals["mobile"] = self.env.user.mobile if self.env.user.mobile else ""
                vals["partner_id"] = self.env.user.partner_id.id
                vals["show_notification"] = self.env.user.show_notification
                return vals
            else:
                vals = {}
                vals["user_state"] = "Only User"
                vals["name"] = self.env.user.name
                vals["email"] = self.env.user.email if self.env.user.email else ""
                vals["image_medium"] = self.env.user.image_medium if self.env.user.image_medium else ""
                vals["mobile"] = self.env.user.mobile if self.env.user.mobile else ""
                vals["partner_id"] = self.env.user.partner_id.id
                vals["show_notification"] = self.env.user.show_notification
                return vals

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
            # return users.id
        else:
            # return False
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
    def get_notification_data_app(self, user_id, worker_type):
        notification = []
        partner_id = self.env['res.users'].browse(user_id).partner_id
        notification_ids = []
        if self.env.user.show_notification :
            notification_ids = self.env['work.order.notification'].search([('team_employees_ids', 'in', partner_id.id)],order='id desc')
        else:
            notification_ids = self.env['work.order.notification'].search([('team_employees_ids', 'in', partner_id.id),('created_date','<=',self.env.user.notification_date)],order='id desc')

        for notification_obj in notification_ids:
            vals = {}
            vals['id'] = notification_obj.id
            vals['customer_name'] = notification_obj.customer_id.name if notification_obj.customer_id else ""
            vals['work_order_name'] = notification_obj.work_order_id.name if notification_obj.work_order_id else ""
            vals['booking_name'] = notification_obj.booking_name if notification_obj.booking_name else ""
            vals['work_location'] = notification_obj.work_location if notification_obj.work_location else ""
            vals['team_name'] = notification_obj.team_id.name if notification_obj.team_id else ""
            vals['team_leader_name'] = notification_obj.team_leader_id.name if notification_obj.team_leader_id else ""
            vals['state'] = notification_obj.state if notification_obj.state else ""
            vals['created_date'] = notification_obj.created_date if notification_obj.created_date else ""
            vals['reschedule_startdate'] = notification_obj.reschedule_startdate if notification_obj.reschedule_startdate else ""
            vals['reschedule_enddate'] = notification_obj.reschedule_enddate if notification_obj.reschedule_enddate else ""
            team_emp = []
            for emp in notification_obj.team_employees_ids:
                team_emp.append(emp.name)
            vals['team_employees'] = team_emp
            vals['subject'] = notification_obj.subject
            vals['remarks'] = notification_obj.remarks
            notification.append(vals)
        return notification

work_order_notification()

class stock_picking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def get_workorder_app(self,workorder_id):
        workorder_obj = self.search([('id','=',workorder_id)],order='id desc')
        if workorder_obj:
            workorder = {}
            workorder['work_order_id'] = workorder_obj.id
            workorder['work_order_name'] = workorder_obj.name
            workorder['booking_no'] = workorder_obj.origin if workorder_obj.origin else ""
            workorder['scheduled_start'] = workorder_obj.scheduled_start if workorder_obj.scheduled_start else ""
            workorder['scheduled_end'] = workorder_obj.scheduled_end if workorder_obj.scheduled_end else ""
            workorder['actual_start'] = workorder_obj.actual_start if workorder_obj.actual_start else ""
            workorder['actual_end'] = workorder_obj.actual_end if workorder_obj.actual_end else ""
            workorder['duration'] = workorder_obj.duration_app  # Types of service
            service_types = []
            for move_obj in workorder_obj.move_lines:
                service_types.append(move_obj.name)
            workorder["types_of_service"] = service_types
            workorder['work_location'] = workorder_obj.work_location if workorder_obj.work_location else ""
            workorder['customer_name']= workorder_obj.partner_id.name
            workorder['mobile_no']= workorder_obj.partner_id.mobile if workorder_obj.partner_id.mobile else ""
            state = ''
            if workorder_obj.state == 'pending':
                state = 'Pending'
            elif workorder_obj.state == 'assigned':
                state = 'Started'
            elif workorder_obj.state == 'done':
                state = 'Completed'
            elif workorder_obj.state == 'cancel':
                state = 'Cancelled'
            workorder['status'] =  state
            workorder['vehicle_no'] = workorder_obj.vehicle_new_id.name if workorder_obj.vehicle_new_id else ""
            workorder['team_name'] = workorder_obj.team.name if workorder_obj.team else ""
            workorder['team_leader'] = workorder_obj.team_leader.name if workorder_obj.team_leader else ""
            team_workers = []
            for team_worker_obj in workorder_obj.team_employees:
                team_workers.append(team_worker_obj.employee_id.name)
            workorder['workers'] = team_workers
            workorder['remarks'] = workorder_obj.remarks if workorder_obj.remarks else ""
        return workorder

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
            record.actual_start = fields.Datetime.now()
            if record.state == 'pending':
                partners = self.get_partners(record)
                vals = {}
                partner_name = ''
                try:
                    partner_name = record.partner_id.name.encode('utf-8')
                except:
                    partner_name = record.partner_id.name
                if record.work_location:
                    work_location = ''
                    try:
                        work_location = record.work_location.encode('utf-8')
                    except:
                        work_location = record.work_location
                    subject = 'Your work order '+str(record.name)+' with '+str(partner_name or '')+','+ str(work_location)\
                              +' scheduled on ('+str(record.scheduled_start)+') has been started.Thank You.'
                else:
                    subject = 'Your work order '+str(record.name)+' with '+str(partner_name or '')\
                              +' scheduled on ('+str(record.scheduled_start) + ') has been started.Thank You.'
                vals['work_order_id'] = record.id
                vals['customer_id'] = record.partner_id.id if record.partner_id else False
                vals['booking_name'] = record.origin if record.origin else ''
                vals['work_location'] = record.work_location if record.work_location else ''
                vals['team_id'] = record.team.id if record.team else False
                vals['team_leader_id'] = record.team_leader.id if record.team_leader else False
                vals['team_employees_ids'] = [(6, 0, partners.ids)]
                vals['subject'] = subject
                vals['remarks'] = record.remarks if record.remarks else ''
                vals['state'] = 'Started'
                vals['created_date'] = fields.Datetime.now()
                record.env['work.order.notification'].create(vals)
                record.state = 'assigned'

    # end function  for erp side
    @api.multi
    def action_validate(self):
        res = super(stock_picking,self).action_validate()
        for wo_obj in self:
            record = self.search([('id','=',wo_obj.id)],order='id desc')
            partners = self.get_partners(record)
            vals = {}
            partner_name = ''
            try:
                partner_name = record.partner_id.name.encode('utf-8')
            except:
                partner_name = record.partner_id.name
            if record.work_location:
                work_location = ''
                try:
                    work_location = record.work_location.encode('utf-8')
                except:
                    work_location = record.work_location

                subject = 'Your work order ' + str(record.name) + ' with ' + str(partner_name or '') + ', ' \
                          + str(work_location) +' scheduled on (' + str(record.scheduled_start) + ') has been completed successfully. Thank You.'
            else:
                subject = 'Your work order ' + str(record.name) + ' with ' + str(partner_name or '') + ' scheduled on (' + str(record.scheduled_start) \
                          + ') has been completed successfully. Thank You.'
            vals['customer_id'] = record.partner_id.id if record.partner_id else False
            vals['work_order_id'] = record.id
            vals['booking_name'] = record.origin if record.origin else ''
            vals['work_location'] = record.work_location if record.work_location else ''
            vals['team_id'] = record.team.id if record.team else False
            vals['team_leader_id'] = record.team_leader.id if record.team_leader else False
            vals['team_employees_ids'] = [(6, 0, partners.ids)]
            vals['subject'] = subject
            vals['remarks'] = record.remarks if record.remarks else ''
            vals['state'] = 'Completed'
            vals['created_date'] = fields.Datetime.now()
            record.env['work.order.notification'].create(vals)

        return res

    @api.multi
    def get_work_orders(self, user_id, worker_type, get_state):
        work_orders = []
        employee_id = self.env['hr.employee'].search([('user_id', '=', user_id)], limit=1).ids
        if not employee_id:
            employee_id = self.env['hr.employee'].search([('resource_id.user_id', '=', user_id)], limit=1).ids
        work_order_ids = []
        if (worker_type == "team_lead"):
            work_order_ids = self.env['stock.picking'].search([('team_leader', 'in', employee_id), ("state", "=", get_state)],order='id desc')
        else:
            work_order_employee_ids = self.env['working.order.employee'].search([('employee_id', 'in', employee_id)])
            for temp_obj in work_order_employee_ids:
                if temp_obj.order_id.state == get_state:
                    work_order_ids.append(temp_obj.order_id)
        for work_order_obj in work_order_ids:
            vals = {}
            vals['work_order_id'] = work_order_obj.id
            vals['work_order_name'] = work_order_obj.name
            vals['booking_no'] = work_order_obj.origin if work_order_obj.origin else ""
            vals['scheduled_start'] = work_order_obj.scheduled_start if work_order_obj.scheduled_start else ""
            vals['scheduled_end'] = work_order_obj.scheduled_end if work_order_obj.scheduled_end else ""
            vals['actual_start'] = work_order_obj.actual_start if work_order_obj.actual_start else ""
            vals['actual_end'] = work_order_obj.actual_end if work_order_obj.actual_end else ""
            vals['duration'] = work_order_obj.duration_app  # Types of service
            service_types = []
            for move_obj in work_order_obj.move_lines:
                service_types.append(move_obj.name)
            vals["types_of_service"] = service_types
            vals['work_location'] = work_order_obj.work_location if work_order_obj.work_location else ""
            vals['customer_name']= work_order_obj.partner_id.name
            vals['mobile_no']= work_order_obj.partner_id.mobile if work_order_obj.partner_id.mobile else ""
            state = ''
            if work_order_obj.state == 'pending':
                state = 'Pending'
            elif work_order_obj.state == 'assigned':
                state = 'Started'
            elif work_order_obj.state == 'done':
                state = 'Completed'
            elif work_order_obj.state == 'cancel':
                state = 'Cancelled'
            vals['status'] = state
            vals['vehicle_no'] = work_order_obj.vehicle_new_id.name if work_order_obj.vehicle_new_id else ""
            vals['team_name'] = work_order_obj.team.name if work_order_obj.team else ""
            vals['team_leader'] = work_order_obj.team_leader.name if work_order_obj.team_leader else ""
            team_workers = []
            for team_worker_obj in work_order_obj.team_employees:
                team_workers.append(team_worker_obj.employee_id.name)
            vals['workers'] = team_workers
            vals['remarks'] = work_order_obj.remarks if work_order_obj.remarks else ""
            work_orders.append(vals)
        return work_orders

    @api.multi
    def get_equipment_data_app(self, work_order_id):
        equipment_list = []
        #for record in self.env['stock.picking'].browse(work_order_id).equip_ids:
        for book_line_obj in self.env['stock.picking'].browse(work_order_id).equip_ids:
            #book_line_obj = self.search([('id','=',record.id)],order='id desc')
            tmp_vals = {}
            tmp_vals["id"] = book_line_obj.id
            tmp_vals["image"] = book_line_obj.equipment_id.image_medium if book_line_obj.equipment_id.image_medium else ""
            tmp_vals["checked"] = book_line_obj.checked
            tmp_vals["name"] = book_line_obj.equipment_id.name
            equipment_list.append(tmp_vals)
        return equipment_list

    @api.multi
    def get_dashboard_notification_counts(self, user_id, worker_type):
        vals={}
        date_today = fields.Datetime.from_string(fields.Datetime.now())
        from_date = (date_today + datetime.timedelta(days=1)).replace( hour=00, minute=00, second=01)
        to_date = (date_today + datetime.timedelta(days=1)).replace( hour=23, minute=59, second=59)
        employee_id = self.env['hr.employee'].search([('user_id', '=', user_id)], limit=1).ids
        if not employee_id:
            employee_id = self.env['hr.employee'].search([('resource_id.user_id', '=', user_id)], limit=1).ids
        work_order_ids = []
        if (worker_type == "team_lead"):
            pending_work_order_ids = self.env['stock.picking'].search([('team_leader', 'in', employee_id), ("state", "=", "pending")],order='id desc')
            vals["pending_work_order_count"] = len(pending_work_order_ids)
            # Completed Work Order Count
            completed_work_order_ids = self.env['stock.picking'].search([('team_leader', 'in', employee_id), ("state", "=", "done")],order='id desc')
            vals["completed_work_order_count"] = len(completed_work_order_ids)
            # Reminders Count
            reminder_order_ids = self.env['stock.picking'].search([('team_leader', 'in', employee_id), ('scheduled_start', '>=', fields.Datetime.to_string(from_date)),('scheduled_start', '<=', fields.Datetime.to_string(to_date))],order='id desc')
            vals["reminders_work_order_count"] = len(reminder_order_ids)
            # Notification Count
            notification_ids = []
            if self.env.user.show_notification:
                notification_ids = self.env['work.order.notification'].search([('team_leader_id', 'in', employee_id)])
            else:
                notification_ids = self.env['work.order.notification'].search([('team_leader_id', 'in', employee_id),('created_date', '<=', self.env.user.notification_date)])
            vals["notification_count"] = len(notification_ids)
            return vals

        else:
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

stock_picking()
