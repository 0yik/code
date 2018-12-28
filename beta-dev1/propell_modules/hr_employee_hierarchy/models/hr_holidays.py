from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
# import logging
# _logger = logging.getLogger(__name__)

class hr_employee(models.Model):
    _inherit = 'hr.employee'

    def get_groups(self):
        for obj in self:
            worker_id = self.env.ref('hr_employee_hierarchy.group_leave_worker')
            superwiser_id = self.env.ref('hr_employee_hierarchy.group_leave_supervisor')
            eng_id = self.env.ref('hr_employee_hierarchy.group_leave_engineer')
            sic_id = self.env.ref('hr_employee_hierarchy.group_leave_sic')
            assis_hod_id = self.env.ref('hr_employee_hierarchy.group_leave_tic')
            hod_id = self.env.ref('hr_employee_hierarchy.group_leave_hod')
            gm_id = self.env.ref('hr_employee_hierarchy.group_leave_gm')
            ed_id = self.env.ref('hr_employee_hierarchy.group_leave_ed')
            md_id = self.env.ref('hr_employee_hierarchy.group_leave_md')
            string = ''
            if obj.user_id and obj.user_id.id in worker_id.users.ids:
                string += worker_id.name + ", "
            if obj.user_id and obj.user_id.id in superwiser_id.users.ids:
                string += superwiser_id.name + ", "
            if obj.user_id and obj.user_id.id in eng_id.users.ids:
                string += eng_id.name + ", "
            if obj.user_id and obj.user_id.id in sic_id.users.ids:
                string += sic_id.name + ", "
            if obj.user_id and obj.user_id.id in assis_hod_id.users.ids:
                string += assis_hod_id.name + ", "
            if obj.user_id and obj.user_id.id in hod_id.users.ids:
                string += hod_id.name + ", "
            if obj.user_id and obj.user_id.id in gm_id.users.ids:
                string += gm_id.name + ", "
            if obj.user_id and obj.user_id.id in ed_id.users.ids:
                string += ed_id.name + ", "
            if obj.user_id and obj.user_id.id in md_id.users.ids:
                string += md_id.name + ", "

            obj.emp_group_level = string[:-2]

    current_leave_state = fields.Selection(compute='_compute_leave_status', string="Current Leave Status",
        selection=[
            ('draft', 'New'),
            ('confirm', 'Waiting for SIC/Manager approval'),
            ('tic_approval', 'Waiting for TIC/OIC approval'),
            ('hod_approval', 'Waiting for HOD approval'),
            ('gm_approval', 'Waiting for GM approval'),
            ('ed_approval', 'Waiting for ED approval'),
            ('md_approval', 'Waiting for MD approval'),
            ('next_approval', 'Waiting for Next Manager approval'),
            ('refuse', 'Refused'), ('validate1', 'Waiting Final Approval'),
            ('validate', 'Approved'), ('cancel', 'Cancelled')
        ])
    hierarchy_id = fields.Many2one('leave.approve.hierarchy', string="Leave Approval Hierarchy")
    emp_group_level = fields.Char(compute="get_groups", string="Leave Group")

class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    @api.depends('holiday_status_id')
    def _is_off_in_lieu(self):
        for obj in self:
            if obj.holiday_status_id.name == 'OIL':
                obj.is_oil = True

    state = fields.Selection([('draft', 'New'), ('confirm', 'Waiting for SIC/Manager approval'),
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
    state_change = fields.Boolean(default=False)
    is_oil = fields.Boolean(compute="_is_off_in_lieu", default=False)

    def notify_email_manager(self,next_manager_id):
       #notification to leave manager .
        if self.id == False:
           return
        temp_id = self.env['ir.model.data'].get_object_reference('hr_employee_hierarchy', 'email_temp_leave_approval_manager')[1]
        ctx = self.env.context.copy() if self.env.context else {}
        menu_id = self.env['ir.model.data'].get_object_reference('hr_holidays', 'menu_open_company_allocation')[1]
        action_id =  self.env['ir.model.data'].get_object_reference('hr_holidays','open_company_allocation')[1]
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        ctx['approval_link'] = base_url + "/web?#id="+ str(self.id) +"&view_type=form&model=hr.holidays&menu_id="+str(menu_id)+"&action=" + str(action_id)
#         ctx['approval_link'] = base_url + "/web#id="+ str(self.id) +"&view_type=form&model=hr.holidays"
        mail_from = self.employee_id.user_id.partner_id.email
        template_id = self.env.ref('hr_employee_hierarchy.email_temp_leave_approval_manager')
        gm_id = self.env.ref('hr_employee_hierarchy.group_leave_gm')
        ed_id = self.env.ref('hr_employee_hierarchy.group_leave_ed')
        md_id = self.env.ref('hr_employee_hierarchy.group_leave_md')
        for user in next_manager_id.users:
            emp_id = self.env['hr.employee'].sudo().search([('user_id', '=', user.id), ('department_id', '=', self.employee_id.department_id.id)], limit=1)
            flag = False
            if next_manager_id in [gm_id, ed_id, md_id]:
                flag = True
            if emp_id or flag:
                template_id.email_from = mail_from
                if emp_id:
                    template_id.email_to = emp_id.work_email or emp_id.user_id.partner_id.email
                else:
                    template_id.email_to = self.env['hr.employee'].search([('name', '=', user.name)], limit=1).work_email or user.login
#                 template_id.email_to = self.env['hr.employee'].search([('name','=',user.name)]).work_email or user.login
                # template_id.send_mail(self.id, force_send=True)
#                 if ctx.get('default_state') == 'next_approval':
                if ctx.get('default_state'):
                    ctx.pop('default_state')
                if template_id.email_from == template_id.email_to:
                    continue
                template_id.with_context(ctx).send_mail(self.id, force_send=True)
        return template_id

    def notify_email(self, users):
        ctx = self.env.context.copy() if self.env.context else {}
        menu_id = self.env['ir.model.data'].get_object_reference('hr_holidays', 'menu_open_company_allocation')[1]
        action_id = self.env['ir.model.data'].get_object_reference('hr_holidays', 'open_company_allocation')[1]
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        ctx['approval_link'] = base_url + "/web?#id=" + str(self.id) + "&view_type=form&model=hr.holidays&menu_id=" + str(menu_id) + "&action=" + str(action_id)

        mail_from = self.employee_id.work_email or self.employee_id.user_id.partner_id.email or self.employee_id.user_id.login
        template_id = self.env.ref('hr_employee_hierarchy.email_temp_leave_approval_manager')

        for user in users:
            emp_id = self.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
            template_id.email_from = mail_from
            email_to = False
            if emp_id:
                email_to = emp_id.work_email or emp_id.user_id.partner_id.email or emp_id.user_id.login
            template_id.email_to = email_to
            if ctx.get('default_state'):
                ctx.pop('default_state')
            template_id.with_context(ctx).send_mail(self.id, force_send=True)
        return template_id

    def approve_next(self):
        hod_id = self.env.ref('hr_employee_hierarchy.group_leave_hod')
        employee_ids = self.env['hr.employee'].sudo().search([('department_id', '=', self.employee_id.department_id.id)])
        user_ids = [x.user_id.id for x in employee_ids]
        if self._uid not in user_ids and self._uid != 1:
            raise ValidationError(_('Warning \n You can not Approve this Off in Lieu. Only HOD from %s department can approve this Leave.') % (self.employee_id.department_id.name))
        if self._uid not in hod_id.users.ids and self._uid != 1:
            raise ValidationError(_('Warning \n Only HOD of %s Department can Approve this Leave.') % (self.employee_id.department_id.name))
#         if self._uid != self.next_manager_id.user_id.id:

        self.action_approve()

        mail_from = False
        mail_to = self.employee_id.work_email or self.employee_id.user_id.partner_id.email or False
        emp_id = self.env['hr.employee'].sudo().search([('user_id', '=', self._uid)], limit=1)
        if emp_id:
            mail_from = emp_id.work_email or emp_id.user_id.partner_id.email or emp_id.user_id.login

        template_id = self.env.ref('hr_employee_hierarchy.email_temp_leave_approval_notification_for_oil')
        template_id.email_from = mail_from
        template_id.email_to = mail_to
        ctx = self.env.context.copy() if self.env.context else {}
#         if ctx.get('default_state') == 'next_approval':
        if ctx.get('default_state'):
            ctx.pop('default_state')
        template_id.with_context(ctx).send_mail(self.id, force_send=True)
#         template_id.send_mail(self.id, force_send=True)
        return

    def validate_allocate_leave(self):
        if self.type == 'add':
            self.action_approve()
 
        return

    def leave_approve_hierarchy(self, from_create=False):
        group_ids = []
        sic_id = self.env.ref('hr_employee_hierarchy.group_leave_sic')
        assis_hod_id = self.env.ref('hr_employee_hierarchy.group_leave_tic')
        hod_id = self.env.ref('hr_employee_hierarchy.group_leave_hod')
        gm_id = self.env.ref('hr_employee_hierarchy.group_leave_gm')
        ed_id = self.env.ref('hr_employee_hierarchy.group_leave_ed')
        md_id = self.env.ref('hr_employee_hierarchy.group_leave_md')
        for hierarchy_line in self.employee_id.hierarchy_id.hierarchy_line_ids:
            group_ids.append(hierarchy_line.groups.id)
        if self.state == 'draft' or self.state == 'pm_approval':
            if sic_id.id in group_ids and (self.employee_id.user_id.id not in sic_id.users.ids and self.employee_id.user_id.id not in assis_hod_id.users.ids and self.employee_id.user_id.id not in hod_id.users.ids and self.employee_id.user_id.id not in gm_id.users.ids and self.employee_id.user_id.id not in ed_id.users.ids and self.employee_id.user_id.id not in md_id.users.ids):
                self.state = 'confirm'
                return self.state
            elif assis_hod_id.id in group_ids and (self.employee_id.user_id.id not in assis_hod_id.users.ids and self.employee_id.user_id.id not in hod_id.users.ids and self.employee_id.user_id.id not in gm_id.users.ids and self.employee_id.user_id.id not in ed_id.users.ids and self.employee_id.user_id.id not in md_id.users.ids):
                self.state = 'tic_approval'
                return self.state
            elif hod_id.id in group_ids and (self.employee_id.user_id.id not in hod_id.users.ids and self.employee_id.user_id.id not in gm_id.users.ids and self.employee_id.user_id.id not in ed_id.users.ids and self.employee_id.user_id.id not in md_id.users.ids):
                self.state = 'hod_approval'
                return self.state
            elif gm_id.id in group_ids and (self.employee_id.user_id.id not in gm_id.users.ids and self.employee_id.user_id.id not in ed_id.users.ids and self.employee_id.user_id.id not in md_id.users.ids):
                self.state = 'gm_approval'
                return self.state
            elif ed_id.id in group_ids and (self.employee_id.user_id.id not in ed_id.users.ids and self.employee_id.user_id.id not in md_id.users.ids):
                self.state = 'ed_approval'
                return self.state
            elif md_id.id in group_ids and (self.employee_id.user_id.id not in md_id.users.ids):
                self.state = 'md_approval'
                return self.state
        if self.state == 'confirm':
            if from_create and not self.is_recovery:
                if sic_id.id in group_ids and (self.employee_id.user_id.id not in sic_id.users.ids and self.employee_id.user_id.id not in assis_hod_id.users.ids and self.employee_id.user_id.id not in hod_id.users.ids and self.employee_id.user_id.id not in gm_id.users.ids and self.employee_id.user_id.id not in ed_id.users.ids and self.employee_id.user_id.id not in md_id.users.ids):
                    self.state = 'confirm'
                    return self.state
            if from_create and self.is_recovery and sic_id.id in group_ids and (self.employee_id.user_id.id not in sic_id.users.ids and self.employee_id.user_id.id not in assis_hod_id.users.ids and self.employee_id.user_id.id not in hod_id.users.ids and self.employee_id.user_id.id not in gm_id.users.ids and self.employee_id.user_id.id not in ed_id.users.ids and self.employee_id.user_id.id not in md_id.users.ids):
                self.state = 'confirm'
                return self.state

            if assis_hod_id.id in group_ids and (self.employee_id.user_id.id not in assis_hod_id.users.ids and self.employee_id.user_id.id not in hod_id.users.ids and self.employee_id.user_id.id not in gm_id.users.ids and self.employee_id.user_id.id not in ed_id.users.ids and self.employee_id.user_id.id not in md_id.users.ids):
                self.state = 'tic_approval'
                return self.state
            elif hod_id.id in group_ids and (self.employee_id.user_id.id not in hod_id.users.ids and self.employee_id.user_id.id not in gm_id.users.ids and self.employee_id.user_id.id not in ed_id.users.ids and self.employee_id.user_id.id not in md_id.users.ids):
                self.state = 'hod_approval'
                return self.state
            elif gm_id.id in group_ids and (self.employee_id.user_id.id not in gm_id.users.ids and self.employee_id.user_id.id not in ed_id.users.ids and self.employee_id.user_id.id not in md_id.users.ids):
                self.state = 'gm_approval'
                return self.state
            elif ed_id.id in group_ids and (self.employee_id.user_id.id not in ed_id.users.ids and self.employee_id.user_id.id not in md_id.users.ids):
                self.state = 'ed_approval'
                return self.state
            elif md_id.id in group_ids and (self.employee_id.user_id.id not in md_id.users.ids):
                self.state = 'md_approval'
                return self.state
        if self.state == 'tic_approval':
            if hod_id.id in group_ids:
                self.state = 'hod_approval'
                return self.state
            elif gm_id.id in group_ids:
                self.state = 'gm_approval'
                return self.state
            elif ed_id.id in group_ids:
                self.state = 'ed_approval'
                return self.state
            elif md_id.id in group_ids:
                self.state = 'md_approval'
                return self.state
        if self.state == 'hod_approval':
            if gm_id.id in group_ids:
                self.state = 'gm_approval'
                return self.state
            elif ed_id.id in group_ids:
                self.state = 'ed_approval'
                return self.state
            elif md_id.id in group_ids:
                self.state = 'md_approval'
                return self.state
        if self.state == 'gm_approval':
            if ed_id.id in group_ids:
                self.state = 'ed_approval'
                return self.state
            elif md_id.id in group_ids:
                self.state = 'md_approval'
                return self.state
        if self.state == 'ed_approval':
            if md_id.id in group_ids:
                self.state = 'md_approval'
                return self.state

        return

    def approve_sic(self):
        sic_id = self.env.ref('hr_employee_hierarchy.group_leave_sic')
        assis_hod_id = self.env.ref('hr_employee_hierarchy.group_leave_tic')
        hod_id = self.env.ref('hr_employee_hierarchy.group_leave_hod')
        gm_id = self.env.ref('hr_employee_hierarchy.group_leave_gm')
        ed_id = self.env.ref('hr_employee_hierarchy.group_leave_ed')
        md_id = self.env.ref('hr_employee_hierarchy.group_leave_md')
        if self.employee_id.hierarchy_id:
            employee_ids = self.env['hr.employee'].sudo().search([('department_id', '=', self.employee_id.department_id.id)])
            user_ids = [x.user_id.id for x in employee_ids]
            if self._uid not in user_ids and self._uid != 1:
                raise ValidationError(_('Warning \n Only SIC of %s Department can Approve this Leave.') % (self.employee_id.department_id.name))

            state=self.leave_approve_hierarchy()
            if state =='tic_approval':
                self.notify_email_manager(assis_hod_id)
            if state =='hod_approval':
                self.notify_email_manager(hod_id)
            if state =='gm_approval':
                self.notify_email_manager(gm_id)
            if state == 'ed_approval':
                self.notify_email_manager(ed_id)
            if state == 'md_approval':
                self.notify_email_manager(md_id)
        else:
            assis_hod_id = self.env.ref('hr_employee_hierarchy.group_leave_tic')
            self.write({'state': 'tic_approval'})
            self.notify_email_manager(assis_hod_id)
        return

    def approve_tic(self):
        sic_id = self.env.ref('hr_employee_hierarchy.group_leave_sic')
        assis_hod_id = self.env.ref('hr_employee_hierarchy.group_leave_tic')
        hod_id = self.env.ref('hr_employee_hierarchy.group_leave_hod')
        gm_id = self.env.ref('hr_employee_hierarchy.group_leave_gm')
        ed_id = self.env.ref('hr_employee_hierarchy.group_leave_ed')
        md_id = self.env.ref('hr_employee_hierarchy.group_leave_md')

        if self.employee_id.hierarchy_id:
            employee_ids = self.env['hr.employee'].sudo().search([('department_id', '=', self.employee_id.department_id.id)])
            user_ids = [x.user_id.id for x in employee_ids]
            if self._uid not in user_ids and self._uid != 1:
                raise ValidationError(_('Warning \n Only TIC of %s Department can Approve this Leave.') % (self.employee_id.department_id.name))

            state=self.leave_approve_hierarchy()
            if state =='hod_approval':
                self.notify_email_manager(hod_id)
            if state =='gm_approval':
                self.notify_email_manager(gm_id)
            if state == 'ed_approval':
                self.notify_email_manager(ed_id)
            if state == 'md_approval':
                self.notify_email_manager(md_id)
        else:
            hod_id = self.env.ref('hr_employee_hierarchy.group_leave_hod')
            self.write({'state': 'hod_approval'})
            self.notify_email_manager(hod_id)
        return

    def approve_hod(self):
        sic_id = self.env.ref('hr_employee_hierarchy.group_leave_sic')
        assis_hod_id = self.env.ref('hr_employee_hierarchy.group_leave_tic')
        hod_id = self.env.ref('hr_employee_hierarchy.group_leave_hod')
        gm_id = self.env.ref('hr_employee_hierarchy.group_leave_gm')
        ed_id = self.env.ref('hr_employee_hierarchy.group_leave_ed')
        md_id = self.env.ref('hr_employee_hierarchy.group_leave_md')

        if self.employee_id.hierarchy_id:
            employee_ids = self.env['hr.employee'].sudo().search([('department_id', '=', self.employee_id.department_id.id)])
            user_ids = [x.user_id.id for x in employee_ids]
            if self._uid not in user_ids and self._uid != 1:
                raise ValidationError(_('Warning \n Only HOD of %s Department can Approve this Leave.') % (self.employee_id.department_id.name))

            state=self.leave_approve_hierarchy()
            if state =='gm_approval':
                self.notify_email_manager(gm_id)
            if state == 'ed_approval':
                self.notify_email_manager(ed_id)
            if state == 'md_approval':
                self.notify_email_manager(md_id)
        else:
            gm_id = self.env.ref('hr_employee_hierarchy.group_leave_gm')
            self.write({'state': 'gm_approval'})
            self.notify_email_manager(gm_id)
        return

    def approve_gm(self):
 
        rec_id1 = self.env.ref('hr_employee_hierarchy.group_leave_engineer')
        rec_id2 = self.env.ref('hr_employee_hierarchy.group_leave_supervisor')
        rec_id3 = self.env.ref('hr_employee_hierarchy.group_leave_worker')
        ed_id = self.env.ref('hr_employee_hierarchy.group_leave_ed')
        if (self.employee_id.user_id.id in rec_id1.users.ids) or (self.employee_id.user_id.id in rec_id2.users.ids) or (self.employee_id.user_id.id in rec_id3.users.ids):
            self.action_approve()
            self.notify_email_employee('Leave Approved')
        else:
            sic_id = self.env.ref('hr_employee_hierarchy.group_leave_sic')
            assis_hod_id = self.env.ref('hr_employee_hierarchy.group_leave_tic')
            hod_id = self.env.ref('hr_employee_hierarchy.group_leave_hod')
            gm_id = self.env.ref('hr_employee_hierarchy.group_leave_gm')
            ed_id = self.env.ref('hr_employee_hierarchy.group_leave_ed')
            md_id = self.env.ref('hr_employee_hierarchy.group_leave_md')
            if self.employee_id.hierarchy_id:
#                 employee_ids = self.env['hr.employee'].sudo().search([('department_id', '=', self.employee_id.department_id.id)])
#                 user_ids = [x.user_id.id for x in employee_ids]
#                 if self._uid not in user_ids and self._uid != 1:
#                     raise ValidationError(_('Warning \n Only GM of %s Department can Approve this Leave.') % (self.employee_id.department_id.name))

                state=self.leave_approve_hierarchy()
                if state == 'ed_approval':
                    self.notify_email_manager(ed_id)
                if state == 'md_approval':
                    self.notify_email_manager(md_id)
            else:
                self.write({'state': 'ed_approval'})
                self.notify_email_manager(ed_id)
        return

    def approve_ed(self):
#         Approve if GM is not in hierarchy
        rec_id1 = self.env.ref('hr_employee_hierarchy.group_leave_engineer')
        rec_id2 = self.env.ref('hr_employee_hierarchy.group_leave_supervisor')
        rec_id3 = self.env.ref('hr_employee_hierarchy.group_leave_worker')
        if (self.employee_id.user_id.id in rec_id1.users.ids) or (self.employee_id.user_id.id in rec_id2.users.ids) or (self.employee_id.user_id.id in rec_id3.users.ids):
            self.action_approve()
            self.notify_email_employee('Leave Approved')
            return
#         *********
        rec_id = self.env.ref('hr_employee_hierarchy.group_leave_sic')
        md_id = self.env.ref('hr_employee_hierarchy.group_leave_md')

        if self.employee_id.user_id.id in rec_id.users.ids:
            self.action_approve()
            self.notify_email_employee('Leave Approved')

        else:
            sic_id = self.env.ref('hr_employee_hierarchy.group_leave_sic')
            assis_hod_id = self.env.ref('hr_employee_hierarchy.group_leave_tic')
            hod_id = self.env.ref('hr_employee_hierarchy.group_leave_hod')
            gm_id = self.env.ref('hr_employee_hierarchy.group_leave_gm')
            ed_id = self.env.ref('hr_employee_hierarchy.group_leave_ed')
            md_id = self.env.ref('hr_employee_hierarchy.group_leave_md')
            if self.employee_id.hierarchy_id:
#                 employee_ids = self.env['hr.employee'].sudo().search([('department_id', '=', self.employee_id.department_id.id)])
#                 user_ids = [x.user_id.id for x in employee_ids]
#                 if self._uid not in user_ids and self._uid != 1:
#                     raise ValidationError(_('Warning \n Only ED of %s Department can Approve this Leave.') % (self.employee_id.department_id.name))

                state=self.leave_approve_hierarchy()
                if state == 'md_approval':
                    self.notify_email_manager(md_id)
            else:
                self.write({'state': 'md_approval'})
                self.notify_email_manager(md_id)
        return

    def approve_md(self):
        self.action_approve()
        self.notify_email_employee('Leave Approved')
        return

    @api.multi
    def action_refuse(self):
        if self.state !=False:
            if self._uid == self.employee_id.user_id.id and self._uid != 1:
                raise ValidationError(_('Sorry, You can not Refuse your own Leave.'))

            engineer_grp = self.env.ref('hr_employee_hierarchy.group_leave_engineer')
            supervisor_grp = self.env.ref('hr_employee_hierarchy.group_leave_supervisor')
            worker_grp = self.env.ref('hr_employee_hierarchy.group_leave_worker')
            site_mgr_id = self.env.ref('hr_employee_hierarchy.group_leave_sic')
            assis_hod_id = self.env.ref('hr_employee_hierarchy.group_leave_tic')
            hod_id = self.env.ref('hr_employee_hierarchy.group_leave_hod')
            gm_id = self.env.ref('hr_employee_hierarchy.group_leave_gm')
            ed_id = self.env.ref('hr_employee_hierarchy.group_leave_ed')
            flag = False

            if (self._uid in engineer_grp.users.ids or self._uid in supervisor_grp.users.ids or self._uid in worker_grp.users.ids) and self._uid != 1:
                flag = True

            if self._uid in site_mgr_id.users.ids and self.state == 'confirm' and self._uid != 1 and (self.employee_id.user_id.id in site_mgr_id.users.ids or self.employee_id.user_id.id in assis_hod_id.users.ids or self.employee_id.user_id.id in hod_id.users.ids or self.employee_id.user_id.id in gm_id.users.ids or self.employee_id.user_id.id in ed_id.users.ids):
                flag = True
            if self.state == 'tic_approval' and (self.employee_id.user_id.id in assis_hod_id.users.ids or self.employee_id.user_id.id in hod_id.users.ids or self.employee_id.user_id.id in gm_id.users.ids or self.employee_id.user_id.id in ed_id.users.ids) and self._uid != 1:
                if self._uid in assis_hod_id.users.ids or self._uid in site_mgr_id.users.ids:
                    flag = True
            if self.state == 'hod_approval' and (self.employee_id.user_id.id in hod_id.users.ids or self.employee_id.user_id.id in gm_id.users.ids or self.employee_id.user_id.id in ed_id.users.ids) and self._uid != 1:
                if self._uid in assis_hod_id.users.ids or self._uid in site_mgr_id.users.ids or self._uid in hod_id.users.ids:
                    flag = True

            if (self._uid not in gm_id.users.ids or self._uid not in ed_id.users.ids) and self._uid != 1:
                emp = self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1)

                tmp = False
                if self.state in ['eng_approval', 'sup_approval', 'pm_approval'] and self.type == 'remove':
                    team_member_ids = self.env['project.teammember'].sudo().search([('team_member', 'in', [self.employee_id.user_id.id])])
                    project_ids = self.env['project.project'].sudo().search([('supervisor_id', 'in', [self.employee_id.user_id.id])])
                    for team_member_id in team_member_ids:
                        if self.state == 'eng_approval':
                            if self._uid not in team_member_id.project_id.engineer_ids.ids:
                                raise ValidationError(_('Sorry, You can not Refuse Leave, Only engineer from %s project can approve this Leave.') % (team_member_id.project_id.name))
                            else:
                                tmp = True
                                break

                        if self.state == 'sup_approval':
                            if self._uid not in team_member_id.project_id.supervisor_id.ids:
                                raise ValidationError(_('Sorry, You can not Refuse Leave, Only Supervisor can approve this Leave.'))
                            else:
                                tmp = True
                                break

                        if self.state == 'pm_approval':
                            if self._uid not in team_member_id.project_id.user_id.ids:
                                raise ValidationError(_('Sorry, You can not Refuse Leave, Only Project Manager can approve this Leave.'))
                            else:
                                tmp = True
                                break
#                         if self._uid in team_member_id.project_id.supervisor_id.ids:
#                             tmp = True
#                             break

#                         if self._uid in team_member_id.project_id.user_id.ids:
#                             tmp = True
#                             break

                    for project_id in project_ids:
                        if self._uid in project_id.user_id.ids:
                            tmp = True
                            break

                if emp and self.employee_id.department_id != emp.department_id and not tmp:
                    raise ValidationError(_('Sorry, You can not Refuse Leave, you are belongs from Other Department.'))

#             if self.state == 'gm_approval' and self._uid != 1:
#                 if self._uid in assis_hod_id.users.ids or self._uid in site_mgr_id.users.ids or self._uid in hod_id.users.ids or self._uid in gm_id.users.ids:
#                     flag = True
#             if self.state == 'ed_approval' and self._uid != 1:
#                 if self._uid in assis_hod_id.users.ids or self._uid in site_mgr_id.users.ids or self._uid in hod_id.users.ids or self._uid in gm_id.users.ids or self._uid in ed_id.users.ids:
#                     flag = True

            if flag:
                raise ValidationError(_('Sorry, You can not Refuse Leave, you are belongs from same group.'))

            mail_to = self.employee_id.user_id.partner_id.email
            user = self.env['res.users'].search([('id', '=', self._uid)])
            template_id = self.env.ref('hr_employee_hierarchy.email_temp_leave_refuse_notification')
            template_id.email_from = user.partner_id.email
            template_id.email_to = mail_to

            ctx = self.env.context.copy() if self.env.context else {}
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            ctx['approval_link'] = base_url + "/web#id="+ str(self.id) +"&view_type=form&model=hr.holidays"
#             if ctx.get('default_state') == 'next_approval':
            if ctx.get('default_state'):
                ctx.pop('default_state')
            template_id.with_context(ctx).send_mail(self.id, force_send=True)
#             template_id.send_mail(self.id, force_send=True)
            res = super(HrHolidays, self).action_refuse()
        return

    def project_approval_hierarchy(self):
        team_member_ids = self.env['project.teammember'].sudo().search([('team_member', 'in', [self.employee_id.user_id.id])])
        project_ids = self.env['project.project'].sudo().search([('supervisor_id', 'in', [self.employee_id.user_id.id])])
        flag = False
        for team_member_id in team_member_ids:
            if team_member_id.project_id.allow_eng:
                self.state = 'eng_approval'
                self.notify_email(team_member_id.project_id.engineer_ids)
                return True

            if team_member_id.project_id.supervisor_id and not team_member_id.project_id.allow_eng:
                if not flag:
                    self.state = 'sup_approval'
                    flag = True
                self.notify_email(team_member_id.project_id.supervisor_id)

            if team_member_id.project_id.user_id and not team_member_id.project_id.supervisor_id and not team_member_id.project_id.allow_eng:
                if not flag:
                    self.state = 'pm_approval'
                    flag = True
                self.notify_email(team_member_id.project_id.user_id)
        if flag:
            return True
        flag1 = False
        for project_id in project_ids:
            if not flag1:
                self.state = 'pm_approval'
                flag1 = True
            self.notify_email(project_id.user_id)
        if flag1:
            return True

        return False

    @api.model
    def create(self, vals):
        res = super(HrHolidays, self).create(vals)
        if res.employee_id.leave_manager:
            res.next_manager_id = res.employee_id.leave_manager.id
        if vals.get('from_project'):
            approve = res.project_approval_hierarchy()
            if approve:
                return res

#         NOTE : set status
        site_mgr_id = self.env.ref('hr_employee_hierarchy.group_leave_sic')
        assis_hod_id = self.env.ref('hr_employee_hierarchy.group_leave_tic')
        hod_id = self.env.ref('hr_employee_hierarchy.group_leave_hod')
        gm_id = self.env.ref('hr_employee_hierarchy.group_leave_gm')
        ed_id = self.env.ref('hr_employee_hierarchy.group_leave_ed')
        md_id = self.env.ref('hr_employee_hierarchy.group_leave_md')

        if res.is_recovery and res.state != 'confirm':
            res.state = 'confirm'
        if res.holiday_status_id.name == 'OIL' and res.type == 'add':
            employee_ids = self.env['hr.employee'].sudo().search([('department_id', '=', res.employee_id.department_id.id)])
            user_ids = [x.user_id.id for x in employee_ids]
            hod_id = self.env.ref('hr_employee_hierarchy.group_leave_hod')
            s1 = set(user_ids)
            s2 = set(hod_id.users.ids)
            if not s1.intersection(s2):
                raise UserError(_('Your department does not have HOD. Off in Lieu is approved by HOD.'))
            res.state = 'next_approval'
#             res.notify_email_manager(hod_id)
            mail_from = res.employee_id.work_email or res.employee_id.user_id.partner_id.email or False
            for user in hod_id.users:
                if user.id in user_ids:
                    mail_to = False
                    emp_id = self.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
                    if emp_id:
                        mail_to = emp_id.work_email or emp_id.user_id.partner_id.email or emp_id.user_id.login

                    template_id = res.env.ref('hr_employee_hierarchy.email_temp_leave_approval_manager')
                    ctx = res.env.context.copy() if res.env.context else {}
                    menu_id = res.env['ir.model.data'].get_object_reference('hr_holidays', 'menu_open_company_allocation')[1]
                    action_id = res.env['ir.model.data'].get_object_reference('hr_holidays', 'open_company_allocation')[1]
                    base_url = res.env['ir.config_parameter'].sudo().get_param('web.base.url')
                    ctx['approval_link'] = base_url + "/web?#id=" + str(res.id) + "&view_type=form&model=hr.holidays&menu_id=" + str(menu_id) + "&action=" + str(action_id)

                    template_id.email_from = mail_from
                    template_id.email_to = mail_to
                    if ctx.get('default_state'):
                        ctx.pop('default_state')
                    template_id.with_context(ctx).send_mail(res.id, force_send=True)
            return res

        elif res.type == 'add' and not res.is_recovery:
            res.state = 'validate'
            return res

        if not res.employee_id.hierarchy_id:
            if res.employee_id.user_id.id in site_mgr_id.users.ids:
                res.state = 'tic_approval'
            elif res.employee_id.user_id.id in assis_hod_id.users.ids:
                res.state = 'hod_approval'
            elif res.employee_id.user_id.id in hod_id.users.ids:
                res.state = 'gm_approval'
            elif res.employee_id.user_id.id in gm_id.users.ids:
                res.state = 'ed_approval'
            elif res.employee_id.user_id.id in ed_id.users.ids:
                res.state = 'md_approval'
            else:
                res.state = 'confirm'

        else:
            #code to send email when leave request create
            if res.employee_id.hierarchy_id:
                state=res.leave_approve_hierarchy(True)
                if state =='confirm':
                    res.notify_email_manager(site_mgr_id)
                if state =='tic_approval':
                    res.notify_email_manager(assis_hod_id)
                if state =='hod_approval':
                    res.notify_email_manager(hod_id)
                if state =='gm_approval':
                    res.notify_email_manager(gm_id)
                if state == 'ed_approval':
                    res.notify_email_manager(ed_id)
                if state == 'md_approval':
                    res.notify_email_manager(md_id)
            else:

                res.state = 'confirm'
                res.notify_email_manager(site_mgr_id)

        return res

    @api.multi
    def action_confirm(self):
        if self.filtered(lambda holiday: holiday.state != 'draft'):
            raise UserError(_('Leave request must be in Draft state ("To Submit") in order to confirm it.'))
        if self.type == 'remove':
            approve = self.project_approval_hierarchy()
            if approve:
                return self

        if self.employee_id.leave_manager:
            self.next_manager_id = self.employee_id.leave_manager.id

#         NOTE : set status
        site_mgr_id = self.env.ref('hr_employee_hierarchy.group_leave_sic')
        assis_hod_id = self.env.ref('hr_employee_hierarchy.group_leave_tic')
        hod_id = self.env.ref('hr_employee_hierarchy.group_leave_hod')
        gm_id = self.env.ref('hr_employee_hierarchy.group_leave_gm')
        ed_id = self.env.ref('hr_employee_hierarchy.group_leave_ed')
        md_id = self.env.ref('hr_employee_hierarchy.group_leave_md')
        if self.holiday_status_id.name == 'OIL' and self.type == 'add':
            employee_ids = self.env['hr.employee'].sudo().search([('department_id', '=', self.employee_id.department_id.id)])
            user_ids = [x.user_id.id for x in employee_ids]
            hod_id = self.env.ref('hr_employee_hierarchy.group_leave_hod')
            s1 = set(user_ids)
            s2 = set(hod_id.users.ids)
            if not s1.intersection(s2):
                raise UserError(_('Your department does not have HOD. Off in Lieu is approved by HOD.'))
            self.state = 'next_approval'
#             res.notify_email_manager(hod_id)
            mail_from = self.employee_id.work_email or self.employee_id.user_id.partner_id.email or False
            for user in hod_id.users:
                if user.id in user_ids:
                    mail_to = False
                    emp_id = self.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
                    if emp_id:
                        mail_to = emp_id.work_email or emp_id.user_id.partner_id.email or emp_id.user_id.login

                    template_id = self.env.ref('hr_employee_hierarchy.email_temp_leave_approval_manager')
                    ctx = self.env.context.copy() if self.env.context else {}
                    menu_id = self.env['ir.model.data'].get_object_reference('hr_holidays', 'menu_open_company_allocation')[1]
                    action_id = self.env['ir.model.data'].get_object_reference('hr_holidays', 'open_company_allocation')[1]
                    base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                    ctx['approval_link'] = base_url + "/web?#id=" + str(self.id) + "&view_type=form&model=hr.holidays&menu_id=" + str(menu_id) + "&action=" + str(action_id)

                    template_id.email_from = mail_from
                    template_id.email_to = mail_to
                    if ctx.get('default_state'):
                        ctx.pop('default_state')
                    template_id.with_context(ctx).send_mail(self.id, force_send=True)
            return
        elif self.type == 'add' and not self.is_recovery:
            self.state = 'validate'
            return True

        if not self.employee_id.hierarchy_id:
            if self.employee_id.user_id.id in site_mgr_id.users.ids:
                self.state = 'tic_approval'
            elif self.employee_id.user_id.id in assis_hod_id.users.ids:
                self.state = 'hod_approval'
            elif self.employee_id.user_id.id in hod_id.users.ids:
                self.state = 'gm_approval'
            elif self.employee_id.user_id.id in gm_id.users.ids:
                self.state = 'ed_approval'
            elif self.employee_id.user_id.id in ed_id.users.ids:
                self.state = 'md_approval'
            else:
                self.state = 'confirm'
        else:
            if self.employee_id.hierarchy_id:
                state = self.leave_approve_hierarchy()
                if state =='confirm':
                    self.notify_email_manager(site_mgr_id)
                if state =='tic_approval':
                    self.notify_email_manager(assis_hod_id)
                if state =='hod_approval':
                    self.notify_email_manager(hod_id)
                if state =='gm_approval':
                    self.notify_email_manager(gm_id)
                if state == 'ed_approval':
                    self.notify_email_manager(ed_id)
                if state == 'md_approval':
                    self.notify_email_manager(md_id)
            else:
                self.state = 'confirm'
                self.notify_email_manager(site_mgr_id)

        return True

    def notify_email_employee(self,subject):
        #notification to employee
        mail_from = self.employee_id.work_email or self.user_id.login
        emp_user = self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1)
        template_id = self.env.ref('hr_employee_hierarchy.email_temp_leave_approval_notification')
        template_id.email_from = emp_user.work_email or emp_user.user_id.partner_id.email
        template_id.subject = subject
        template_id.email_to = mail_from
        template_id.send_mail(self.id, force_send=True)
        return template_id


    @api.multi
    def _notification_recipients(self, message, groups):
        """ Handle HR users and officers recipients that can validate or refuse holidays
        directly from email. """
        groups = super(HrHolidays, self)._notification_recipients(message, groups)

        self.ensure_one()
        hr_actions = []
        if self.state == 'confirm' and self.state=='refuse':
            app_action = self._notification_link_helper('controller', controller='/hr_holidays/validate')
            hr_actions += [{'url': app_action, 'title': _('Approve')}]
        if self.state in ['confirm', 'validate', 'validate1'] and self.state=='refuse':
            ref_action = self._notification_link_helper('controller', controller='/hr_holidays/refuse')
            hr_actions += [{'url': ref_action, 'title': _('Refuse')}]

        new_group = (
            'group_hr_holidays_user', lambda partner: bool(partner.user_ids) and any(user.has_group('hr_holidays.group_hr_holidays_user') for user in partner.user_ids), {
                'actions': hr_actions,
            })

        return [new_group] + groups