
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta, time, date
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_TIME_FORMAT


class project_booking(models.Model):
    
    _inherit = 'project.booking'
    
    notification_ids = fields.One2many('notification.notification', 'booking_id', string='Notifications')
    
    
    def _send_notification_on_reject_by_tester(self, self_obj, rejected_obj):
        user_ids = [self.user_tester_id.id, rejected_obj.user_tester_id.id]
        tester_template = self.env.ref('hilti_modifier_booking_notification.mail_template_for_reject_swap_by_tester')
        tester_template.send_mail(self.id, force_send=True)
        
        notification_message = 'Taster has rejected swap for booking ' + self.booking_no + '.'

        self.env['notification.notification'].create({
            'name': notification_message,
            'booking_id': self.id,
            'user_ids': [[6, 0, user_ids]]
        })
        #TODO by mustafa
        # in this case just notifiy tester of another tester
        return True
    
    def _send_notification_on_accept_by_tester(self, booking_to_obj, booking_from_obj):
        user_ids = [booking_to_obj.user_tester_id.id, booking_from_obj.user_tester_id.id]
        tester_template = self.env.ref('hilti_modifier_booking_notification.mail_template_for_accept_swap_by_tester')
        tester_template.send_mail(self.id, force_send=True)
        
        notification_message = 'Taster has Accepted swap for booking ' + self.booking_no + '.'

        self.env['notification.notification'].create({
            'name': notification_message,
            'booking_id': self.id,
            'user_ids': [[6, 0, user_ids]]
        })
        #TODO by mustafa
        # in this case notify both customer and tester
        # Pls ask Valli for msg format
        return True
    
    
    
    @api.multi
    def add_delay(self, delay_time, delay_remark):
        delay_time_configured = self.env['ir.values'].get_default('admin.configuration', 'delay_time')
        booking_before_time = self.env['ir.values'].get_default('admin.configuration', 'booking_before_time')
        for pr_book in self:
            import datetime
            now = datetime.datetime.today()
            now = str(now).split('.')[0]
            total_needed = datetime.datetime.strptime(str(pr_book.final_end_dtime), "%Y-%m-%d %H:%M:%S") - datetime.datetime.strptime(str(pr_book.final_start_dtime), "%Y-%m-%d %H:%M:%S")
            total_tested = datetime.datetime.strptime(str(now), "%Y-%m-%d %H:%M:%S") - datetime.datetime.strptime(str(pr_book.testing_start_time), "%Y-%m-%d %H:%M:%S")
            total_hm = abs(total_needed)
            total_hm1 = abs(total_tested)
            total_tested_minutes = int(total_hm1.total_seconds()/60)
            total_needed_minutes = int(total_hm.total_seconds()/60)
            final_diff = int(total_hm.total_seconds()/60) - int(total_hm1.total_seconds()/60)
            if delay_time_configured < final_diff:
                raise UserError(_("Delay button can be clicked only before %s mins of booking end time. Please try again later during that time. Thank You.") % delay_time_configured)
            else:
                pr_book.delay_time = delay_time
                pr_book.delay_remark = delay_remark
            total_check_time = float(booking_before_time) + float(delay_time)
            start_time = "%02d:%02d" % (int(total_check_time), (total_check_time*60) % 60)
            check_dt_end = datetime.datetime.strptime(pr_book.final_end_dtime, "%Y-%m-%d %H:%M:%S")
            total_check_en_time = check_dt_end + timedelta(hours=int(start_time.split(':')[0]), minutes=int(start_time.split(':')[1]))
            count = 0
            for book in self.env['project.booking'].search([('tester_id', '=', pr_book.tester_id and pr_book.tester_id.id)]):
                if str(check_dt_end) <= book.final_start_dtime <= str(total_check_en_time):
                    count = 1
                    raise UserError(_("You have your next booking %s on %s.Hence, you cannot proceed further on this delayed booking. Please click on the Book for Delay button to make a new booking for the delay. Thank You.") % (book.booking_no, book.final_start_dtime))
            pr_book.send_booking_delay_notification()
        return True
        
        
    
    @api.multi
    def unlink(self):
        for rec in self:
            rec.notification_ids.unlink()
        return super(project_booking, self).unlink()

    def send_notification(self, customer_template, tester_template, admin_template, notification_message):

        user_ids = []
        # Sending mail to customer
        if self.user_id.id:
            user_ids.append(self.user_id.id)
        customer_template.send_mail(self.id, force_send=True)

        # Sending mail to Account Manager

        if self.user_id.account_manager_id:
            manager_user = self.env['res.users'].search([('partner_id', '=', self.user_id.account_manager_id.id)])
            if manager_user:
                user_ids.append(manager_user.id)
            if self.user_id.receive_notifications:
                admin_template.with_context(user_email=self.user_id.account_manager_id.id).send_mail(self.id, force_send=True)
        if self.tester_id:
            user_ids.append(self.user_tester_id.id)
            tester_template.send_mail(self.id, force_send=True)
        
        # Sending mail to Admin
              
        admins = self.env.ref('hilti_modifier_accessrights.group_hilti_admin')
        for admin in admins.users:
            user_ids.append(admin.id)
            admin_template.with_context(user_email=admin.partner_id.id).send_mail(self.id, force_send=True)
#              
        self.env['notification.notification'].create({
            'name': notification_message,
            'booking_id': self.id,
#             'ref_number': self.booking_no,
            'user_ids': [[6, 0, user_ids]]
        })
        return True

    def send_confirmation_notification(self):
        customer_template = self.env.ref('hilti_modifier_booking_notification.mail_template_booking_details_customer')
        tester_template = self.env.ref('hilti_modifier_booking_notification.mail_template_booking_details_tester')
        admin_template = self.env.ref('hilti_modifier_booking_notification.mail_template_booking_details_admin')
        notification_message = 'A booking referenced as ' + self.booking_no + ' has been confirmed.'
        self.send_notification(customer_template, tester_template, admin_template, notification_message)
        return True
    
    def send_booking_reschedule_notification(self):
        customer_template = self.env.ref('hilti_modifier_booking_notification.mail_template_booking_reschedule_customer')
        tester_template = self.env.ref('hilti_modifier_booking_notification.mail_template_booking_reschedule_tester')
        admin_template = self.env.ref('hilti_modifier_booking_notification.mail_template_booking_reschedule_admin')
        notification_message = 'A booking referenced as ' + self.booking_no + ' has been Rescheduled.'
        self.send_notification(customer_template, tester_template, admin_template, notification_message)
        return True
    
    def send_booking_cancel_notification(self):
        customer_template = self.env.ref('hilti_modifier_booking_notification.mail_template_booking_cancel_customer')
        tester_template = self.env.ref('hilti_modifier_booking_notification.mail_template_booking_cancel_tester')
        admin_template = self.env.ref('hilti_modifier_booking_notification.mail_template_booking_cancel_admin')
        notification_message = 'A booking referenced as ' + self.booking_no + ' has been Cancel.'
        self.send_notification(customer_template, tester_template, admin_template, notification_message)
        return True
    
    def send_booking_delay_notification(self):
        customer_template = self.env.ref('hilti_modifier_booking_notification.mail_template_booking_delay_customer')
        tester_template = self.env.ref('hilti_modifier_booking_notification.mail_template_booking_delay_tester')
        admin_template = self.env.ref('hilti_modifier_booking_notification.mail_template_booking_delay_admin')
        notification_message = 'A booking referenced as ' + self.booking_no + ' has been Delayed.'
        self.send_notification(customer_template, tester_template, admin_template, notification_message)
        return True
    
    def send_booking_reconfirmation_notification(self):
        customer_template = self.env.ref('hilti_modifier_booking_notification.mail_template_booking_reconfirmation_customer')
        tester_template = self.env.ref('hilti_modifier_booking_notification.mail_template_booking_reconfirmation_tester')
        admin_template = self.env.ref('hilti_modifier_booking_notification.mail_template_booking_reconfirmation_admin')
        notification_message = 'A booking referenced as ' + self.booking_no + ' has been Reconfirmed.'
        self.send_notification(customer_template, tester_template, admin_template, notification_message)
        return True
    
    def send_booking_reminder_reconfirmation(self):
        customer_template = self.env.ref('hilti_modifier_booking_notification.mail_template_booking_reminder_reconfirmation_customer')
        tester_template = self.env.ref('hilti_modifier_booking_notification.mail_template_booking_reminder_reconfirmation_tester')
        admin_template = self.env.ref('hilti_modifier_booking_notification.mail_template_booking_reminder_reconfirmation_admin')
        notification_message = 'Please re-confirm booking referenced as ' + self.booking_no + '.'
        self.send_notification(customer_template, tester_template, admin_template, notification_message)
        return True
    
    @api.model
    def reconfirm_booking_reminder(self):
        bookings = self.search([('is_final', '=', True), ('status', '=', 'pending')])
        reminder_sent_before_hours = self.env['ir.values'].get_default('admin.configuration', 'reminder_sent_before_hours')
        for booking in bookings:
            if booking.final_start_dtime and booking.final_end_dtime:
                date_diff = datetime.strptime(booking.final_start_dtime, DEFAULT_SERVER_DATETIME_FORMAT) - datetime.now()
                days, seconds = date_diff.days, date_diff.seconds
                hours = days * 24 + seconds // 3600
                if hours == reminder_sent_before_hours:
                    booking.send_booking_reminder_reconfirmation()
        return True
    
    @api.model
    def send_notification_for_dedicated_bookings(self):
        bookings = self.search([('add_accept_button', '=', True), ('status', '!=', 'cancelled')])
        hours_before_send_notification_for_dedicated_bookings = self.env['ir.values'].get_default('admin.configuration', 'hours_before_send_notification_for_dedicated_bookings')
        for booking in bookings:
            if booking.final_start_dtime and booking.final_end_dtime:
                date_diff = datetime.strptime(booking.final_start_dtime, DEFAULT_SERVER_DATETIME_FORMAT) - datetime.now()
                days, seconds = date_diff.days, date_diff.seconds
                hours = days * 24 + seconds // 3600
                if hours == hours_before_send_notification_for_dedicated_bookings:
                    customer_template = self.env.ref('hilti_modifier_booking_notification.mail_template_for_dedicated_booking_customer')
                    customer_template.send_mail(booking.id, force_send=True)
                    booking.add_accept_button = False
        return True
    
    
    @api.multi
    def accept_dedicated_booking(self):
        for rec in self:
            rec.write({
                'user_tester_id': self.env.user.id,
                'add_accept_button': False,
                'is_final': True
            })
            tester_template = self.env.ref('hilti_modifier_booking_notification.mail_template_for_dedicated_support_booking_accept_tester')
            user_ids = []
            for tester in self.env.ref('hilti_modifier_accessrights.group_hilti_tester').users:
                if tester.id != self.env.user.id:
                    user_ids.append(tester.id)
                    tester_template.with_context(user_email=tester.partner_id.id).send_mail(rec.id, force_send=True)
            self.env['notification.notification'].create({
                'name': "The task with booking no" + rec.booking_no + " has been accepted by tester.",
                'booking_id': rec.id,
                'user_ids': [[6, 0, user_ids]]
            })
        return True
    
    @api.model
    def create(self, vals):
        result = super(project_booking, self).create(vals)
        if self._context and 'send_remark_to_cust' in self._context:
            customer_template = self.env.ref('hilti_modifier_booking_notification.mail_template_booking_delayed_customer_booking')
            customer_template.with_context(user_email=result.partner_id.id, delayed_massage = result.delayed_remarks_cust).send_mail(result.id, force_send=True)
            admins = self.env.ref('hilti_modifier_accessrights.group_hilti_admin')
            user_ids = []
            user_ids.append(result.user_id.id)
            user_ids.append(result.user_tester_id.id)
            for admin in admins.users:
                user_ids.append(admin.id)
            self.env['notification.notification'].create({
                    'name': 'Delayed booking has been created due to  ' + result.delayed_remarks_cust + ' .',
                    'booking_id': result.id,
                    'user_ids': [[6, 0, user_ids]],
                })
        if self._context and 'send_notification_to_testers' in self._context:
            tester_template = self.env.ref('hilti_modifier_booking_notification.mail_template_for_dedicated_support_booking_tester')
            user_ids = []
            for tester in self.env.ref('hilti_modifier_accessrights.group_hilti_tester').users:
                user_ids.append(tester.id)
                tester_template.with_context(user_email=tester.partner_id.id).send_mail(result.id, force_send=True)
            self.env['notification.notification'].create({
                'name': "A new dedicated support is received",
                'booking_id': result.id,
                'user_ids': [[6, 0, user_ids]]
            })
            customer_template = self.env.ref('hilti_modifier_booking_notification.mail_template_for_dedicated_support_booking_customer')
            customer_template.send_mail(result.id, force_send=True)
            self.env['notification.notification'].create({
                'name': "Your booking is awaiting confirmation from the testers and once a tester is available, you will be notified on the booking confirmation soon.",
                'booking_id': result.id,
                'user_ids': [[6, 0, [result.user_id.id]]]
            })
        if result.is_final:
            result.send_confirmation_notification()
        return result
    
    @api.multi
    def write(self, vals):
        res = super(project_booking, self).write(vals)
        if vals.get('is_final'):
            for rec in self:
                rec.send_confirmation_notification()
        send_notification_on_cancel = self.env['ir.values'].get_default('admin.configuration', 'send_notification_on_cancel')
        if send_notification_on_cancel and vals.get('status') == 'cancelled':
            for rec in self:
                rec.send_booking_cancel_notification()
        if vals.get('status') == 'reconfirmed':
            for rec in self:
                rec.send_booking_reconfirmation_notification()
        return res
    
    @api.multi
    def cancel_booking_from_reminder(self):
        self.is_cancel_from_tester = True
        self.status = 'cancelled'
        return True
    
    @api.multi
    def tester_reminder(self):
        total_reminder = self.env['ir.values'].get_default('admin.configuration', 'total_reminder')
        reminder_duration = self.env['ir.values'].get_default('admin.configuration', 'reminder_duration')
        send = False
        if not total_reminder > self.reminder_count:
            raise UserError(_("Reminder button to be clickable %s times.") % total_reminder)
        if not self.reminder_time:
            send = True
        else:
            now = datetime.today()
            now = str(now).split('.')[0]
            diff = datetime.strptime(str(now), "%Y-%m-%d %H:%M:%S") - datetime.strptime(self.reminder_time, "%Y-%m-%d %H:%M:%S")
            total_hm = abs(diff)
            minutes = int(total_hm.total_seconds() / 60)
            if minutes >= reminder_duration:
                send = True
            else:
                raise UserError(_("Next reminder to Customer can be sent only after %s minutes. Please wait and try after some time.") % reminder_duration)
                send = False
        if total_reminder > self.reminder_count and send == True:
            self.reminder_count = self.reminder_count + 1
            all_partner = []
            if self.reminder_count == total_reminder:
                self.show_cancel_button = True
            all_partner_id = []
            user_ids = [self.user_id.id]
            all_partner.append(self.partner_id)
            all_partner_id.append(self.partner_id.id)
            if self.partner_id.account_manager_id and self.partner_id.account_manager_id:
                account_manager_user = self.env['res.users'].search([('partner_id', '=', self.partner_id.account_manager_id.id)])
                if account_manager_user:
                    user_ids.append(account_manager_user.id)
                all_partner.append(self.partner_id.account_manager_id)
                all_partner_id.append(self.partner_id.account_manager_id.id)
            for a in all_partner:
                self.reminder_time = datetime.now()
                ctx = dict(self._context or {})
                ctx['partner_email'] = a.id
                template = self.env.ref('hilti_modifier_booking_notification.email_template_for_reminder_id')
                template.with_context(ctx).send_mail(self.id, force_send=True)
            self.env['notification.notification'].create({
                'name': 'Tester is waiting for booking referenced as ' + self.booking_no + ' for testing.',
                'booking_id': self.id,
#                 'ref_number': self.booking_no,
                'user_ids': [[6, 0, user_ids]]
            })
            self.reminder_history = [(0, 0,
                                         {'reminder_count': self.reminder_count,
                                          'reminder_time': self.reminder_time,
                                          'partner_ids': [(6, 0, all_partner_id)]})]
            if self.reminder_count == total_reminder:
                self._cr.commit()
                raise UserError(_("You can cancel this booking now as the customer is not responding to your reminders."))
        return {'total_reminder': total_reminder, 'reminder_count': self.reminder_count, 'reminder_duration': reminder_duration}
    
    
class project_project(models.Model):
    _inherit = 'project.project'
    
    def approve_project(self):
        self.status = 'approved'
        if self.user_id and self.user_id.id and self.user_id.partner_id and self.user_id.partner_id.id: 
            customer_template = self.env.ref('hilti_modifier_company.mail_template_approvel_project_to_customer')
            customer_template.with_context(customer_email=self.user_id.partner_id.id).send_mail(self.id, force_send=True)
        
    @api.model
    def create(self, vals):
        res = super(project_project, self).create(vals)
        if self._context and 'created_from_user' in self._context:
            user_ids = []
            res.status = 'draft'
            admin_template = self.env.ref('hilti_modifier_company.mail_template_approvel_project')
            admins = self.env.ref('hilti_modifier_accessrights.group_hilti_admin')
            for admin in admins.users:
                user_ids.append(admin.id)
                admin_template.with_context(admin_email=admin.partner_id.id).send_mail(res.id, force_send=True)
            notification_message = 'A project has been sent to admin for approve which is referenced as ' + res.name + '.'
            self.env['notification.notification'].create({
                    'name': notification_message,
                    'project_id': res.id,
                    'user_ids': [[6, 0, user_ids]],
                })
        else:
            res.status = 'approved'
        return res
    