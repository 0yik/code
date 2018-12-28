# -*- coding: utf-8 -*-


from openerp import api, exceptions, fields, models, _
from odoo.exceptions import UserError, AccessError, ValidationError


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    @api.multi
    @api.depends('level_to_send')
    def _get_next_approver(self):
        for obj in self:
            search_ids = self._get_approval_objs(obj)
            if search_ids:
                if search_ids.approval_line_ids:
                    obj.next_approval_ids = search_ids.approval_line_ids[obj.level_to_send-1].employee_ids
            else:
                obj.next_approval_ids = False

    # below field have default 1 value to access directly approval level
    level_to_send = fields.Integer(
        string='identify which level',
        help='Technical field to identify to which\
        level we have to use.', default=1, )
    next_approval_ids = fields.Many2many(
        'hr.employee', compute="_get_next_approver", string="Next Approver")

    def get_url(self, obj):
        url = ''
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        menu_id = self.env['ir.model.data'].get_object_reference(
            'hr_holidays', 'menu_open_ask_holidays_new')[1]
        action_id =  self.env['ir.model.data'].get_object_reference(
            'hr_holidays', 'open_ask_holidays')[1]
        url = base_url + "/web?db=" + str(self._cr.dbname) +"#id=" + str(
            obj.id) + "&view_type=form&model=hr.holidays&menu_id="+str(
                menu_id)+"&action=" + str(action_id)
        return url

    def _get_approval_objs(self, obj):
        search_ids = self.env['leave.approval'].search(
            [('department_ids', 'in', [obj.department_id.id]),
             ('leave_type_ids', 'in', [obj.holiday_status_id.id])
             ], limit=1)
        return search_ids

    @api.model
    def create(self, values):
        res = super(HrHolidays, self).create(values)
        if not res.department_id:
            raise exceptions.UserError(_('Please add department for %s Employee.' %(res.employee_id.name)))
        approval_ids = self._get_approval_objs(res)
        if values['type'] != 'add':
            if not approval_ids:
                raise exceptions.UserError(
                    _("Please ensure the employee \'s department and leave type \
                      have been specified in the leave approval configuration."))
            ir_model_data = self.env['ir.model.data']
            try:
                template_id = ir_model_data.get_object_reference(
                    'leave_multi_approval_levels',
                    'email_template_edi_leave_request')[1]
            except ValueError:
                template_id = False
            ctx = self._context.copy()
            url = self.get_url(res)
            if not approval_ids.approval_line_ids:
                raise exceptions.UserError(_("Add Approver for %s Leave Approval." %(approval_ids.name)))
            ## first we check if employee is in approval level
            level_to_send = res.level_to_send
            for line in approval_ids.approval_line_ids[0]:
                for employee in line.employee_ids:
                    if not employee.work_email:
                        raise exceptions.UserError(_("Add Email for %s employee." %(employee.name)))
                    ctx.update({'email_to': employee.work_email,
                                'url': url,
                                'approval_name': employee.name,
                                'emp_name': res.employee_id.name,
                                'holiday_status_name': res.holiday_status_id.name2,
                                'date_from': res.date_from and fields.Datetime.from_string(res.date_from).strftime('%d/%m/%Y') or '',
                                'date_to': res.date_to and fields.Datetime.from_string(res.date_to).strftime('%d/%m/%Y') or '',
                                })
                    self.env['mail.template'].browse(template_id).with_context(
                        ctx).send_mail(res.id, force_send=True)

        return res

    @api.multi
    def action_approve(self):
        # Overriding method for multilevel update

        # if double_validation: this method is the first approval approval
        # if not double_validation: this method calls action_validate() below
        if not self.env.user.has_group('hr_holidays.group_hr_holidays_user'):
            raise UserError(_('Only an HR Officer or Manager can approve leave requests.'))

        manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

        for holiday in self:
            if holiday.type == 'add':
                if holiday.state != 'confirm':
                    raise UserError(_('Leave request must be confirmed ("To Approve") in order to approve it.'))

                if holiday.double_validation:
                    return holiday.write({'state': 'validate1', 'manager_id': manager.id if manager else False})
                else:
                    holiday.action_validate()
            else:
                approval_ids = self._get_approval_objs(holiday)
                if not approval_ids:
                    raise exceptions.UserError(
                        _("Please ensure the employee \'s department and leave type \
                          have been specified in the leave approval configuration."))
                ir_model_data = self.env['ir.model.data']

                ctx = self._context.copy()
                url = self.get_url(holiday)
                if not approval_ids.approval_line_ids:
                    raise exceptions.UserError(_("Add Approver for %s Leave Approval." %(approval_ids.name)))

                # Send Approved mail if len of length approval line equal
                if holiday.level_to_send == len(approval_ids.approval_line_ids):
                    employee_id  = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
                    if not employee_id:
                        raise exceptions.UserError(_("Please create employee for you"))
                    exist = self._check_whether_in_approval_list(holiday, approval_ids, employee_id)

                    if not exist:
                        raise exceptions.UserError(_("You do not have access to approve/reject the leave request."))
                    try:
                        template_id = ir_model_data.get_object_reference(
                            'leave_multi_approval_levels',
                            'email_template_edi_leave_request_approved')[1]
                    except ValueError:
                        template_id = False

                    if holiday.state != 'confirm':
                        raise UserError(_('Leave request must be confirmed ("To Approve") in order to approve it.'))

                    if holiday.double_validation:
                        return holiday.write({'state': 'validate1', 'manager_id': manager.id if manager else False})
                    else:
                        holiday.action_validate()
                        ctx.update({'email_from': self.env.user.email,
                            'url': url,
                            'approval_name': holiday.employee_id.name,
                            'emp_name': holiday.employee_id.name,
                            'holiday_status_name': holiday.holiday_status_id.name2,
                            'date_from': fields.Datetime.from_string(holiday.date_from).strftime('%d/%m/%Y'),
                            'date_to': fields.Datetime.from_string(holiday.date_to).strftime('%d/%m/%Y'),
                            })
                        self.env['mail.template'].browse(template_id).with_context(
                            ctx).send_mail(holiday.id, force_send=True)

                # only send the next level mail approval
                else:
                    if holiday.state != 'confirm':
                        raise UserError(_('Leave request must be confirmed ("To Approve") in order to approve it.'))

                    if holiday.double_validation:
                        approval_ids = self._get_approval_objs(holiday)
                        if not approval_ids:
                            raise exceptions.UserError(
                                _("Please ensure the employee \'s department and leave type \
                                  have been specified in the leave approval configuration."))
                        ir_model_data = self.env['ir.model.data']
                        try:
                            template_id = ir_model_data.get_object_reference(
                                'leave_multi_approval_levels',
                                'email_template_edi_leave_request')[1]
                        except ValueError:
                            template_id = False

                        ctx = self._context.copy()
                        url = self.get_url(holiday)

                        if not approval_ids.approval_line_ids:
                            raise exceptions.UserError(_("Add Approver for %s Leave Approval." %(approval_ids.name)))

                        employee_id  = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
                        if not employee_id:
                            raise exceptions.UserError(_("Please create employee for you"))
                        exist = self._check_whether_in_approval_list(holiday, approval_ids, employee_id)
                        if not exist:
                            raise exceptions.UserError(_("You do not have access to approve/reject the leave request."))
                        level_to_send = holiday.level_to_send
                        for line in approval_ids.approval_line_ids[level_to_send]:
                            for employee in line.employee_ids:
                                if not employee.work_email:
                                    raise exceptions.UserError(_("Add Email for %s employee." %(employee.name)))
                                ctx.update({'email_to': employee.work_email,
                                            'url': url,
                                            'approval_name': employee.name,
                                            'emp_name': holiday.employee_id.name,
                                            'holiday_status_name': holiday.holiday_status_id.name2,
                                            'date_from': holiday.date_from and fields.Datetime.from_string(holiday.date_from).strftime('%d/%m/%Y') or '',
                                            'date_to': holiday.date_to and fields.Datetime.from_string(holiday.date_to).strftime('%d/%m/%Y') or '',
                                            })
                                self.env['mail.template'].browse(template_id).with_context(
                                    ctx).send_mail(holiday.id, force_send=True)
                        # incrementing level to send value
                        level_to_send +=1
                        return holiday.write({'state': 'validate1', 'manager_id': manager.id if manager else False, 'level_to_send': level_to_send})
                    # Sending next level approval without change state
                    else:
                        approval_ids = self._get_approval_objs(holiday)
                        if not approval_ids:
                            raise exceptions.UserError(
                                _("Please ensure the employee \'s department and leave type \
                                  have been specified in the leave approval configuration."))
                        ir_model_data = self.env['ir.model.data']
                        try:
                            template_id = ir_model_data.get_object_reference(
                                'leave_multi_approval_levels',
                                'email_template_edi_leave_request')[1]
                        except ValueError:
                            template_id = False

                        ctx = self._context.copy()
                        url = self.get_url(holiday)

                        if not approval_ids.approval_line_ids:
                            raise exceptions.UserError(_("Add Approver for %s Leave Approval." %(approval_ids.name)))

                        employee_id  = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
                        if not employee_id:
                            raise exceptions.UserError(_("Please create employee for you"))
                        exist = self._check_whether_in_approval_list(holiday, approval_ids, employee_id)

                        if not exist:
                            raise exceptions.UserError(_("You do not have access to approve/reject the leave request."))

                        level_to_send = holiday.level_to_send
                        for line in approval_ids.approval_line_ids[level_to_send]:
                            for employee in line.employee_ids:
                                if not employee.work_email:
                                    raise exceptions.UserError(_("Add Email for %s employee." %(employee.name)))
                                ctx.update({'email_to': employee.work_email,
                                            'url': url,
                                            'approval_name': employee.name,
                                            'emp_name': holiday.employee_id.name,
                                            'holiday_status_name': holiday.holiday_status_id.name2,
                                            'date_from': holiday.date_from and fields.Datetime.from_string(holiday.date_from).strftime('%d/%m/%Y') or '',
                                            'date_to': holiday.date_to and fields.Datetime.from_string(holiday.date_to).strftime('%d/%m/%Y') or '',
                                            })
                                self.env['mail.template'].browse(template_id).with_context(
                                    ctx).send_mail(holiday.id, force_send=True)
                        # incrementing level to send value
                        level_to_send +=1
                        return holiday.write({'level_to_send': level_to_send})

    def _check_whether_in_approval_list(self, obj, approval_obj, employee_id):
        # retrurn boolean value to check for user exist in list or not
        # return true if exist
        # return False if not exist
        search_ids = False
        search_ids = self.env['leave.approval.line'].search([
            ('leave_approval_id', '=', approval_obj.id),
            ('employee_ids', 'in', [employee_id.id]),
        ])
        if search_ids:
            return True
        else:
            return False

    '''

    @api.multi
    def action_draft(self):
        for holiday in self:
            if not holiday.can_reset:
                raise UserError(_('Only an HR Manager or the concerned employee can reset to draft.'))
            if holiday.state not in ['confirm', 'refuse']:
                raise UserError(_('Leave request state must be "Refused" or "To Approve" in order to reset to Draft.'))

            approval_ids = self._get_approval_objs(holiday)

            if not approval_ids:
                raise exceptions.UserError(
                    _("Please ensure the employee \'s department and leave type \
                      have been specified in the leave approval configuration."))

            if not approval_ids.approval_line_ids:
                raise exceptions.UserError(_("Add Approver for %s Leave Approval." %(approval_ids.name)))

            employee_id  = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
            if not employee_id:
                raise exceptions.UserError(_("Please create employee for you" %(approval_ids.name)))
            exist = self._check_whether_in_approval_list(holiday, approval_ids, employee_id)

            if not exist:
                raise exceptions.UserError(_("You do not have access to approve/reject the leave request."))

            holiday.write({
                'state': 'draft',
                'manager_id': False,
                'manager_id2': False,
            })

            linked_requests = holiday.mapped('linked_request_ids')
            for linked_request in linked_requests:
                linked_request.action_draft()
            linked_requests.unlink()

            ctx = self._context.copy()
            url = self.get_url(holiday)

            if not holiday.employee_id.work_email:
                raise exceptions.UserError(_("Add Email for %s employee." %(holiday.employee_id.name)))
            if not self.env.user.email:
                raise exceptions.UserError(_("Add Email address in %s User." %(self.env.user.name)))

            ctx.update({'email_from': self.env.user.email,
                        'url': url,
                        'approval_name': holiday.employee_id.name,
                        'emp_name': holiday.employee_id.name,
                        'holiday_status_name': holiday.holiday_status_id.name2,
                        'date_from': fields.Datetime.from_string(holiday.date_from).strftime('%d/%m/%Y'),
                        'date_to': fields.Datetime.from_string(holiday.date_to).strftime('%d/%m/%Y'),
                        })
            self.env['mail.template'].browse(template_id).with_context(
                ctx).send_mail(holiday.id, force_send=True)

        return True
    '''

    @api.multi
    def action_refuse(self):
        if not self.env.user.has_group('hr_holidays.group_hr_holidays_user'):
            raise UserError(_('Only an HR Officer or Manager can refuse leave requests.'))

        manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for holiday in self:
            if holiday.state not in ['confirm', 'validate', 'validate1']:
                raise UserError(_('Leave request must be confirmed or validated in order to refuse it.'))

            if holiday.state == 'validate1':
                holiday.write({'state': 'refuse', 'manager_id': manager.id})
            else:
                holiday.write({'state': 'refuse', 'manager_id2': manager.id})
            # Delete the meeting
            if holiday.meeting_id:
                holiday.meeting_id.unlink()
            # If a category that created several holidays, cancel all related
            holiday.linked_request_ids.action_refuse()

            approval_ids = self._get_approval_objs(holiday)

            if not approval_ids:
                raise exceptions.UserError(
                    _("Please ensure the employee \'s department and leave type \
                      have been specified in the leave approval configuration."))

            if not approval_ids.approval_line_ids:
                raise exceptions.UserError(_("Add Approver for %s Leave Approval." %(approval_ids.name)))

            employee_id  = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
            if not employee_id:
                raise exceptions.UserError(_("Please create employee for you"))
            exist = self._check_whether_in_approval_list(holiday, approval_ids, employee_id)

            if not exist:
                raise exceptions.UserError(_("You do not have access to approve/reject the leave request."))

            ctx = self._context.copy()
            url = self.get_url(holiday)

            if not holiday.employee_id.work_email:
                raise exceptions.UserError(_("Add Email for %s employee." %(holiday.employee_id.name)))

            if not self.env.user.email:
                raise exceptions.UserError(_("Add Email address in %s User." %(self.env.user.name)))

            ir_model_data = self.env['ir.model.data']
            try:
                template_id = ir_model_data.get_object_reference(
                    'leave_multi_approval_levels',
                    'email_template_edi_leave_request_reject')[1]
            except ValueError:
                template_id = False

            ctx.update({'email_from': self.env.user.email,
                        'url': url,
                        'approval_name': holiday.employee_id.name,
                        'emp_name': holiday.employee_id.name,
                        'holiday_status_name': holiday.holiday_status_id.name2,
                        'date_from': fields.Datetime.from_string(holiday.date_from).strftime('%d/%m/%Y'),
                        'date_to': fields.Datetime.from_string(holiday.date_to).strftime('%d/%m/%Y'),
                        })
            self.env['mail.template'].browse(template_id).with_context(
                ctx).send_mail(holiday.id, force_send=True)

        self._remove_resource_leave()
        return True

HrHolidays()
