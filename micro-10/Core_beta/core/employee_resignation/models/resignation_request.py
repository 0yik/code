# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _
from datetime import datetime, timedelta


class ResignationRequest(models.Model):
    _name = 'resignation.request'
    _description = 'Resignation Request'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    name = fields.Char(
        string='Name', size=64, help='Unique Name of resignation.',
        default='New', )
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Employee', help='Employee', track_visibility='onchange',)
    cessation_date = fields.Date(
        string='Cessation Date', track_visibility='onchange')
    department_id = fields.Many2one(
        comodel_name='hr.department',
        string='Department', help='Department')
    join_date = fields.Date(
        string='Date Joined', track_visibility='onchange',)
    state = fields.Selection(
        selection=[('draft', 'Draft'),
                   ('waiting_approval', 'Waiting Approval'),
                   ('waiting_hr_approval', 'Waiting HR Approval'),
                   ('approved', 'Approved'),
                   ('reject', 'Rejected'),
                   ], string='State',
        help='Status of the resignation.', default='draft',
        track_visibility='onchange', )
    resignation_date = fields.Date(
        string='Resignation Date',
        help='Resignation Date of employee.', track_visibility='onchange',
        default=fields.Date.today, )
    resignation_note = fields.Text(
        string='Resignation Reason',
        help='Resignation Reason', track_visibility='onchange',)
    notice_period_id = fields.Many2one(
        comodel_name='employee.notice.period',
        string='Notice Period', help='', track_visibility='onchange',)
    department_comment = fields.Text(
        string='Department Comment',
        help='Department Comment by manager', track_visibility='onchange',)
    hr_comment = fields.Text(
        string='HR Manager Comment',
        help='HR Comment by manager', track_visibility='onchange',)

    @api.onchange('notice_period_id', 'resignation_date')
    def onchange_get_cessation_date(self):
        """docstring for onchange_get_cessation_date"""
        if self.notice_period_id and self.resignation_date:
            self.cessation_date = fields.Date.from_string(
                self.resignation_date) + timedelta(days=self.notice_period_id.duration)


    @api.onchange('employee_id')
    def onchange_employee_id(self):
        """docstring for onchange_employee"""
        if self.employee_id:
            self.notice_period_id = self.employee_id.notice_period_id and self.employee_id.notice_period_id.id or False
            self.join_date = self.employee_id.join_date
            self.department_id = self.employee_id.department_id and self.employee_id.department_id.id or False
            self.cessation_date = self.employee_id.cessation_date

    def get_url(self, obj):
        url = ''
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        menu_id = self.env['ir.model.data'].get_object_reference(
            'employee_resignation', 'menu_resignation_approve')[1]
        action_id = self.env['ir.model.data'].get_object_reference(
            'employee_resignation', 'act_open_resignation_approve_view')[1]
        url = base_url + "/web?db=" + str(self._cr.dbname) + "#id=" + str(
            obj.id) + "&view_type=form&model=resignation.request&menu_id="+str(
                menu_id)+"&action=" + str(action_id)
        return url

    @api.multi
    def action_submit(self):
        for self_obj in self:
            #if self_obj.employee_id.user_id.id != self.env.user.id:
            #    raise exceptions.UserError(_("You can not submit resignation of another employee."))
            ir_model_data = self.env['ir.model.data']
            try:
                template_id = ir_model_data.get_object_reference(
                    'employee_resignation',
                    'email_template_edi_resignation_request')[1]
            except ValueError:
                template_id = False

            ctx = self._context.copy()
            url = self.get_url(self_obj)
            ctx.update({'url': url})

            if not self.department_id.manager_id:
                raise exceptions.UserError(
                    _("Your department manager is not assign kindly contact your administrator."))

            if not self_obj.department_id.manager_id.work_email:
                raise exceptions.UserError(
                    _("Your department manager %s has \
                        do not have email address." %(self_obj.department_id.manager_id.name)))

            ctx.update({'email_to': self_obj.department_id.manager_id.work_email})
            ctx.update({'email_from': self.env.user.email})

            self_obj.write(
                {'name': self.env['ir.sequence'].next_by_code('resignation.request') or _('New'),
                 'state': 'waiting_approval', })
            self._cr.commit()
            ctx.update({'department_manager': self_obj.department_id.manager_id.name})

            if self_obj.resignation_date:
                ctx.update({'date_resignation': fields.Date.from_string(
                    self_obj.resignation_date).strftime('%d/%m/%Y')})
            else:
                ctx.update({'date_resignation': ''})
            if self_obj.cessation_date:
                ctx.update({'cessation_date': fields.Date.from_string(
                    self_obj.cessation_date).strftime('%d/%m/%Y')})
            else:
                ctx.update({'cessation_date': ''})

            # sending mail
            self.env['mail.template'].browse(template_id).with_context(
                ctx).send_mail(self_obj.id, force_send=True)

        return True

    @api.multi
    def action_approve_department_manager(self):
        for self_obj in self:
            if self.env.user.id != self.department_id.manager_id.user_id.id:
                raise exceptions.UserError(_("Sorry you can not approve this resignation request.\
                         Only %s can approve this resignation request." %(
                             self.department_id.manager_id.name)))
            ir_model_data = self.env['ir.model.data']
            try:
                template_id = ir_model_data.get_object_reference(
                    'employee_resignation',
                    'email_template_edi_resignation_request')[1]
            except ValueError:
                template_id = False

            ctx = self._context.copy()

            url = self.get_url(self_obj)
            ctx.update({'url': url})

            # finding hr manager users
            hr_manage_id = self.env.ref('hr.group_hr_manager').id
            user_ids = self.env['res.users'].search(
                [('groups_id', 'in',  [hr_manage_id])])

            if self_obj.resignation_date:
                ctx.update({'date_resignation': fields.Date.from_string(
                    self_obj.resignation_date).strftime('%d/%m/%Y')})
            else:
                ctx.update({'date_resignation': ''})

            if self_obj.cessation_date:
                ctx.update({'cessation_date': fields.Date.from_string(
                    self_obj.cessation_date).strftime('%d/%m/%Y')})
            else:
                ctx.update({'cessation_date': ''})

            for user in user_ids:
                ctx.update({'email_to': user.email,
                            'email_from': self.env.user.email,
                            'department_manager': user.name,
                            })
                self.env['mail.template'].browse(template_id).with_context(
                    ctx).send_mail(self_obj.id, force_send=True)
            self_obj.write(
                {'state': 'waiting_hr_approval', })

        return True

    api.multi
    def action_approve_hr_manager(self):
        """docstring for action_approve_hr_manager"""
        for self_obj in self:
            if not self.env.user.has_group('hr.group_hr_manager'):
                raise exceptions.UserError(_("Only HR Manager can approve this resignation request."))

            ir_model_data = self.env['ir.model.data']
            try:
                template_id = ir_model_data.get_object_reference(
                    'employee_resignation',
                    'email_template_edi_resignation_request_approved')[1]
            except ValueError:
                template_id = False

            ctx = self._context.copy()

            url = self.get_url(self_obj)

            ctx.update({'url': url})

            ctx.update({'email_to': self_obj.employee_id.work_email})
            ctx.update({'email_from': self.env.user.email})

            self.env['mail.template'].browse(template_id).with_context(
                ctx).send_mail(self_obj.id, force_send=True)

            self_obj.write({'state': 'approved', })
            self_obj.employee_id.write(
                {'emp_status': 'in_notice',
                 'cessation_date': self_obj.cessation_date
                 })

        return True

    @api.multi
    def action_reject(self):
        for self_obj in self:
            if not self.env.user.has_group('hr.group_hr_manager'):
                raise exceptions.UserError(_("Only HR Manager can reject this resignation request."))

            ir_model_data = self.env['ir.model.data']
            try:
                template_id = ir_model_data.get_object_reference(
                    'employee_resignation',
                    'email_template_edi_resignation_request_reject')[1]
            except ValueError:
                template_id = False

            ctx = self._context.copy()

            url = self.get_url(self_obj)

            ctx.update({'url': url})

            ctx.update({'email_to': self_obj.employee_id.work_email})
            ctx.update({'email_from': self.env.user.email})

            self.env['mail.template'].browse(template_id).with_context(
                ctx).send_mail(self_obj.id, force_send=True)

            self_obj.write(
                {'state': 'reject', })
        return True



ResignationRequest()
