# -*- coding: utf-8 -*-
from odoo import fields, models, _, api, exceptions
from odoo.exceptions import UserError, ValidationError


class product_product(models.Model):
    _inherit = 'product.product'

    product_doa_id = fields.Many2one('expense.approval.matrix', 'Product DOA')

product_product()


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    next_to_submit = fields.Integer(
        string='Next level to submit',
        default=1,
        help='technical field state that whom to submit.')
    first_time = fields.Boolean(
        "Is First Time to submit?", help="technical field to submit check.",
        default=False, copy=False, )

    def get_url(self, obj):
        url = ''
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        menu_id = self.env['ir.model.data'].get_object_reference(
            'hr_expense', 'menu_hr_expense_my_expenses_to_submit')[1]
        action_id =  self.env['ir.model.data'].get_object_reference(
            'hr_expense', 'hr_expense_actions_my_unsubmitted')[1]

        url = base_url + "/web?db=" + str(self._cr.dbname) + "#id=" + str(
            obj.id) + "&view_type=form&model=hr.expense&menu_id="+str(
                menu_id) + "&action=" + str(action_id)
        return url

    def _search_approval_matrix(self, obj):
        """docstring for _search_approval_matrix"""
        search_ids = self.env['expense.approval.matrix'].search(
            [('department_ids', 'in', [obj.employee_id.department_id.id])],
            limit=1)
        return search_ids

    def _check_whether_in_approver_list(self, obj, line_obj, user_id):
        # retrurn boolean value to check for user exist in list or not
        # return true if exist
        # return False if not exist
        # self.env.user.id
        search_ids = False
        employee_id  = self.env['hr.employee'].search(
            [('user_id', '=', user_id.id)])
        if not employee_id:
            raise exceptions.UserError(_("Please create employee for you."))
        search_ids = self.env['expense.approval.matrix.lines'].search(
            [('id', '=', line_obj.id),
             ('employee_ids', 'in', [employee_id.id])])
        if search_ids:
            return True
        else:
            return False

#   @api.multi
#   def submit_expenses(self):
#       if not self.employee_id.department_id:
#           raise UserError(_("Add Department in %s employee." % (
#               self.employee_id.name)))
#       matrix_ids = self._search_approval_matrix(self)
#       ir_model_data = self.env['ir.model.data']
#       if not matrix_ids:
#           raise UserError(
#               _("Configure expense approval matrix for %s \
#                     department." % (self.employee_id.department_id.name)))
#       if not matrix_ids.approval_line_ids:
#           raise UserError(_("Configure expense approval Lines for %s." % (
#               matrix_ids.product_doa)))

#       try:
#           req_template_id = ir_model_data.get_object_reference(
#               'expense_approval_matrix',
#               'email_template_edi_expense_request')[1]
#       except ValueError:
#           req_template_id = False

#       ctx = self._context.copy()
#       url = self.get_url(self)

#       if not self.first_time:
#           print "lines first time 3333333333333---", matrix_ids.approval_line_ids
#           for line in matrix_ids.approval_line_ids[0]:
#               print "kkkkkkkkkkk"
#               print "---------", line
#               exist = self._check_whether_in_approver_list(self, line, self.env.user)
#               if not exist:
#                   raise UserError(
#                       _("You do not have access to approve/reject the expense request."))
#               for employee in line.employee_ids:
#                   if not employee.user_id:
#                       raise UserError(_("Add user in employee %s." % (employee.name)))
#                   if not employee.work_email:
#                       raise UserError(_('Add Email for %s employee.' % (employee.work_email)))
#                   ctx.update({'approval_name': employee.name,
#                               'emp_name': self.employee_id.name,
#                               'url': url,
#                               'email_to': employee.work_email,
#                               })
#                   self.env['mail.template'].browse(req_template_id).with_context(
#                                           ctx).send_mail(self.id, force_send=True)
#           self.write({'first_time': True})
#       elif len(matrix_ids.approval_line_ids) == self.next_to_submit:
#           print "INSIDE BOT EQUALllllllllll%%%%%%%%%%l"
#           try:
#               approve_template_id = ir_model_data.get_object_reference(
#                   'expense_approval_matrix',
#                   'email_template_edi_expense_request_approved')[1]
#           except ValueError:
#               approve_template_id = False

#           ctx = self._context.copy()
#           url = self.get_url(self)
#           exist = self._check_whether_in_approver_list(
#               self, matrix_ids.approval_line_ids[-1], self.env.env.user)
#           if not exist:
#               raise UserError(
#                   _("You do not have access to approve/reject the expense request."))
#           ctx.update({'email_from': self.env.user.email,
#                       'email_to': self.employee_id.user_id.email,
#                       'url': url,
#                       })
#           self.env['mail.template'].browse(approve_template_id).with_context(
#                                           ctx).send_mail(self.id, force_send=True)
#           if any(expense.state != 'draft' for expense in self):
#               raise UserError(_("You cannot report twice the same line!"))
#           if len(self.mapped('employee_id')) != 1:
#               raise UserError(_("You cannot report expenses for different employees in the same report!"))
#           return {
#               'type': 'ir.actions.act_window',
#               'view_mode': 'form',
#               'res_model': 'hr.expense.sheet',
#               'target': 'current',
#               'context': {
#                   'default_expense_line_ids': [line.id for line in self],
#                   'default_employee_id': self[0].employee_id.id,
#                   'default_name': self[0].name if len(self.ids) == 1 else ''
#               }
#           }
#       else:
#           print "INSIDE THE ELSE1111111111111 CONDITION"
#           for line in matrix_ids.approval_line_ids[self.next_to_submit]:
#               exist = self._check_whether_in_approver_list(self, line, self.env.user)
#               if not exist:
#                   raise UserError(
#                       _("You do not have access to approve/reject the expense request."))
#               for employee in line.employee_ids:
#                   print "LLLLLLLLLLLLLL"
#                   if not employee.user_id:
#                       raise UserError(_("Add user in employee %s." % (employee.name)))
#                   if not employee.work_email:
#                       raise UserError(_('Add Email for %s employee.' % (employee.work_email)))
#                   ctx.update({'approval_name': employee.name,
#                               'emp_name': self.employee_id.name,
#                               'url': url,
#                               'email_to': employee.work_email,
#                               })
#                   self.env['mail.template'].browse(req_template_id).with_context(
#                                           ctx).send_mail(self.id, force_send=True)
#           next_approver = self.next_to_submit
#           next_approver += 1
#           self.write({'next_to_submit': next_approver})


HrExpense()


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    @api.multi
    @api.depends('next_to_submit')
    def _get_next_approver(self):
        for obj in self:
            search_ids = self._search_approval_matrix(obj)
            if search_ids:
                if search_ids.approval_method == 'more_approval':
                    if search_ids.approval_line_ids:
                        obj.next_approval_ids = search_ids.approval_line_ids[obj.next_to_submit].employee_ids
                    else:
                        obj.next_approval_ids = False
                else:
                    expsense_line_sum = 0.0
                    if self.expense_line_ids:
                        expsense_line_sum = sum([line.total_amount for line in obj.expense_line_ids])
                        line_to_approve = self.env['expense.approval.matrix.lines'].search(
                            [('approval_line_id', 'in', search_ids.ids),
                             ('min_amount', '<=', expsense_line_sum),
                             ('max_amount', '>=', expsense_line_sum),
                             ])
                        if line_to_approve:
                            obj.next_approval_ids = line_to_approve.employee_ids
                        else:
                            obj.next_approval_ids = False
                    else:
                        obj.next_approval_ids = False


    next_to_submit = fields.Integer(
        string='Next level to submit',
        default=0,
        help='technical field state that whom to submit.')
    first_time = fields.Boolean(
        "Is First Time to submit?", help="technical field to submit check.",
        default=False, copy=False, )
    next_approval_ids = fields.Many2many(
        'hr.employee', compute="_get_next_approver", string="Next Approver")

    def get_url(self, obj):
        url = ''
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        menu_id = self.env['ir.model.data'].get_object_reference(
            'hr_expense', 'menu_hr_expense_sheet_all_to_approve')[1]
        action_id =  self.env['ir.model.data'].get_object_reference(
            'hr_expense', 'action_hr_expense_sheet_all_to_approve')[1]

        url = base_url + "/web?db=" + str(self._cr.dbname) + "#id=" + str(
            obj.id) + "&view_type=form&model=hr.expense.sheet&menu_id="+str(
                menu_id) + "&action=" + str(action_id)
        return url

    def _search_approval_matrix(self, obj):
        """docstring for _search_approval_matrix"""
        search_ids = self.env['expense.approval.matrix'].search(
            [('department_ids', 'in', [obj.employee_id.department_id.id])],
            limit=1)
        return search_ids

    def _check_whether_in_approver_list(self, obj, line_obj, user_id):
        # retrurn boolean value to check for user exist in list or not
        # return true if exist
        # return False if not exist
        # self.env.user.id
        search_ids = False
        employee_id  = self.env['hr.employee'].search(
            [('user_id', '=', user_id.id)])
        if not employee_id:
            raise exceptions.UserError(_("Please create employee for you."))
        search_ids = self.env['expense.approval.matrix.lines'].search(
            [('id', '=', line_obj.id),
             ('employee_ids', 'in', [employee_id.id])])
        if search_ids:
            return True
        else:
            return False

    def _check_if_employee_is_approver(self, obj):
        # check if employee is in approver list
        # if yes then return true so the we can increment directly one step ahed
        # if no then return False
        result = False
        approver_matrix_ids = self._search_approval_matrix(obj)
        for line in approver_matrix_ids.approval_line_ids[obj.next_to_submit]:
            if obj.employee_id.id in [emp.id for emp in line.employee_ids]:
                result = True
            else:
                result = False
        return result

    @api.multi
    def approve_expense_sheets(self):
        # modify the approve sheet to change super
        matrix_ids = self._search_approval_matrix(self)
        ir_model_data = self.env['ir.model.data']
        if not matrix_ids:
            raise UserError(
                _("Configure expense approval matrix for %s \
                      department." % (self.employee_id.department_id.name)))
        if not matrix_ids.approval_line_ids:
            raise UserError(_("Configure expense approval Lines for %s." % (
                matrix_ids.product_doa)))

        try:
            req_template_id = ir_model_data.get_object_reference(
                'expense_approval_matrix',
                'email_template_edi_expense_request_sheet')[1]
        except ValueError:
            req_template_id = False

        ctx = self._context.copy()
        url = self.get_url(self)
        if matrix_ids.approval_method == 'more_approval':
            # code for the more expense amount submitted
            if len(matrix_ids.approval_line_ids) == (self.next_to_submit+1):
                try:
                    approve_template_id = ir_model_data.get_object_reference(
                        'expense_approval_matrix',
                        'email_template_edi_expense_request_approved_sheet')[1]
                except ValueError:
                    approve_template_id = False

                ctx = self._context.copy()
                url = self.get_url(self)
                exist = self._check_whether_in_approver_list(
                    self, matrix_ids.approval_line_ids[-1], self.env.user)
                if not exist:
                    raise UserError(
                        _("You do not have access to approve/reject the expense request."))
                ctx.update({'email_from': self.env.user.email,
                            'email_to': self.employee_id.user_id.email,
                            'url': url,
                            })
                self.env['mail.template'].browse(approve_template_id).with_context(
                    ctx).send_mail(self.id, force_send=True)
                return super(HrExpenseSheet, self).approve_expense_sheets()
            else:
                for line in matrix_ids.approval_line_ids[self.next_to_submit]:
                    exist = self._check_whether_in_approver_list(self, line, self.env.user)
                    if not exist:
                        raise UserError(
                            _("You do not have access to approve/reject the expense request."))
                for next_line in matrix_ids.approval_line_ids[self.next_to_submit+1]:
                    for employee in next_line.employee_ids:
                        if not employee.user_id:
                            raise UserError(_("Add user in employee %s." % (employee.name)))
                        if not employee.work_email:
                            raise UserError(_('Add Email for %s employee.' % (employee.work_email)))
                        ctx.update({'approval_name': employee.name,
                                    'emp_name': self.employee_id.name,
                                    'url': url,
                                    'email_to': employee.work_email,
                                    'email_from': self.env.user.email,
                                    })
                        self.env['mail.template'].browse(req_template_id).with_context(
                            ctx).send_mail(self.id, force_send=True)
                next_approver = self.next_to_submit
                next_approver += 1
                self.write({'next_to_submit': next_approver})
        else:
            # direct approve
            # when we have to direct compare expense amount with the matrix
            expsense_line_sum = 0.0
            if not self.expense_line_ids:
                raise exceptions.UserError(_("Add expense line first."))
            expsense_line_sum = sum([line.total_amount for line in self.expense_line_ids])
            line_to_approve = self.env['expense.approval.matrix.lines'].search(
                [('approval_line_id', 'in', matrix_ids.ids),
                 ('min_amount', '<=', expsense_line_sum),
                 ('max_amount', '>=', expsense_line_sum),
                 ])
            if not line_to_approve:
                raise exceptions.UserError(
                    _("There is not expense range found. \n Please define range of expense in expense approval matrix."))

            try:
                approve_template_id = ir_model_data.get_object_reference(
                        'expense_approval_matrix',
                        'email_template_edi_expense_request_approved_sheet')[1]
            except ValueError:
                approve_template_id = False

            ctx = self._context.copy()
            url = self.get_url(self)
            exist = self._check_whether_in_approver_list(
                self, line_to_approve, self.env.user)
            if not exist:
                raise UserError(
                    _("You do not have access to approve/reject the expense request."))
            ctx.update({'email_from': self.env.user.email,
                        'email_to': self.employee_id.user_id.email,
                        'url': url,
                        })
            self.env['mail.template'].browse(approve_template_id).with_context(
                ctx).send_mail(self.id, force_send=True)
            return super(HrExpenseSheet, self).approve_expense_sheets()


    @api.model
    def create(self, vals):
        res = super(HrExpenseSheet, self).create(vals)
        if not res.employee_id.department_id:
            raise UserError(_("Add Department in %s employee." % (
                res.employee_id.name)))
        matrix_ids = self._search_approval_matrix(res)
        ir_model_data = self.env['ir.model.data']
        if not matrix_ids:
            raise UserError(
                _("Configure expense approval matrix for %s \
                      department." % (res.employee_id.department_id.name)))
        if not matrix_ids.approval_line_ids:
            raise UserError(_("Configure expense approval Lines for %s." % (
                matrix_ids.product_doa)))

        try:
            req_template_id = ir_model_data.get_object_reference(
                'expense_approval_matrix',
                'email_template_edi_expense_request_sheet')[1]
        except ValueError:
            req_template_id = False

        ctx = self._context.copy()
        url = self.get_url(res)
        employee_is_approver = self._check_if_employee_is_approver(res)
        if matrix_ids.approval_method == 'more_approval':
            if not employee_is_approver:
                for line in matrix_ids.approval_line_ids[0]:
                    # in create we do not check for the user approve
                    # exist = self._check_whether_in_approver_list(res, line, self.env.user)
                    # if not exist:
                    #    raise UserError(
                    #        _("You do not have access to approve/reject the expense request."))
                    for employee in line.employee_ids:
                        if not employee.user_id:
                            raise UserError(_("Add user in employee %s." % (employee.name)))
                        if not employee.work_email:
                            raise UserError(_('Add Email for %s employee.' % (employee.work_email)))
                        ctx.update({'approval_name': employee.name,
                                    'emp_name': res.employee_id.name,
                                    'url': url,
                                    'email_to': employee.work_email,
                                    'email_from': res.employee_id.work_email,
                                    })
                        self.env['mail.template'].browse(req_template_id).with_context(
                            ctx).send_mail(res.id, force_send=True)
            else:
                for line in matrix_ids.approval_line_ids[1]:
                    # in create we do not check for the user approve
                    # exist = self._check_whether_in_approver_list(res, line, self.env.user)
                    # if not exist:
                    #    raise UserError(
                    #        _("You do not have access to approve/reject the expense request."))
                    for employee in line.employee_ids:
                        if not employee.user_id:
                            raise UserError(_("Add user in employee %s." % (employee.name)))
                        if not employee.work_email:
                            raise UserError(_('Add Email for %s employee.' % (employee.work_email)))
                        ctx.update({'approval_name': employee.name,
                                    'emp_name': res.employee_id.name,
                                    'url': url,
                                    'email_to': employee.work_email,
                                    'email_from': res.employee_id.work_email,
                                    })
                        self.env['mail.template'].browse(req_template_id).with_context(
                            ctx).send_mail(res.id, force_send=True)
                #next_approver = res.next_to_submit
                #next_approver += 1
                #res.write({'next_to_submit': next_approver})
                query = """update hr_expense_sheet set next_to_submit =1 where id=%s"""
                self._cr.execute(query, (res.id,))
        else:
            expsense_line_sum = 0.0
            if not res.expense_line_ids:
                raise exceptions.UserError(_("Add expense line first."))
            expsense_line_sum = sum([line.total_amount for line in res.expense_line_ids])
            line_to_approve = self.env['expense.approval.matrix.lines'].search(
                [('approval_line_id', 'in', matrix_ids.ids),
                 ('min_amount', '<=', expsense_line_sum),
                 ('max_amount', '>=', expsense_line_sum),
                 ])
            if not line_to_approve:
                raise exceptions.UserError(
                    _("There is not expense range found. \n Please define range of expense in expense approval matrix."))

            # here we can not check whether employee is approver or not
            # because we have to directly map with the range of expense
            for employee in line_to_approve.employee_ids:
                if not employee.user_id:
                    raise UserError(
                        _("Add user in employee %s." % (employee.name)))
                if not employee.work_email:
                    raise UserError(
                        _('Add Email for %s employee.' % (employee.work_email)))
                ctx.update({'approval_name': employee.name,
                            'emp_name': res.employee_id.name,
                            'url': url,
                            'email_to': employee.work_email,
                            'email_from': res.employee_id.work_email,
                            })
                self.env['mail.template'].browse(req_template_id).with_context(
                    ctx).send_mail(res.id, force_send=True)
        return res

    @api.multi
    def refuse_expenses(self, reason):
        super(HrExpenseSheet, self).refuse_expenses(reason)
        matrix_ids = self._search_approval_matrix(self)
        ir_model_data = self.env['ir.model.data']

        try:
            req_template_id = ir_model_data.get_object_reference(
                'expense_approval_matrix',
                'email_template_edi_expense_request_reject_sheet')[1]
        except ValueError:
            req_template_id = False

        ctx = self._context.copy()
        for line in matrix_ids.approval_line_ids[self.next_to_submit]:
            exist = self._check_whether_in_approver_list(self, line, self.env.user)
            if not exist:
                raise UserError(
                    _("You do not have access to approve/reject the expense request."))
        ctx.update({
            #'approval_name': employee.name,
            'emp_name': self.employee_id.name,
            #'url': url,
            'email_to': self.employee_id.work_email,
            'email_from': self.env.user.email,
            'reason': reason,
        })
        self.env['mail.template'].browse(req_template_id).with_context(
            ctx).send_mail(self.id, force_send=True)




HrExpenseSheet()

