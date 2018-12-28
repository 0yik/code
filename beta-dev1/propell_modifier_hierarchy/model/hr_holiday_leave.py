from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError, UserError

HOURS_PER_DAY = 8

class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    state = fields.Selection([('draft', 'New'), ('confirm', 'Waiting for SIC/Manager approval'),
                              ('emp_approval', 'Waiting for Employee approval'),
                              ('tic_approval', 'Waiting for TIC/OIC approval'),
                              ('hod_approval', 'Waiting for HOD approval'),
                              ('gm_approval', 'Waiting for GM approval'),
                              ('ed_approval', 'Waiting for ED approval'),
                              ('md_approval', 'Waiting for MD approval'),
                              ('next_approval', 'Waiting for Next Manager approval'),
                              ('refuse', 'Refused'), ('validate1', 'Waiting Final Approval'),
                              ('validate', 'Approved'), ('cancel', 'Cancelled')],
        'State', readonly=True, help='The state is set to \'Draft\', when a holiday request is created.\
        \nThe state is \'Waiting Approval\', when holiday request is confirmed by user.\
        \nThe state is \'Refused\', when holiday request is refused by manager.\
        \nThe state is \'Approved\', when holiday request is approved by manager.', track_visibility='onchange')
    no_approval = fields.Integer("No of Approval")

    def approve_emp(self):
        if self.type == 'remove':
            self.set_status(self)
            if self.state != 'validate':
                self.notify_email_manager()
            #calculate no of approval
            self.no_approval = self.no_approval + 1

        return

    def approve_sic(self):
        if self.type == 'remove':
            self.set_status(self)
            if self.state != 'validate':
                self.notify_email_manager()
            #calculate no of approval
            self.no_approval = self.no_approval + 1

        return

    def approve_tic(self):
        if self.type == 'remove':
            self.set_status(self)
            if self.state != 'validate':
                self.notify_email_manager()
            #calculate no of approval
            self.no_approval = self.no_approval + 1

        return

    def approve_hod(self):
        if self.type == 'remove':
            self.set_status(self)
            if self.state != 'validate':
                self.notify_email_manager()
            #calculate no of approval
            self.no_approval = self.no_approval + 1

        return

    def approve_gm(self):
        if self.type == 'remove':
            self.set_status(self)
            if self.state != 'validate':
                self.notify_email_manager()
            #calculate no of approval
            self.no_approval = self.no_approval + 1

        return

    def approve_ed(self):
        if self.type == 'remove':
            self.set_status(self)
            if self.state != 'validate':
                self.notify_email_manager()
            #calculate no of approval
            self.no_approval = self.no_approval + 1

        return

    def approve_md(self):
        if self.type == 'remove':
            self.set_status(self)
            if self.state != 'validate':
                self.notify_email_manager()
            #calculate no of approval
            self.no_approval = self.no_approval + 1

#         self.action_approve()
#         self.notify_email_employee('Leave Approved')
        return

    def set_status(self, res):
        if res.employee_id.hierarchy_id:
            emp_id = self.env.ref('propell_modifier_hierarchy.group_leave_employee')
            eng_id = self.env.ref('propell_modifier_hierarchy.group_leave_engineer')
            super_id = self.env.ref('propell_modifier_hierarchy.group_leave_supervisor')
            worker_id = self.env.ref('propell_modifier_hierarchy.group_leave_worker')
            site_mgr_id = self.env.ref('propell_modifier_hierarchy.group_leave_sic')
            assis_hod_id = self.env.ref('propell_modifier_hierarchy.group_leave_tic')
            hod_id = self.env.ref('propell_modifier_hierarchy.group_leave_hod')
            gm_id = self.env.ref('propell_modifier_hierarchy.group_leave_gm')
            ed_id = self.env.ref('propell_modifier_hierarchy.group_leave_ed')
            md_id = self.env.ref('propell_modifier_hierarchy.group_leave_md')

            hierarchy_lines = self.env['leave.approve.line'].search([('hierarchy_id', '=', res.employee_id.hierarchy_id.id)], order="sequence")

            #approve leave if no of approval is same with hierarchy
            if res.no_approval == (res.employee_id.hierarchy_id.no_approval):
                res.action_approve()
                res.notify_email_employee('Leave Approved')
                return True

            if not self.env.user.leave_group_rights_id.id:
                raise ValidationError(_("Warning \n  The Leave Group Is Not Set For  This Employee. "))
                    

            if res.state in ['draft', 'confirm']:
                i = 0
                for hierarchy_line in hierarchy_lines:
                    i = i + 1
                    #if self._uid in hierarchy_line.groups.users.ids:
                    if self.env.user.leave_group_rights_id in hierarchy_line.groups:
                        print "break"
                        break
                if i == 0:
                    i = 1

                if len(hierarchy_lines) <= 2:
                    res.action_approve()
                    res.notify_email_employee('Leave Approved')
                    return True
               
                if len(hierarchy_lines) == i:
                    # g_eng = self.env['res.users'].browse(self.env.uid).has_group('propell_modifier_hierarchy.group_leave_engineer')
                    # g_emp = self.env['res.users'].browse(self.env.uid).has_group('propell_modifier_hierarchy.group_leave_employee')
                    # g_super = self.env['res.users'].browse(self.env.uid).has_group('propell_modifier_hierarchy.group_leave_supervisor')
                    # g_worker = self.env['res.users'].browse(self.env.uid).has_group('propell_modifier_hierarchy.group_leave_worker')
                    # if g_eng or g_emp or g_super or g_worker:
                    #     i= 0
                    # else:
                    #     raise ValidationError(_("Warning \n  This employee group not configure Leave Approval Hierarchy "))
                    e_groups = []
                    hierarchys = res.employee_id.hierarchy_id.hierarchy_line_ids
                    for hierarchy in hierarchys:
                        e_groups.append(hierarchy.groups.id)
                    if self.env['res.users'].browse(self.env.uid).leave_group_rights_id:
                        user_group = self.env['res.users'].browse(self.env.uid).leave_group_rights_id.id
                    if user_group not in e_groups:
                        i = 0

                if hierarchy_lines[i]:
                    if emp_id == hierarchy_lines[i].groups:
                        res.state = 'emp_approval'
                    if site_mgr_id == hierarchy_lines[i].groups:                      
                        res.state = 'confirm'
                    if assis_hod_id == hierarchy_lines[i].groups:
                        res.state = 'tic_approval'
                    if hod_id == hierarchy_lines[i].groups:
                        res.state = 'hod_approval'
                    if gm_id == hierarchy_lines[i].groups:
                        res.state = 'gm_approval'
                    if ed_id == hierarchy_lines[i].groups:
                        res.state = 'ed_approval'
                    if md_id == hierarchy_lines[i].groups:
                        res.state = 'md_approval'

                #calculate no of approval
                res.no_approval = res.no_approval + 1
                return
            if res.state in ['emp_approval', 'sic_approval', 'tic_approval', 'hod_approval', 'gm_approval', 'ed_approval', 'md_approval']:
                if res.state == 'emp_approval':
                    flag = False
                    for hierarchy_line in hierarchy_lines:
                        if flag:
                            if emp_id == hierarchy_line.groups:
                                res.state = 'emp_approval'
                            if site_mgr_id == hierarchy_line.groups:
                                res.state = 'sic_approval'
                            if assis_hod_id == hierarchy_line.groups:
                                res.state = 'tic_approval'
                            if hod_id == hierarchy_line.groups:
                                res.state = 'hod_approval'
                            if gm_id == hierarchy_line.groups:
                                res.state = 'gm_approval'
                            if ed_id == hierarchy_line.groups:
                                res.state = 'ed_approval'
                            if md_id == hierarchy_line.groups:
                                res.state = 'md_approval'
                            return
                        if emp_id == hierarchy_line.groups:
                            flag = True
                            if hierarchy_line == hierarchy_lines[-1]:
                                res.action_approve()
                                res.notify_email_employee('Leave Approved')
                                return True

                if res.state == 'sic_approval':
                    flag = False
                    for hierarchy_line in hierarchy_lines:
                        if flag:
                            if emp_id == hierarchy_line.groups:
                                res.state = 'emp_approval'
                            if site_mgr_id == hierarchy_line.groups:
                                res.state = 'sic_approval'
                            if assis_hod_id == hierarchy_line.groups:
                                res.state = 'tic_approval'
                            if hod_id == hierarchy_line.groups:
                                res.state = 'hod_approval'
                            if gm_id == hierarchy_line.groups:
                                res.state = 'gm_approval'
                            if ed_id == hierarchy_line.groups:
                                res.state = 'ed_approval'
                            if md_id == hierarchy_line.groups:
                                res.state = 'md_approval'
                            return
                        if site_mgr_id == hierarchy_line.groups:
                            flag = True
                            if hierarchy_line == hierarchy_lines[-1]:
                                res.action_approve()
                                res.notify_email_employee('Leave Approved')
                                return True

                if res.state == 'tic_approval':
                    flag = False
                    for hierarchy_line in hierarchy_lines:
                        if flag:
                            if emp_id == hierarchy_line.groups:
                                res.state = 'emp_approval'
                            if site_mgr_id == hierarchy_line.groups:
                                res.state = 'sic_approval'
                            if assis_hod_id == hierarchy_line.groups:
                                res.state = 'tic_approval'
                            if hod_id == hierarchy_line.groups:
                                res.state = 'hod_approval'
                            if gm_id == hierarchy_line.groups:
                                res.state = 'gm_approval'
                            if ed_id == hierarchy_line.groups:
                                res.state = 'ed_approval'
                            if md_id == hierarchy_line.groups:
                                res.state = 'md_approval'
                            return
                        if assis_hod_id == hierarchy_line.groups:
                            flag = True
                            if hierarchy_line == hierarchy_lines[-1]:
                                res.action_approve()
                                res.notify_email_employee('Leave Approved')
                                return True

                if res.state == 'hod_approval':
                    flag = False
                    for hierarchy_line in hierarchy_lines:
                        if flag:
                            if emp_id == hierarchy_line.groups:
                                res.state = 'emp_approval'
                            if site_mgr_id == hierarchy_line.groups:
                                res.state = 'sic_approval'
                            if assis_hod_id == hierarchy_line.groups:
                                res.state = 'tic_approval'
                            if hod_id == hierarchy_line.groups:
                                res.state = 'hod_approval'
                            if gm_id == hierarchy_line.groups:
                                res.state = 'gm_approval'
                            if ed_id == hierarchy_line.groups:
                                res.state = 'ed_approval'
                            if md_id == hierarchy_line.groups:
                                res.state = 'md_approval'
                            return
                        if hod_id == hierarchy_line.groups:
                            flag = True
                            if hierarchy_line == hierarchy_lines[-1]:
                                res.action_approve()
                                res.notify_email_employee('Leave Approved')
                                return True

                if res.state == 'gm_approval':
                    flag = False
                    for hierarchy_line in hierarchy_lines:
                        if flag:
                            if emp_id == hierarchy_line.groups:
                                res.state = 'emp_approval'
                            if site_mgr_id == hierarchy_line.groups:
                                res.state = 'sic_approval'
                            if assis_hod_id == hierarchy_line.groups:
                                res.state = 'tic_approval'
                            if hod_id == hierarchy_line.groups:
                                res.state = 'hod_approval'
                            if gm_id == hierarchy_line.groups:
                                res.state = 'gm_approval'
                            if ed_id == hierarchy_line.groups:
                                res.state = 'ed_approval'
                            if md_id == hierarchy_line.groups:
                                res.state = 'md_approval'
                            return
                        if gm_id == hierarchy_line.groups:
                            flag = True
                            if hierarchy_line == hierarchy_lines[-1]:
                                res.action_approve()
                                res.notify_email_employee('Leave Approved')
                                return True

                if res.state == 'ed_approval':
                    flag = False
                    for hierarchy_line in hierarchy_lines:
                        if flag:
                            if emp_id == hierarchy_line.groups:
                                res.state = 'emp_approval'
                            if site_mgr_id == hierarchy_line.groups:
                                res.state = 'sic_approval'
                            if assis_hod_id == hierarchy_line.groups:
                                res.state = 'tic_approval'
                            if hod_id == hierarchy_line.groups:
                                res.state = 'hod_approval'
                            if gm_id == hierarchy_line.groups:
                                res.state = 'gm_approval'
                            if ed_id == hierarchy_line.groups:
                                res.state = 'ed_approval'
                            if md_id == hierarchy_line.groups:
                                res.state = 'md_approval'
                            return
                        if ed_id == hierarchy_line.groups:
                            flag = True
                            if hierarchy_line == hierarchy_lines[-1]:
                                res.action_approve()
                                res.notify_email_employee('Leave Approved')
                                return True

                if res.state == 'md_approval':
                    flag = False
                    for hierarchy_line in hierarchy_lines:
                        if flag:
                            if emp_id == hierarchy_line.groups:
                                res.state = 'emp_approval'
                            if site_mgr_id == hierarchy_line.groups:
                                res.state = 'sic_approval'
                            if assis_hod_id == hierarchy_line.groups:
                                res.state = 'tic_approval'
                            if hod_id == hierarchy_line.groups:
                                res.state = 'hod_approval'
                            if gm_id == hierarchy_line.groups:
                                res.state = 'gm_approval'
                            if ed_id == hierarchy_line.groups:
                                res.state = 'ed_approval'
                            if md_id == hierarchy_line.groups:
                                res.state = 'md_approval'
                            return
                        if md_id == hierarchy_line.groups:
                            flag = True
                            if hierarchy_line == hierarchy_lines[-1]:
                                res.action_approve()
                                res.notify_email_employee('Leave Approved')
                                return True

        return True

    @api.model
    def create(self, vals):
        res = super(HrHolidays, self).create(vals)
        if res.type == 'remove':
            self.set_status(res)
            if self.state != 'validate':
                self.notify_email_manager() 
            res.no_approval = 0    
        return res

    @api.multi
    def action_confirm(self):
        if self.type == 'remove' and self.employee_id.hierarchy_id:
            self.set_status(self)
            if self.state != 'validate':
                self.notify_email_manager()
            self.no_approval = 0
        else:
            res = super(HrHolidays, self).action_confirm()
            return res
        return True

    def notify_email_manager(self):
        next_manager_id = []
        emp_id = self.env.ref('propell_modifier_hierarchy.group_leave_employee')
        site_mgr_id = self.env.ref('propell_modifier_hierarchy.group_leave_sic')
        assis_hod_id = self.env.ref('propell_modifier_hierarchy.group_leave_tic')
        hod_id = self.env.ref('propell_modifier_hierarchy.group_leave_hod')
        gm_id = self.env.ref('propell_modifier_hierarchy.group_leave_gm')
        ed_id = self.env.ref('propell_modifier_hierarchy.group_leave_ed')
        md_id = self.env.ref('propell_modifier_hierarchy.group_leave_md')

        if self.state == 'confirm':
            next_manager_id = site_mgr_id
        if self.state == 'emp_approval':
            next_manager_id = emp_id
        if self.state == 'tic_approval':
            next_manager_id = assis_hod_id
        if self.state == 'hod_approval':
            next_manager_id = hod_id
        if self.state == 'gm_approval':
            next_manager_id = gm_id
        if self.state == 'ed_approval':
            next_manager_id = ed_id
        if self.state == 'md_approval':
            next_manager_id = md_id

        ctx = self.env.context.copy() if self.env.context else {}
        menu_id = self.env['ir.model.data'].get_object_reference('hr_holidays', 'menu_open_company_allocation')[1]
        action_id = self.env['ir.model.data'].get_object_reference('hr_holidays', 'open_company_allocation')[1]
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        ctx['approval_link'] = base_url + "/web?#id=" + str(self.id) + "&view_type=form&model=hr.holidays&menu_id=" + str(menu_id) + "&action=" + str(action_id)

        mail_from = self.employee_id.user_id.partner_id.email
        template_id = self.env.ref('propell_modifier_hierarchy.email_temp_leave_approval_manager')
        gm_id = self.env.ref('propell_modifier_hierarchy.group_leave_gm')
        ed_id = self.env.ref('propell_modifier_hierarchy.group_leave_ed')
        md_id = self.env.ref('propell_modifier_hierarchy.group_leave_md')
        if next_manager_id:
            for user in next_manager_id.users:
                emp_id = self.env['hr.employee'].sudo().search([('user_id', '=', user.id), ('department_id', '=', self.employee_id.department_id.id)])
                flag = False
                if next_manager_id in [gm_id, ed_id, md_id]:
                    flag = True
                if emp_id or flag:
                    template_id.email_from = mail_from
                    if emp_id:
                        template_id.email_to = emp_id.work_email or emp_id.user_id.partner_id.email
                    else:
                        template_id.email_to = self.env['hr.employee'].search([('name', '=', user.name)]).work_email or user.login
                    # template_id.send_mail(self.id, force_send=True)
#                     if ctx.get('default_state') == 'next_approval':
                    if ctx.get('default_state'):
                        ctx.pop('default_state')
                    if template_id.email_from == template_id.email_to:
                        continue
                    template_id.with_context(ctx).send_mail(self.id, force_send=True)
        return template_id

    def notify_email_employee(self, subject):
        #notification to employee
        mail_from = self.employee_id.work_email or self.user_id.login
        emp_user = self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1)
        template_id = self.env.ref('propell_modifier_hierarchy.email_temp_leave_approval_notification')
        template_id.email_from = emp_user.work_email or emp_user.user_id.partner_id.email
        template_id.subject = subject
        template_id.email_to = mail_from
        template_id.send_mail(self.id, force_send=True)
        return template_id

    @api.multi
    def get_approval_email(self):
        email = ''
        if self.employee_id.work_email:
            email = self.employee_id.work_email
        elif self.employee_id.user_id.partner_id.email:
            email = self.employee_id.user_id.partner_id.email
        else:
            raise Warning(_(' Warning \n Email must be configured in %s Employee !') % (self.employee_id.name))
        return email

    #overide method
    @api.multi
    def action_approve(self):
        # if double_validation: this method is the first approval approval
        # if not double_validation: this method calls action_validate() below
        if not self.env.user.has_group('hr_holidays.group_hr_holidays_user'):
            raise UserError(_('Only an HR Officer or Manager can approve leave requests.'))

        manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for holiday in self:
            #if holiday.state != 'confirm':
                #raise UserError(_('Leave request must be confirmed ("To Approve") in order to approve it.'))

            if holiday.double_validation:
                return holiday.write({'state': 'validate1', 'manager_id': manager.id if manager else False})
            else:
                holiday.action_validate()

    #overide method
    @api.multi
    def action_validate(self):
        if not self.env.user.has_group('hr_holidays.group_hr_holidays_user'):
            raise UserError(_('Only an HR Officer or Manager can approve leave requests.'))

        manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for holiday in self:
            #if holiday.state not in ['confirm', 'validate1']:
                #raise UserError(_('Leave request must be confirmed in order to approve it.'))
            if holiday.state == 'validate1' and not holiday.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
                raise UserError(_('Only an HR Manager can apply the second approval on leave requests.'))

            holiday.write({'state': 'validate'})
            if holiday.double_validation:
                holiday.write({'manager_id2': manager.id})
            else:
                holiday.write({'manager_id': manager.id})
            if holiday.holiday_type == 'employee' and holiday.type == 'remove':
                meeting_values = {
                    'name': holiday.display_name,
                    'categ_ids': [(6, 0, [holiday.holiday_status_id.categ_id.id])] if holiday.holiday_status_id.categ_id else [],
                    'duration': holiday.number_of_days_temp * HOURS_PER_DAY,
                    'description': holiday.notes,
                    'user_id': holiday.user_id.id,
                    'start': holiday.date_from,
                    'stop': holiday.date_to,
                    'allday': False,
                    'state': 'open',            # to block that meeting date in the calendar
                    'privacy': 'confidential'
                }
                #Add the partner_id (if exist) as an attendee
                if holiday.user_id and holiday.user_id.partner_id:
                    meeting_values['partner_ids'] = [(4, holiday.user_id.partner_id.id)]

                meeting = self.env['calendar.event'].with_context(no_mail_to_attendees=True).create(meeting_values)
                holiday._create_resource_leave()
                holiday.write({'meeting_id': meeting.id})
            elif holiday.holiday_type == 'category':
                leaves = self.env['hr.holidays']
                for employee in holiday.category_id.employee_ids:
                    values = holiday._prepare_create_by_category(employee)
                    leaves += self.with_context(mail_notify_force_send=False).create(values)
                # TODO is it necessary to interleave the calls?
                leaves.action_approve()
                if leaves and leaves[0].double_validation:
                    leaves.action_validate()
        return True

    #overide method
    @api.multi
    def action_refuse(self):
        if not self.env.user.has_group('hr_holidays.group_hr_holidays_user'):
            raise UserError(_('Only an HR Officer or Manager can refuse leave requests.'))

        manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for holiday in self:
            #if holiday.state not in ['confirm', 'validate', 'validate1']:
                #raise UserError(_('Leave request must be confirmed or validated in order to refuse it.'))

            if holiday.state == 'validate1':
                holiday.write({'state': 'refuse', 'manager_id': manager.id})
            else:
                holiday.write({'state': 'refuse', 'manager_id2': manager.id})
            # Delete the meeting
            if holiday.meeting_id:
                holiday.meeting_id.unlink()
            # If a category that created several holidays, cancel all related
            holiday.linked_request_ids.action_refuse()

            mail_to = holiday.employee_id.user_id.partner_id.email
            mail_from = ''
            employee_id = self.env['hr.employee'].search([('user_id', '=', self._uid)])
            if employee_id:
                mail_from = employee_id.work_email
            if not mail_from:
                user = self.env['res.users'].search([('id', '=', self._uid)])
                mail_from = user.partner_id.email
            template_id = self.env.ref('propell_modifier_hierarchy.email_temp_leave_refuse_notification')
            template_id.email_from = mail_from
            template_id.email_to = mail_to

            ctx = self.env.context.copy() if self.env.context else {}
            menu_id = self.env['ir.model.data'].get_object_reference('hr_holidays', 'menu_open_company_allocation')[1]
            action_id = self.env['ir.model.data'].get_object_reference('hr_holidays', 'open_company_allocation')[1]
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            ctx['approval_link'] = base_url + "/web?#id=" + str(holiday.id) + "&view_type=form&model=hr.holidays&menu_id=" + str(menu_id) + "&action=" + str(action_id)
#             if ctx.get('default_state') == 'next_approval':
            if ctx.get('default_state'):
                ctx.pop('default_state')
            template_id.with_context(ctx).send_mail(holiday.id, force_send=True)

        self._remove_resource_leave()

        return True
